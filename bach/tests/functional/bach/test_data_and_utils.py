"""
Copyright 2021 Objectiv B.V.

Utilities and a very simple dataset for testing Bach DataFrames.

This file does not contain any test, but having the file's name start with `test_` makes pytest treat it
as a test file. This makes pytest rewrite the asserts to give clearer errors.
"""
import datetime
import uuid
from copy import copy
from decimal import Decimal
from typing import List, Union, Type, Any, Dict

import pandas as pd
import sqlalchemy
from sqlalchemy.engine import ResultProxy, Engine, Dialect

from bach import DataFrame, Series
from bach.types import get_series_type_from_db_dtype
from sql_models.constants import DBDialect
from sql_models.util import is_bigquery, is_postgres, is_athena
from tests.unit.bach.util import get_pandas_df

# Three data tables for testing are defined here that can be used in tests
# 1. cities: 3 rows (or 11 for the full dataset) of data on cities
# 2. food: 3 rows of food data
# 3. railways: 7 rows of data on railway stations

# cities is the main table and should be used when sufficient. The other tables can be used in addition
# for more complex scenarios (e.g. merging)
ROW_LIMIT = 3
TEST_DATA_CITIES_FULL = [
    [1, 'Ljouwert', 'Leeuwarden', 93485, 1285],
    [2, 'Snits', 'Súdwest-Fryslân', 33520, 1456],
    [3, 'Drylts', 'Súdwest-Fryslân', 3055, 1268],
    [4, 'Sleat', 'De Friese Meren', 700, 1426],
    [5, 'Starum', 'Súdwest-Fryslân', 960, 1061],
    [6, 'Hylpen', 'Súdwest-Fryslân', 870, 1225],
    [7, 'Warkum', 'Súdwest-Fryslân', 4440, 1399],
    [8, 'Boalsert', 'Súdwest-Fryslân', 10120, 1455],
    [9, 'Harns', 'Harlingen', 14740, 1234],
    [10, 'Frjentsjer', 'Waadhoeke', 12760, 1374],
    [11, 'Dokkum', 'Noardeast-Fryslân', 12675, 1298],
]
# The TEST_DATA set that we'll use in most tests is limited to 3 rows for convenience.
TEST_DATA_CITIES = TEST_DATA_CITIES_FULL[:ROW_LIMIT]
CITIES_COLUMNS_X_DTYPES = {
    'skating_order': 'int64',
    'city': 'string',
    'municipality': 'string',
    'inhabitants': 'int64',
    'founding': 'int64'
}
CITIES_COLUMNS = list(CITIES_COLUMNS_X_DTYPES.keys())
# The default dataframe has skating_order as index, so that column will be prepended before the actual
# data in the query results.
CITIES_INDEX_AND_COLUMNS = ['_index_skating_order'] + CITIES_COLUMNS

TEST_DATA_FOOD = [
    [1, 'Sûkerbôlle', '2021-05-03 11:28:36.388', '2021-05-03'],
    [2, 'Dúmkes', '2021-05-04 23:28:36.388', '2021-05-04'],
    [4, 'Grutte Pier Bier', '2022-05-03 14:13:13.388', '2022-05-03']
]
FOOD_COLUMNS_X_DTYPES = {
    'skating_order': 'int64',
    'food': 'string',
    'moment': 'timestamp',
    'date': 'date',
}
FOOD_COLUMNS = list(FOOD_COLUMNS_X_DTYPES.keys())
FOOD_INDEX_AND_COLUMNS = ['_index_skating_order'] + FOOD_COLUMNS

TEST_DATA_RAILWAYS = [
    [1, 'Drylts', 'IJlst', 1],
    [2, 'It Hearrenfean', 'Heerenveen', 1],
    [3, 'It Hearrenfean', 'Heerenveen IJsstadion', 2],
    [4, 'Ljouwert', 'Leeuwarden', 4],
    [5, 'Ljouwert', 'Camminghaburen', 1],
    [6, 'Snits', 'Sneek', 2],
    [7, 'Snits', 'Sneek Noord', 2],
]
RAILWAYS_COLUMNS_X_DTYPES = {
    'station_id': 'int64',
    'town': 'string',
    'station': 'string',
    'platforms': 'int64',
}
RAILWAYS_COLUMNS = list(RAILWAYS_COLUMNS_X_DTYPES.keys())
RAILWAYS_INDEX_AND_COLUMNS = ['_index_station_id'] + RAILWAYS_COLUMNS

