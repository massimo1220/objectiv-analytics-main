"""
Copyright 2021 Objectiv B.V.
"""
import operator
import re
from abc import abstractmethod, ABC
from functools import reduce

import bach
from typing import Optional, Dict, List

from sql_models.util import is_postgres, is_bigquery

import modelhub
from bach.types import StructuredDtype
from sqlalchemy.engine import Engine

from modelhub.util import (
    ObjectivSupportedColumns, get_supported_dtypes_per_objectiv_column, check_objectiv_dataframe
)
from modelhub.pipelines.base_pipeline import BaseDataPipeline


class BaseExtractedContextsPipeline(BaseDataPipeline):
    """
    Base pipeline in charge of extracting Objectiv context columns from event data source.
    Based on the provided engine, it will perform the proper transformations for generating a bach DataFrame
    that contains all expected series to be used by Modelhub.

    The steps followed in this pipeline are the following:
        1. _get_initial_data: Gets the initial bach DataFrame containing all required context columns
            based on the engine.
        2. _process_data: Extracts required context series from initial format. Each child must implement this
            method, as data format might be different per engine.
        3. _extract_requested_global_contexts: Creates a series per requested global context. Extraction
           depends if child supports snowplow flat format or GLOBAL_CONTEXT series.
        4. _convert_dtypes: Will convert all required context series to their correct dtype
        5. _apply_filters: Applies start_date and end_date filter and event deduplication, if required.

    Final bach DataFrame will be later validated, it must include:
        - all context series defined in ObjectivSupportedColumns
        - correct dtypes for context series
    """
    DATE_FILTER_COLUMN = ObjectivSupportedColumns.DAY.value

    BASE_REQUIRED_DB_DTYPES: Dict[str, StructuredDtype] = {}

    IS_DUPLICATED_EVENT_SERIES_NAME = '__duplicated_event'

    def __init__(self, engine: Engine, table_name: str, global_contexts: List[str]):
        super().__init__()
        self._engine = engine
        self._global_contexts = global_contexts
        self._table_name = table_name

        # check if table has all required columns for pipeline
        dtypes = bach.from_database.get_dtypes_from_table(
            engine=self._engine,
            table_name=self._table_name,
        )

        self._global_contexts_dtypes = self._get_global_contexts_dtypes_from_db_dtypes(db_dtypes=dtypes)
        self._validate_data_dtypes(
            expected_dtypes=self._base_dtypes,
            current_dtypes=dtypes,
        )

    @property
    def _base_dtypes(self) -> Dict[str, StructuredDtype]:
        """
        Mapping between expected columns and series dtypes the pipeline expects in the initial data.
        Each child is responsible of defining BASE_REQUIRED_DB_TYPES and the global contexts dtypes expected
        (if required).
        """
        return {
            **self.BASE_REQUIRED_DB_DTYPES,
            **self._global_contexts_dtypes,
        }

    @abstractmethod
    def _get_global_contexts_dtypes_from_db_dtypes(
        self, db_dtypes: Dict[str, StructuredDtype],
    ) -> Dict[str, StructuredDtype]:
        raise NotImplementedError

    def _get_pipeline_result(self, **kwargs) -> bach.DataFrame:
        """
        Calls all operations performed to the initial data and returns a bach DataFrame with the expected
        context series
        """
        context_df = self._get_initial_data()
        context_df = self._process_data(context_df)
        context_df = self._extract_requested_global_contexts(context_df)

        context_df = self._convert_dtypes(df=context_df)
        context_df = self._apply_filters(df=context_df, **kwargs)

        context_columns = ObjectivSupportedColumns.get_extracted_context_columns()
        context_df = context_df[context_columns + self._global_contexts]

        return context_df.materialize(node_name='context_data')

    @property
    def result_series_dtypes(self) -> Dict[str, str]:
        context_columns = ObjectivSupportedColumns.get_extracted_context_columns()
        supported_dtypes = get_supported_dtypes_per_objectiv_column(
            with_identity_resolution=False,
            with_md_dtypes=True
        )
        return {
            col: dtype for col, dtype in supported_dtypes.items()
            if col in context_columns
        }

    def _get_initial_data(self) -> bach.DataFrame:
        return bach.DataFrame.from_table(
            table_name=self._table_name,
            engine=self._engine,
            index=[],
            all_dtypes=self._base_dtypes,
        )

    @abstractmethod
    def _process_data(self, df: bach.DataFrame) -> bach.DataFrame:
        """
        Transforms and prepares initial event data for global context extraction.
        """
        raise NotImplementedError

    def _extract_requested_global_contexts(self, df: bach.DataFrame) -> bach.DataFrame:
        """
        Creates a new series for location_stack and each requested global context. Provided DataFrame
        is expected to have the required format based on implementation.
        """
        raise NotImplementedError

    def validate_pipeline_result(self, result: bach.DataFrame) -> None:
        """
        Checks if we are returning ALL expected context series with proper dtype.
        """
        check_objectiv_dataframe(
            result,
            columns_to_check=ObjectivSupportedColumns.get_extracted_context_columns(),
            global_contexts_to_check=self._global_contexts,
            check_dtypes=True,
            infer_identity_resolution=False,
            with_md_dtypes=True
        )

    def _apply_filters(
        self,
        df: bach.DataFrame,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        **kwargs,
    ) -> bach.DataFrame:
        """
        Apply different filters on the dataframe.
        Currently only event deduplication and date range are supported.

        returns bach DataFrame
        """
        df_cp = df.copy()

        if (
            self.IS_DUPLICATED_EVENT_SERIES_NAME not in df.data_columns
            and not start_date and not end_date
        ):
            return df_cp

        if (
            self.IS_DUPLICATED_EVENT_SERIES_NAME in df.data_columns
            and df[self.IS_DUPLICATED_EVENT_SERIES_NAME].dtype != bach.SeriesBoolean.dtype
        ):
            raise Exception(f'{self.IS_DUPLICATED_EVENT_SERIES_NAME} must boolean dtype.')

        if not df_cp.is_materialized:
            df_cp = df_cp.materialize()

        date_filters = []
        if start_date:
            date_filters.append(df_cp[self.DATE_FILTER_COLUMN] >= start_date)
        if end_date:
            date_filters.append(df_cp[self.DATE_FILTER_COLUMN] <= end_date)

        all_filters = []
        if date_filters:
            all_filters.append(reduce(operator.and_, date_filters))

        if self.IS_DUPLICATED_EVENT_SERIES_NAME in df_cp.data_columns:
            all_filters.append(~df_cp[self.IS_DUPLICATED_EVENT_SERIES_NAME])

        return df_cp[reduce(operator.or_, all_filters)]


