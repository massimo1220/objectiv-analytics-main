"""
Copyright 2022 Objectiv B.V.
"""
import re
from dataclasses import dataclass
from typing import Optional

import nbformat
from nbclient.exceptions import CellExecutionError
from papermill.clientwrap import PapermillNotebookClient
from papermill.engines import NBClientEngine, NotebookExecutionManager
from papermill.iorw import load_notebook_node

from checklock_holmes.models.nb_checker_models import (
    CellError, CellTiming, NoteBookCheck, NoteBookMetadata
)
from checklock_holmes.settings import settings
from checklock_holmes.utils.cell_tags import CellTags
from checklock_holmes.utils.constants import (
    NB_SCRIPT_TO_STORE_TEMPLATE, SET_ENV_VARIABLE_TEMPLATE, DATE_FORMAT
)
from checklock_holmes.utils.helpers import CuriousIncident
from checklock_holmes.utils.supported_engines import SupportedEngine


class WatsonExecutionManager(NotebookExecutionManager):
    MAX_LOG_EXCEPTION_MESSAGE = 500

    def cell_exception(
        self, cell: nbformat.NotebookNode, cell_index: str = None, **kwargs,
    ) -> None:
        super().cell_exception(cell, cell_index, **kwargs)

        exc = kwargs['exception']

        if self.nb.metadata.papermill.error is None:
            self.nb.metadata.papermill.error = CellError(
                number=cell.metadata.papermill.index,
                exc=f'{exc.ename}: {exc.evalue[:self.MAX_LOG_EXCEPTION_MESSAGE]}',
            )

    def notebook_start(self, **kwargs) -> None:
        super().notebook_start(**kwargs)
        for cell_idx, cell in enumerate(self.nb.cells):
            cell.metadata.papermill.index = cell_idx


class ChecklockNBClient(PapermillNotebookClient):
    async def async_execute_cell(
        self,
        cell: nbformat.NotebookNode,
        cell_index: int,
        execution_count: Optional[int] = None,
        store_history: bool = True,
    ) -> nbformat.NotebookNode:
        try:
            self.nb_man.cell_start(cell, cell_index)
            await super().async_execute_cell(
                cell=cell,
                cell_index=cell_index,
                execution_count=execution_count,
                store_history=store_history,
            )
        except CellExecutionError as ex:
            self.nb_man.cell_exception(cell, cell_index=cell_index, exception=ex)
        finally:
            self.nb_man.cell_complete(cell, cell_index=cell_index)

        return cell


class ChecklockNBEngine(NBClientEngine):
    EXECUTION_TIMEOUT = 2 * 60  # 2 minutes

    @classmethod
    async def async_execute_notebook(cls, nb: nbformat.NotebookNode) -> nbformat.NotebookNode:
        """
        A wrapper to handle notebook execution tasks.

        Wraps the notebook object in a `NotebookExecutionManager` in order to track
        execution state in a uniform manner. This is meant to help simplify
        engine implementations. This allows a developer to just focus on
        iterating and executing the cell contents.
        """
        nb_man = WatsonExecutionManager(
            nb,
            output_path=None,  # don't save notebook outputs
            progress_bar=False,  # ignore for now
            autosave_cell_every=0,  # don't perform any autosave
        )

        nb_man.notebook_start()
        try:
            await cls.async_execute_managed_notebook(nb_man)
        finally:
            nb_man.cleanup_pbar()
            nb_man.notebook_complete()

        return nb_man.nb

    @classmethod
    async def async_execute_managed_notebook(cls, nb_man: WatsonExecutionManager) -> nbformat.NotebookNode:
        nb_client = ChecklockNBClient(
            nb_man=nb_man,
            timeout=cls.EXECUTION_TIMEOUT,
            interrupt_on_timeout=True,
            allow_errors=True,
            force_raise_errors=True,
        )
        return await nb_client.async_execute()