TEST_DATA_JSON = [
    [0,
     '{"a": "b"}',
     '[{"a": "b"}, {"c": "d"}]',
     '{"a": "b"}'
     ],
    [1,
     '{"_type": "SectionContext", "id": "home"}',
     '["a","b","c","d"]',
     '["a","b","c","d"]'
     ],
    [2,
     '{"a": "b", "c": {"a": "c"}}',
     '[{"_type": "a", "id": "b"},{"_type": "c", "id": "d"},{"_type": "e", "id": "f"}]',
     '{"a": "b", "c": {"a": "c"}}'
     ],
    [3,
     '{"a": "b", "e": [{"a": "b"}, {"c": "d"}]}',
     '[{"_type":"WebDocumentContext","id":"#document"},'
     ' {"_type":"SectionContext","id":"home"},'
     ' {"_type":"SectionContext","id":"top-10"},'
     ' {"_type":"ItemContext","id":"5o7Wv5Q5ZE"}]',
     '[{"_type":"WebDocumentContext","id":"#document"},'
     ' {"_type":"SectionContext","id":"home"},'
     ' {"_type":"SectionContext","id":"top-10"},'
     ' {"_type":"ItemContext","id":"5o7Wv5Q5ZE"}]'
     ],
    [4,
     None,
     None,
     None
     ],
]
JSON_COLUMNS = ['row', 'dict_column', 'list_column', 'mixed_column']
JSON_INDEX_AND_COLUMNS = ['_row_id'] + JSON_COLUMNS


def get_df_with_test_data(engine: Engine, full_data_set: bool = False) -> DataFrame:
    dataset = TEST_DATA_CITIES_FULL if full_data_set else TEST_DATA_CITIES
    return DataFrame.from_pandas(
        engine=engine,
        df=get_pandas_df(dataset, CITIES_COLUMNS),
        convert_objects=True
    )


def get_df_with_food_data(engine: Engine) -> DataFrame:
    return DataFrame.from_pandas(
        engine=engine,
        df=get_pandas_df(TEST_DATA_FOOD, FOOD_COLUMNS),
        convert_objects=True,
    )


def get_df_with_railway_data(engine: Engine) -> DataFrame:
    return DataFrame.from_pandas(
        engine=engine,
        df=get_pandas_df(TEST_DATA_RAILWAYS, RAILWAYS_COLUMNS),
        convert_objects=True,
    )


def get_df_with_json_data(engine: Engine, dtype='json') -> DataFrame:
    assert dtype in ('string', 'json', 'json_postgres')
    df = DataFrame.from_pandas(
        engine=engine,
        df=get_pandas_df(TEST_DATA_JSON, JSON_COLUMNS),
        convert_objects=True,
    )
    if dtype:
        df['dict_column'] = df.dict_column.astype(dtype)
        df['list_column'] = df.list_column.astype(dtype)
        df['mixed_column'] = df.mixed_column.astype(dtype)
    return df.materialize()


def run_query(engine: sqlalchemy.engine, sql: str) -> ResultProxy:
    # escape sql, as conn.execute will think that '%' indicates a parameter
    sql = sql.replace('%', '%%')
    with engine.connect() as conn:
        res = conn.execute(sql)
        return res


def df_to_list(df):
    data_list = df.reset_index().to_numpy().tolist()
    return(data_list)


def _convert_uuid_expected_data(engine: Engine, data: List[List[Any]]) -> List[List[Any]]:
    """
    Convert any UUID objects in data to string, if we represent uuids with strings in the engine's dialect.
    """
    if is_postgres(engine):
        return data
    if is_athena(engine) or is_bigquery(engine):
        result = [
            [str(cell) if isinstance(cell, uuid.UUID) else cell for cell in row]
            for row in data
        ]
        return result
    raise Exception(f'engine not supported {engine}')


