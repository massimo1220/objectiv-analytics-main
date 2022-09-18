"""
CHECKLOCK HOLMES CLI
Usage:
    checklock-holmes.py [-x | --exitfirst] [-e | --engine=<engine>...] [--nb=<file>...] [--gh_issues_dir=<ghi>] [--dump_nb_scripts_dir=<nbs_dir>] [-t | --timeit] [--start_date=<start_date>] [--end_date=<end_date>]
    checklock-holmes.py -h | --help

Options:
    -h --help                       Show this screen.
    -x --exitfirst                  Stop checks after first fail.
    -e --engine=<engine>...         Engines to run checks. Current supported engines: [{supported_engines}] [default: all].
    --nb=<file>...                  Notebooks to be checked [default: {default_nb_dir}].
    --gh_issues_dir=<ghi>           Directory for logging github issues [default: {default_github_issues_dir}].
    --dump_nb_scripts_dir<nbs_dir>  Directory where to dump notebook scripts.
    -t --timeit                     Time each cell
    --start_date=<start_date>       First date for which objectiv data is loaded for Modelhub. Format as 'YYYY-MM-DD'.
    --end_date=<end_date>           Last date for which objectiv data is loaded for Modelhub. Format as 'YYYY-MM-DD'.

Before running checks, please define .env file. Must include the following variables per engine:

- Postgres
PG_DB__DSN

- BigQuery
BQ_DB__DSN
BQ_DB__CREDENTIALS_PATH

Copyright 2022 Objectiv B.V.
"""
import datetime

import asyncio
import itertools
from typing import List

from docopt import docopt
from tqdm.asyncio import tqdm_asyncio

from checklock_holmes.models.nb_checker_models import (
    NoteBookCheck, NoteBookCheckSettings, NoteBookMetadata
)
from checklock_holmes.nb_checker import NoteBookChecker
from checklock_holmes.settings import settings
from checklock_holmes.utils.constants import (
    DEFAULT_GITHUB_ISSUES_DIR, DEFAULT_NOTEBOOKS_DIR, DATE_FORMAT
)
from checklock_holmes.utils.helpers import (
    display_check_results, get_github_issue_filename, store_github_issue,
    store_nb_script
)
from checklock_holmes.utils.supported_engines import SupportedEngine


async def _check_notebook_per_engine(
    nb_path: str,
    check_settings: NoteBookCheckSettings,
    github_issues_file_path: str,
) -> List[NoteBookCheck]:
    nb_metadata = NoteBookMetadata(
        path=nb_path, start_date=check_settings.start_date, end_date=check_settings.end_date,
    )
    nb_checker = NoteBookChecker(metadata=nb_metadata)

    tasks = []
    for engine in check_settings.engines_to_check:
        # store script before check, this way we don't wait till the check is finished
        if check_settings.dump_nb_scripts_dir:
            script_path = f'{check_settings.dump_nb_scripts_dir}/{nb_checker.metadata.name}_{engine}.py'
            store_nb_script(script_path, nb_checker.get_script(engine))

        tasks.append(nb_checker.async_check_notebook(engine))

    pb = tqdm_asyncio()
    pb.set_description(f'Checking {nb_metadata.name}...')
    nb_checks = await pb.gather(*tasks)
    for nb_check in nb_checks:
        if nb_check.error:
            store_github_issue(nb_check, github_issues_file_path)
    return nb_checks


async def async_check_notebooks(check_settings: NoteBookCheckSettings, exit_on_fail: bool) -> None:
    if not settings.engine_env_var_mapping:
        print(
            'Cannot run checks, nothing to be done if you do not define '
            'any environmental variable for any engine. Goodbye!'
        )
        return

    github_issues_file_path = f'{check_settings.github_issues_dir}/{get_github_issue_filename()}'

    all_checks = await asyncio.gather(
        *[
            _check_notebook_per_engine(
                nb_path,
                check_settings=check_settings,
                github_issues_file_path=github_issues_file_path,
            )
            for nb_path in check_settings.notebooks_to_check
        ]
    )
    all_checks = list(itertools.chain.from_iterable(all_checks))

    # display final check report
    display_check_results(
        nb_checks=all_checks,
        github_files_path=github_issues_file_path,
        display_cell_timings=check_settings.display_cell_timing,
    )


if __name__ == '__main__':
    cli_docstring = __doc__.format(
        supported_engines=', '.join([engine for engine in SupportedEngine]),
        default_nb_dir=DEFAULT_NOTEBOOKS_DIR,
        default_github_issues_dir=DEFAULT_GITHUB_ISSUES_DIR,
    )
    arguments = docopt(cli_docstring, help=True, options_first=False)
    start_date = None
    if arguments['--start_date']:
        start_date = datetime.datetime.strptime(arguments['--start_date'], DATE_FORMAT)

    end_date = None
    if arguments['--end_date']:
        end_date = datetime.datetime.strptime(arguments['--end_date'], DATE_FORMAT)
    nb_check_settings = NoteBookCheckSettings(
        engines_to_check=arguments['--engine'],
        github_issues_dir=arguments['--gh_issues_dir'],
        dump_nb_scripts_dir=arguments['--dump_nb_scripts_dir'],
        notebooks_to_check=arguments['--nb'],
        display_cell_timing=arguments['--timeit'],
        start_date=start_date,
        end_date=end_date,
    )
    asyncio.run(
        async_check_notebooks(nb_check_settings, exit_on_fail=arguments['--exitfirst'])
    )