class NativeObjectivExtractedContextsPipeline(BaseExtractedContextsPipeline):
    """
    ExtractedContextsPipeline that process Objectiv native format, where global_contexts and location_stack
    values are required to be extracted from a "taxonomy" json.
    """
    TAXONOMY_JSON_COLUMN_NAME = 'value'
    TAXONOMY_JSON_FIELD_DTYPES = {
        '_type': bach.SeriesString.dtype,
        '_types': bach.SeriesJson.dtype,
        'global_contexts': modelhub.series.SeriesGlobalContexts.dtype,
        'location_stack': modelhub.series.SeriesLocationStack.dtype,
        'time': bach.SeriesInt64.dtype,
    }

    BASE_REQUIRED_DB_DTYPES = {
        'event_id': bach.SeriesUuid.dtype,
        'day': bach.SeriesDate.dtype,
        'moment': bach.SeriesTimestamp.dtype,
        'cookie_id': bach.SeriesUuid.dtype,
        'value': bach.SeriesJson.dtype,
    }

    def _get_global_contexts_dtypes_from_db_dtypes(
        self, db_dtypes: Dict[str, StructuredDtype]
    ) -> Dict[str, StructuredDtype]:
        return {}

    def _process_data(self, df: bach.DataFrame) -> bach.DataFrame:
        """
        Extracts all needed values from the native taxonomy json/dict and creates a new Series for each.

        Returns a bach DataFrame containing each extracted field as series
        """
        df_cp = df.copy()
        taxonomy_series = df_cp[self.TAXONOMY_JSON_COLUMN_NAME].astype(bach.SeriesJson.dtype)
        for key, dtype in self.TAXONOMY_JSON_FIELD_DTYPES.items():
            # parsing element to string and then to dtype will avoid
            # conflicts between casting compatibility
            taxonomy_col = taxonomy_series.json.get_value(key, as_str=True)
            taxonomy_col = taxonomy_col.astype(dtype).copy_override(name=key)
            df_cp[key] = taxonomy_col

        # rename series to objectiv supported before extracting global contexts, as there may be overlap
        df_cp = df_cp.rename(
            columns={
                'cookie_id': ObjectivSupportedColumns.USER_ID.value,
                '_type': ObjectivSupportedColumns.EVENT_TYPE.value,
                '_types': ObjectivSupportedColumns.STACK_EVENT_TYPES.value,
            },
        )
        return df_cp.drop(columns=[self.TAXONOMY_JSON_COLUMN_NAME])

    def _extract_requested_global_contexts(self, df: bach.DataFrame) -> bach.DataFrame:
        """ See implementation in parent class :class:`BaseExtractedContextsPipeline` """
        if ObjectivSupportedColumns.GLOBAL_CONTEXTS.value not in df.data_columns:
            raise Exception(
                f'{self._engine.name} requires flattening for global context extraction, but'
                f'{ObjectivSupportedColumns.GLOBAL_CONTEXTS.value} is not present in dataframe.'
            )
        df_cp = df.copy()

        gc_series = (
            df_cp[ObjectivSupportedColumns.GLOBAL_CONTEXTS.value].astype('objectiv_global_contexts')
        )
        # Extract the requested global contexts
        for gc in self._global_contexts:
            if gc in df_cp.data:
                raise ValueError(f'column {gc} already existing in df, can not extract global context')
            df_cp[gc] = gc_series.obj.get_contexts(gc).astype('objectiv_global_context')

        return df_cp.drop(columns=[ObjectivSupportedColumns.GLOBAL_CONTEXTS.value])