@dataclass
class NoteBookChecker:
    metadata: NoteBookMetadata

    _DEFAULT_ENV_VARIABLES = {
        'OBJECTIV_VERSION_CHECK_DISABLE': 'true'
    }
    _ENV_VAR_CELL_TAG = 'injected-engine-variables'

    async def async_check_notebook(self, engine: SupportedEngine) -> NoteBookCheck:
        """
        Creates and executes the notebook's script for the provided engine.

        Returns a generated report based on the execution.
        """
        # skip checks for engines without env variables
        if engine not in settings.engine_env_var_mapping:
            return NoteBookCheck(
                metadata=self.metadata,
                engine=engine,
                skipped=True,
            )

        try:
            executed_nb = await ChecklockNBEngine.async_execute_notebook(
                nb=self._load_notebook_node(engine),
            )
        except Exception as exc:
            raise CuriousIncident(notebook_name=self.metadata.name, exc=exc)

        failing_block = ''
        cell_timings = []
        for idx, cell in enumerate(executed_nb.cells):
            # ignore env setup and markdown cells
            if self._ENV_VAR_CELL_TAG in cell.metadata.tags or cell.cell_type != 'code':
                continue

            cell_exec_data = cell.metadata.papermill
            if cell_exec_data.exception is True:
                failing_block = cell.source
                break

            cell_timings.append(
                CellTiming(number=idx, time=cell_exec_data.duration)
            )

        notebook_exec_data = executed_nb.metadata.papermill
        return NoteBookCheck(
            metadata=self.metadata,
            engine=engine,
            completed=notebook_exec_data.exception is None,
            error=notebook_exec_data.error,
            failing_block=failing_block,
            elapsed_time=notebook_exec_data.duration,
            elapsed_time_per_cell=cell_timings,
        )

    def get_script(self, engine: SupportedEngine) -> str:
        """
        Extracts all code cells from the notebook and generates a script based on it.
        If is_execution is True, then code cells will be wrapped for error logging
        and (if required) timing loging. Otherwise, cells will be added as found in the notebook.

        When executing, we ignore cells containing only comments as this will generate errors when
        executing the script.
        """
        formatted_blocks = []
        nb_node = self._load_notebook_node(engine)
        for cell_index, cell in enumerate(nb_node.cells):
            if cell.cell_type != 'code':
                continue

            formatted_block = f'\n# CELL {cell_index}\n{cell.source}'
            formatted_blocks.append(formatted_block.replace('\n', '\n    '))

        nb_script = '\n'.join(formatted_blocks)
        if self.metadata.name:
            # creates script for debugging
            # the template defines a function for the entire notebook
            # and adds a call to it in if __name__ == '__main__'
            nb_script = NB_SCRIPT_TO_STORE_TEMPLATE.format(
                notebook=re.sub(r'(-|\s)+', '_', self.metadata.name),
                script=nb_script.strip(),
            )

        return nb_script

    def _get_env_setup_block(self, engine: SupportedEngine) -> str:
        """
        Returns the code block for setting env variables based on the engine to use.
        """
        env_variables = settings.get_env_variables(engine)
        env_variables.update(self._DEFAULT_ENV_VARIABLES)
        env_variables_stmt = '\n'.join(
            [
                SET_ENV_VARIABLE_TEMPLATE.format(
                    env_var_name=env_var, env_var_value=val,
                )
                for env_var, val in env_variables.items()
            ]
        )
        return f'# env variables setup\nimport os\n{env_variables_stmt}'

    def _load_notebook_node(
        self,
        engine: SupportedEngine,
    ) -> nbformat.NotebookNode:
        nb_node = load_notebook_node(notebook_path=self.metadata.path)
        nb_node.metadata['papermill']['error'] = None

        env_cell = nbformat.v4.new_code_cell(source=self._get_env_setup_block(engine))
        env_cell.metadata['checklock_tags'] = [CellTags.INJECTED_ENGINE_VARIABLES]
        env_cell.metadata['tags'] = [CellTags.INJECTED_ENGINE_VARIABLES.value]

        env_cell.metadata['papermill'] = {}
        nb_node.cells = [env_cell] + nb_node.cells
        return self._tag_notebook_cells(nb_node)

    def _tag_notebook_cells(self, nb_node: nbformat.NotebookNode) -> nbformat.NotebookNode:
        _GET_OBJECTIV_DF_REGEX = re.compile(r'get_objectiv_dataframe\((?P<params>.*)\)', re.MULTILINE)

        default_obj_params = []

        if self.metadata.start_date:
            default_obj_params.append(f'start_date="{self.metadata.start_date.strftime(DATE_FORMAT)}"')

        if self.metadata.end_date:
            default_obj_params.append(f'end_date="{self.metadata.end_date.strftime(DATE_FORMAT)}"')

        for cell in nb_node.cells:
            if cell.metadata.get('checklock_tags') or cell.cell_type != 'code':
                continue

            tags = CellTags.get_tags(cell.source)

            cell.metadata['checklock_tags'] = tags
            cell.metadata['tags'].extend([tag.value for tag in tags])

            if (
                CellTags.GET_OBJECTIV_DATAFRAME in tags
                and (self.metadata.start_date or self.metadata.end_date)
            ):
                match = _GET_OBJECTIV_DF_REGEX.search(cell.source)
                params = match.group('params').split(',') if match else []

                new_params = default_obj_params.copy()
                for param in params:

                    if 'start_date' in param and self.metadata.start_date:
                        continue

                    if 'end_date' in param and self.metadata.end_date:
                        continue

                    new_params.append(param.strip())

                cell.source = _GET_OBJECTIV_DF_REGEX.sub(
                    f'get_objectiv_dataframe({", ".join(new_params)})', cell.source
                )

        return nb_node
