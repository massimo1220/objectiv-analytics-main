"""
Copyright 2022 Objectiv B.V.
"""
import datetime
import json
from typing import List

import bach
import pandas as pd
import pytest
from sql_models.util import is_bigquery
from tests.functional.bach.test_data_and_utils import assert_equals_data

from modelhub.pipelines.extracted_contexts import BaseExtractedContextsPipeline, get_extracted_context_pipeline
from tests_modelhub.data_and_utils.utils import create_engine_from_db_params, get_parsed_objectiv_data, \
    DBParams

_EXPECTED_CONTEXT_COLUMNS = [
    'event_id',
    'day',
    'moment',
    'user_id',
    'location_stack',
    'event_type',
    'stack_event_types',
]


def _get_parsed_test_data_pandas_df(engine, db_format: DBParams.Format) -> pd.DataFrame:
    parsed_data = get_parsed_objectiv_data(engine)
    if not is_bigquery(engine):
        assert db_format == DBParams.Format.OBJECTIV
        return pd.DataFrame(parsed_data)

    bq_data = []
    for event in parsed_data:
        if db_format == DBParams.Format.SNOWPLOW :
            bq_data.append(
                {
                    'collector_tstamp': datetime.datetime.utcfromtimestamp(event['value']['time'] / 1e3),
                    'event_id': str(event['event_id']),
                    'network_userid': str(event['cookie_id']),
                    'se_action': event['value']['_type'],
                    'se_category': json.dumps(event['value']['_types']),
                    'true_tstamp': datetime.datetime.utcfromtimestamp(event['value']['time'] / 1e3),
                    'contexts_io_objectiv_location_stack_1_0_0': [
                        {'location_stack': json.dumps(event['value']['location_stack'])}
                    ],
                }
            )
        else:
            raise TypeError(f"Unsupported db format {db_format}")

    return pd.DataFrame(bq_data)


def get_expected_context_pandas_df(
        engine, db_format: DBParams.Format, global_contexts: List[str] = None,
) -> pd.DataFrame:

    field_name_mapping = {}
    for context_name in global_contexts or []:
        capitalized_name = "".join([c.capitalize() for c in context_name.split('_')])+'Context'
        field_name_mapping[capitalized_name] = context_name

    data = get_parsed_objectiv_data(engine)

    # Append requested global contexts, and remove the all containing one
    for i, row in enumerate(data):
        # cookie_id can also be a global context name, make sure it's not overwritten
        row['user_id'] = row['cookie_id']
        del(row['cookie_id'])

        # create one column for every requested context, for every row
        row_context_data = {c: [] for c in field_name_mapping.values()}
        for row_context_item in row['value']['global_contexts']:
            if row_context_item['_type'] in field_name_mapping:
                toplevel_field_name = field_name_mapping[row_context_item['_type']]
                if db_format == DBParams.Format.SNOWPLOW:
                    # SP format does not carry types
                    if '_type' in row_context_item:
                        del(row_context_item['_type'])
                    if '_types' in row_context_item:
                        del(row_context_item['_types'])
                row_context_data[toplevel_field_name].append(row_context_item)
        row['value'] = {**row['value'], **row_context_data}
        del(row['value']['global_contexts'])

    pdf = pd.DataFrame(data)
    context_pdf = pdf['value'].apply(pd.Series)

    context_pdf['event_id'] = pdf['event_id']
    context_pdf['day'] = pdf['day']
    context_pdf['moment'] = pdf['moment']
    context_pdf['user_id'] = pdf['user_id']
    context_pdf = context_pdf.rename(
        columns={
            '_type': 'event_type',
            '_types': 'stack_event_types',
        }
    )

    return context_pdf[_EXPECTED_CONTEXT_COLUMNS + (global_contexts or [])]


def _get_extracted_contexts_pipeline(db_params, global_contexts=None) -> BaseExtractedContextsPipeline:
    engine = create_engine_from_db_params(db_params)
    return get_extracted_context_pipeline(engine=engine, table_name=db_params.table_name,
                                     global_contexts=global_contexts or [])


def test_get_pipeline_result(db_params) -> None:
    # select cookie_id context since it's gc column overlaps with cookie_id uuid column on pg.
    # cookie_id_context also has a multi-part name, so we test that immediately as well. Exciting :)
    context_pipeline = _get_extracted_contexts_pipeline(db_params, global_contexts=['identity', 'cookie_id'])
    engine = context_pipeline._engine

    result = context_pipeline().sort_values(by='event_id').to_pandas()

    expected = get_expected_context_pandas_df(
        engine, global_contexts=['identity', 'cookie_id'], db_format=db_params.format
    )
    pd.testing.assert_frame_equal(expected, result)


def test_get_initial_data(db_params) -> None:
    context_pipeline = _get_extracted_contexts_pipeline(db_params)
    engine = context_pipeline._engine
    expected = _get_parsed_test_data_pandas_df(engine, db_params.format)
    result = context_pipeline._get_initial_data()

    if db_params.format == DBParams.Format.OBJECTIV:
        assert set(result.data_columns) == set(expected.columns)
        sorted_columns = sorted(result.data_columns)
        result = result[sorted_columns].sort_values(by='event_id')
        assert_equals_data(
            result,
            expected_columns=sorted_columns,
            expected_data=expected[sorted_columns].to_numpy().tolist(),
            use_to_pandas=True,
        )
        return

    if db_params.format == DBParams.Format.SNOWPLOW:
        location_stack_column = 'contexts_io_objectiv_location_stack_1_0_0'
        assert location_stack_column in result.data
        assert result[location_stack_column].dtype == 'list'
        assert result[location_stack_column].elements[0].elements['location_stack'].dtype == 'string'
        assert 'event_id' in result.data

        # need to sort the rows since order is non-deterministic
        result = result.sort_values(by='event_id')

        assert_equals_data(
            result,
            expected_columns=['collector_tstamp', 'event_id', 'network_userid', 'se_action',
                              'se_category', 'true_tstamp', 'contexts_io_objectiv_location_stack_1_0_0'],
            expected_data=expected.to_numpy().tolist(),
            use_to_pandas=True,
        )
    else:
        raise Exception()