def assert_equals_data(
    bt: Union[DataFrame, Series],
    expected_columns: List[str],
    expected_data: List[list],
    order_by: Union[str, List[str]] = None,
    use_to_pandas: bool = False,
    round_decimals: bool = False,
    decimal=4,
    convert_uuid: bool = False,
) -> List[List[Any]]:
    """
    Execute the sql of ButTuhDataFrame/Series's view_sql(), with the given order_by, and make sure the
    result matches the expected columns and data.

    Note: By default this does not call `to_pandas()`, which we nowadays consider our 'normal' path,
    but directly executes the result from `view_sql()`. To test `to_pandas()` set use_to_pandas=True.
    :return: the values queried from the database
    """
    if len(expected_data) == 0:
        raise ValueError("Cannot check data if 0 rows are expected.")

    if isinstance(bt, Series):
        # Otherwise sorting does not work as expected
        bt = bt.to_frame()

    if convert_uuid:
        expected_data = _convert_uuid_expected_data(bt.engine, expected_data)

    if order_by:
        bt = bt.sort_values(order_by)
    elif not bt.order_by:
        bt = bt.sort_index()

    if not use_to_pandas:
        column_names, db_values = _get_view_sql_data(bt)
    else:
        column_names, db_values = _get_to_pandas_data(bt)

    assert len(db_values) == len(expected_data)
    assert column_names == expected_columns

    _date_freq = 'ms' if is_athena(bt.engine) else 'us'
    for i, df_row in enumerate(db_values):
        expected_row = expected_data[i]
        assert len(df_row) == len(expected_row)
        for j, val in enumerate(df_row):
            actual = copy(val)
            expected = copy(expected_row[j])

            if isinstance(val, (float, Decimal)) and round_decimals:
                actual = round(Decimal(actual), decimal)
                expected = round(Decimal(expected), decimal)

            if isinstance(actual, pd.Timestamp):
                pdt_expected = pd.Timestamp(expected, tz=None)
                actual = actual.floor(freq=_date_freq)
                expected = pdt_expected.floor(freq=_date_freq)

            assert_msg = f'row {i} is not equal: {expected_row} != {df_row}'
            if actual is pd.NaT:
                assert expected is pd.NaT, assert_msg
            else:
                assert actual == expected, assert_msg
    return db_values


def _get_view_sql_data(df: DataFrame):
    sql = df.view_sql()
    db_rows = run_query(df.engine, sql)
    column_names = list(db_rows.keys())
    db_values = [list(row) for row in db_rows]
    print(db_values)
    return column_names, db_values


def _get_to_pandas_data(df: DataFrame):
    pdf = df.to_pandas()
    # Convert pdf to the same format as _get_view_sql_data gives
    column_names = (list(pdf.index.names) if df.index else []) + list(pdf.columns)
    pdf = pdf.reset_index()
    db_values = []
    for value_row in pdf.to_numpy().tolist():
        db_values.append(value_row if df.index else value_row[1:])  # don't include default index value
    print(db_values)
    return column_names, db_values


def assert_postgres_type(
        series: Series,
        expected_db_type: str,
        expected_series_type: Type[Series]
):
    """
    Check that the given Series has the expected data type in the Postgres database, and that it has the
    expected Series type after being read back from the database.

    This uses series.engine as the connection.
    NOTE: If series.engine is not a Postgres engine, then this function simply returns without doing any
    asserts!

    :param series: Series object to check the type of
    :param expected_db_type: one of the types listed on https://www.postgresql.org/docs/current/datatype.html
    :param expected_series_type: Subclass of Series
    """
    engine = series.engine
    if not is_postgres(engine):
        return
    sql = series.to_frame().view_sql()
    sql = f'with check_type as ({sql}) select pg_typeof("{series.name}") from check_type limit 1'
    db_rows = run_query(engine=engine, sql=sql)
    db_values = [list(row) for row in db_rows]
    db_type = db_values[0][0]
    if expected_db_type:
        assert db_type == expected_db_type
    series_type = get_series_type_from_db_dtype(DBDialect.POSTGRES, db_type)
    assert series_type == expected_series_type


def assert_db_types(
        df: DataFrame,
        series_expected_db_type: Dict[str, str],
):
    """
    Check that the given series in the DataFrame have the expected data types in the database.

    ONLY supported for Postgres and Athena. Other database engines will raise an exception.

    :param df: DataFrame object for which to check the database types
    :param series_expected_db_type: mapping of series-names, to database types.
    """
    engine = df.engine
    if is_postgres(engine):
        typeof_function_name = 'pg_typeof'
    elif is_athena(engine):
        typeof_function_name = 'typeof'
    else:
        raise Exception(f'Not supported: {engine.name}')

    df_sql = df.view_sql()
    types_sql = ', '.join(
        f'{typeof_function_name}("{series_name}")'for series_name in series_expected_db_type.keys()
    )
    sql = f'with check_type as ({df_sql}) select {types_sql} from check_type limit 1'
    db_rows = run_query(engine=engine, sql=sql)
    db_values = [list(row) for row in db_rows]
    for i, series_name in enumerate(series_expected_db_type.keys()):
        expected_db_type = series_expected_db_type[series_name]
        db_type = db_values[0][i]
        msg = f"expected type {expected_db_type} for {series_name}, found {db_type}"
        assert db_type == expected_db_type, msg


def convert_expected_data_timestamps(dialect: Dialect, data: List[List[Any]]) -> List[List[Any]]:
    """ Set UTC timezone on datetime objects if dialect is BigQuery. """
    def set_tz(value):
        if not isinstance(value, (datetime.datetime, datetime.date)) or not is_bigquery(dialect):
            return value
        return value.replace(tzinfo=datetime.timezone.utc)
    return [[set_tz(cell) for cell in row] for row in data]