class SnowplowExtractedContextsPipeline(BaseExtractedContextsPipeline, ABC):
    """
    ExtractedContextsPipeline that processes Snowplow flattened format. Format might not be the same
    for all engines implemented in Snowplow, therefore this class should be extended and each
    child must be in charge of handling their own format.
    """
    BASE_REQUIRED_DB_DTYPES = {
        'collector_tstamp': bach.SeriesTimestamp.dtype,
        'event_id': bach.SeriesString.dtype,
        'network_userid': bach.SeriesString.dtype,
        'se_action': bach.SeriesString.dtype,
        'se_category': bach.SeriesString.dtype,
        'true_tstamp': bach.SeriesTimestamp.dtype
    }

    def _process_data(self, df: bach.DataFrame) -> bach.DataFrame:
        """
        Removes duplicated event_ids and renames initial series name to its respectiv Objectiv series name.
        """
        df_cp = df.rename(
            columns={
                'se_action': ObjectivSupportedColumns.EVENT_TYPE.value,
                'se_category': ObjectivSupportedColumns.STACK_EVENT_TYPES.value,
                'network_userid': ObjectivSupportedColumns.USER_ID.value,
            }
        )

        # Mark duplicated event_ids
        # Unfortunately, some events might share an event ID due to
        # browser pre-cachers or scraping bots sending the same event multiple time. Although,
        # legitimate clients might try to send the same events multiple times,
        # in an attempt to make sure that events do not get lost in case of connection problems
        # and/or app reloads. We can easily recognize these events as they'll have non-unique event-ids.
        # In all cases we are only interested in the first event. On postgres we achieve this by having a
        # primary key index on event-id. On BigQuery such indexes are not possible. Instead, we here filter
        # out duplicate event-ids, keeping the first event
        # based on the time the collector sends it to snowplow.
        window = df_cp.sort_values(by=['collector_tstamp']).groupby(by=['event_id']).window()
        df_cp[self.IS_DUPLICATED_EVENT_SERIES_NAME] = (
            df_cp['event_id'].window_row_number(window=window) > 1
        )
        # Snowplow data source has no moment and day columns, therefore we need to generate them
        if df_cp['true_tstamp'].dtype == 'timestamp':
            df_cp['moment'] = df_cp['true_tstamp']
        else:
            df_cp['moment'] = df_cp['true_tstamp'].copy_override(
                expression=bach.expression.Expression.construct(
                    f'TIMESTAMP_MILLIS({{}})', df_cp['true_tstamp']
                )
            ).copy_override_type(bach.SeriesTimestamp)

        if 'day' not in df_cp.data_columns:
            df_cp['day'] = df_cp['moment'].astype('date')

        return df_cp.drop(columns=['true_tstamp', 'collector_tstamp'])