def test_process_data(db_params) -> None:
    context_pipeline = _get_extracted_contexts_pipeline(db_params)
    engine = context_pipeline._engine

    df = context_pipeline._get_initial_data()

    if is_bigquery(engine):
        assert 'day' not in df.data
        assert 'moment' not in df.data

    df = context_pipeline._process_data(df)
    assert 'day' in df.data
    assert 'moment' in df.data

    df = context_pipeline._convert_dtypes(df)
    result = df.reset_index(drop=True)

    expected_series = [
        'user_id', 'event_type', 'stack_event_types', 'event_id', 'day', 'moment',
    ]

    result = result.sort_values(by='event_id')[expected_series].to_pandas()
    expected = (
        get_expected_context_pandas_df(engine, db_format=db_params.format)
        .sort_values(by='event_id')[expected_series]
    )

    pd.testing.assert_frame_equal(
        expected,
        result,
        check_index_type=False,
    )


@pytest.mark.skip_postgres
def test_apply_filters_duplicated_event_ids(db_params) -> None:
    context_pipeline = _get_extracted_contexts_pipeline(db_params)
    engine = context_pipeline._engine

    default_timestamp = datetime.datetime(2022, 1, 1,  1,  1, 1)
    tstamps = [
        datetime.datetime(2022, 1, 1, 12, 0, 0),
        default_timestamp,
        default_timestamp,
        datetime.datetime(2022, 1, 1, 12, 0, 1),
        datetime.datetime(2022, 1, 2, 12, 0, 1),
        datetime.datetime(2022, 1, 1, 11, 59, 59),
        datetime.datetime(2022, 1, 3, 12, 0, 1)
    ]
    pdf = pd.DataFrame(
        {
            'event_id': ['1', '2', '3', '1', '4', '1', '4'],
            'collector_tstamp': tstamps,
            'true_tstamp': tstamps,
            'contexts_io_objectiv_location_stack_1_0_0': ['{}'] * 7,
        }
    )
    df = bach.DataFrame.from_pandas(engine, pdf, convert_objects=True).reset_index(drop=True)
    result = context_pipeline._process_data(df)
    result = context_pipeline._apply_filters(result)

    # collector_timestamp will be removed, so will true_tstamp, but the latter will live on as moment
    # so we can use that one to check whether the right event was selected.
    assert_equals_data(
        result.sort_values(by='event_id')[['event_id', 'moment']],
        expected_columns=['event_id', 'moment'],
        expected_data=[
            ['1', datetime.datetime(2022, 1, 1, 11, 59, 59)],
            ['2', default_timestamp],
            ['3', default_timestamp],
            ['4', datetime.datetime(2022, 1, 2, 12,  0, 1)],
        ],
        use_to_pandas=True,
    )


def test_apply_filters(db_params) -> None:
    context_pipeline = _get_extracted_contexts_pipeline(db_params)
    engine = context_pipeline._engine

    pdf = get_expected_context_pandas_df(engine, db_params.format)[['event_id', 'day']]
    if is_bigquery(engine):
        pdf['event_id'] = pdf['event_id'].astype(str)

    df = bach.DataFrame.from_pandas(engine=engine, df=pdf, convert_objects=True)
    df = df.reset_index(drop=True)

    result = context_pipeline._apply_filters(df)
    assert df == result

    start_date = '2021-12-01'
    result = context_pipeline._apply_filters(df, start_date=start_date).sort_values(by='event_id')
    start_mask = pdf['day'] >= datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
    expected = pdf[start_mask].reset_index(drop=True)

    pd.testing.assert_frame_equal(expected, result.to_pandas(), check_index_type=False)

    end_date = '2021-12-02'
    result = context_pipeline._apply_filters(df, end_date=end_date).sort_values(by='event_id')
    end_mask = pdf['day'] <= datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
    expected = pdf[end_mask].reset_index(drop=True)

    pd.testing.assert_frame_equal(expected, result.to_pandas(), check_index_type=False)

    result = context_pipeline._apply_filters(
        df, start_date=start_date, end_date=end_date,
    ).sort_values(by='event_id')
    expected = pdf[start_mask & end_mask].reset_index(drop=True)

    pd.testing.assert_frame_equal(expected, result.to_pandas(), check_index_type=False)


def test_extract_requested_global_contexts(db_params) -> None:
    global_contexts = ['application']
    context_pipeline = _get_extracted_contexts_pipeline(db_params, global_contexts=global_contexts)
    engine = context_pipeline._engine

    df = context_pipeline._get_initial_data()
    df = context_pipeline._process_data(df)
    df = context_pipeline._extract_requested_global_contexts(df)
    df = context_pipeline._convert_dtypes(df)
    result = df.reset_index(drop=True)

    expected_series = ['event_id', 'location_stack', 'application']

    result = result.sort_values(by='event_id')[expected_series].to_pandas()
    expected = (
        get_expected_context_pandas_df(engine, db_format=db_params.format, global_contexts=global_contexts)
        .sort_values(by='event_id')[expected_series]
    )

    pd.testing.assert_frame_equal(
        expected,
        result,
        check_index_type=False,
    )
