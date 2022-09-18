"""
Copyright 2021 Objectiv B.V.
"""
import pytest

from bach import SeriesBoolean, SeriesInt64, SeriesString, \
    SeriesFloat64, SeriesTimestamp, DataFrame
from tests.functional.bach.test_data_and_utils import assert_postgres_type

import datetime

from tests.unit.bach.util import get_pandas_df


@pytest.mark.skip_athena_todo()
@pytest.mark.skip_bigquery_todo()
def test_all_supported_types(engine):
    TEST_DATA_SUPPORTED_TYPES = [
        [1.32, 4, datetime.datetime(2015, 12, 13, 9, 54, 45, 543), 'fierljeppen', True]
    ]
    bt = DataFrame.from_pandas(
        engine=engine,
        df=get_pandas_df(TEST_DATA_SUPPORTED_TYPES, ['float', 'int', 'timestamp', 'string', 'bool']),
        convert_objects=True,
    )

    # TODO: don't use assert_postgres_type here
    assert_postgres_type(bt['float'], 'double precision', SeriesFloat64)
    assert_postgres_type(bt['int'], 'bigint', SeriesInt64)
    assert_postgres_type(bt['timestamp'], 'timestamp without time zone', SeriesTimestamp)
    assert_postgres_type(bt['string'], 'text', SeriesString)
    assert_postgres_type(bt['bool'], 'boolean', SeriesBoolean)



@pytest.mark.skip_athena_todo()
@pytest.mark.skip_bigquery_todo()
def test_string_as_index(engine):
    TEST_DATA_SUPPORTED_TYPES = [
        ['fierljeppen', 1.32, 4, datetime.datetime(2015, 12, 13, 9, 54, 45, 543), True]
    ]

    bt = DataFrame.from_pandas(
        engine=engine,
        df=get_pandas_df(TEST_DATA_SUPPORTED_TYPES, ['string', 'float', 'int', 'timestamp', 'bool']),
        convert_objects=True,
    )

    # TODO: don't use assert_postgres_type here
    assert_postgres_type(bt['float'], 'double precision', SeriesFloat64)
    assert_postgres_type(bt['int'], 'bigint', SeriesInt64)
    assert_postgres_type(bt['timestamp'], 'timestamp without time zone', SeriesTimestamp)
    assert_postgres_type(bt['string'], 'text', SeriesString)
    assert_postgres_type(bt['bool'], 'boolean', SeriesBoolean)


@pytest.mark.skip_athena_todo()
@pytest.mark.skip_bigquery_todo()
def test_load_df_without_conversion(engine):
    TEST_DATA_SUPPORTED_TYPES = [
        [1.32, 4, datetime.datetime(2015, 12, 13, 9, 54, 45, 543), True]
    ]
    bt = DataFrame.from_pandas(
        engine=engine,
        df=get_pandas_df(TEST_DATA_SUPPORTED_TYPES, ['float', 'int', 'timestamp', 'bool']),
        convert_objects=True,
    )

    # TODO: don't use assert_postgres_type here
    assert_postgres_type(bt['float'], 'double precision', SeriesFloat64)
    assert_postgres_type(bt['int'], 'bigint', SeriesInt64)
    assert_postgres_type(bt['timestamp'], 'timestamp without time zone', SeriesTimestamp)
    assert_postgres_type(bt['bool'], 'boolean', SeriesBoolean)