class BigQueryExtractedContextsPipeline(SnowplowExtractedContextsPipeline):
    """
    BigQuery Pipeline implementation for SnowplowExtractedContextsPipeline. This pipeline
    assumes there is a column per global context and a single column for location stack.
    """
    def _get_global_context_mapping_from_series_names(self, series_names: List[str]):
        """
        Returns mapping between db column name and global context name.
        """
        # match things like contexts_io_objectiv_context_cookie_id_context_1_0_0 -> cookie_id
        # but also contexts_io_objectiv_location_stack_1_0_0 -> location_stack
        global_contexts_column_mapping: Dict[str, str] = {}

        base_patterns = [r'(?P<ls_context>location_stack)']
        if self._global_contexts:
            base_patterns.append(rf"(context_(?P<gc_context>{'|'.join(self._global_contexts)})_context)",)
        pattern_global_context = re.compile(
            rf"contexts_io_objectiv_({'|'.join(base_patterns)})_\d_\d_\d"
        )

        for col in series_names:
            match = pattern_global_context.search(col)
            if not match:
                continue

            context_name = match.group('ls_context') or match.group('gc_context')

            global_contexts_column_mapping[col] = context_name

        return global_contexts_column_mapping

    def _get_global_contexts_dtypes_from_db_dtypes(
        self, db_dtypes: Dict[str, StructuredDtype],
    ) -> Dict[str, StructuredDtype]:
        """
        Returns mapping between global context columns and expected series dtype for each.
        """
        gc_mapping = self._get_global_context_mapping_from_series_names(list(db_dtypes.keys()))
        missing = ({'location_stack'} & set(self._global_contexts)) - set(gc_mapping.values())
        if missing:
            raise ValueError(f'Requested global contexts {sorted(missing)} not found in data.')

        return {
            db_col_name: [{}]
            if gc_name in self._global_contexts else [{gc_name: bach.SeriesString.dtype}]
            for db_col_name, gc_name in gc_mapping.items()
        }

    def _extract_requested_global_contexts(self, df: bach.DataFrame) -> bach.DataFrame:
        """ See implementation in parent class :class:`BaseExtractedContextsPipeline` """
        gc_mapping = self._get_global_context_mapping_from_series_names(
            series_names=df.data_columns
        )

        df_cp = df.rename(columns=gc_mapping)

        ls_series_name = str(ObjectivSupportedColumns.LOCATION_STACK.value)

        # for BQ, location stack series has the following format:
        # [{'location_stack': '[{...}, {...},...]'}]
        # therefore we need to extract the first element in the array and afterwards the value
        # of location_stack
        ls_series_list = df_cp[ls_series_name].copy_override_type(bach.SeriesList, instance_dtype=[{}])
        ls_series_dict = ls_series_list.elements[0].copy_override_type(
            series_type=bach.SeriesDict, instance_dtype={'location_stack': bach.SeriesString.dtype}
        )
        df_cp[ls_series_name] = ls_series_dict.elements['location_stack']

        return df_cp.astype(
            {
                ls_series_name: 'objectiv_location_stack',
                **{gc: 'objectiv_global_context' for gc in self._global_contexts}
            }
        )


def get_extracted_context_pipeline(
    engine: Engine, table_name: str, global_contexts: List[str]
) -> BaseExtractedContextsPipeline:
    """
    Returns an instance of ExtractedContextPipeline based on the provided engine.
    """
    if is_postgres(engine):
        # currently we only support old format for Postgres
        return NativeObjectivExtractedContextsPipeline(engine, table_name, global_contexts)

    if is_bigquery(engine):
        return BigQueryExtractedContextsPipeline(engine, table_name, global_contexts)

    raise Exception(f'There is no ExtractedContextsPipeline subclass for {engine.name}.')
