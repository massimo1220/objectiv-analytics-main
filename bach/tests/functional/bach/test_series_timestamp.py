"""
Copyright 2021 Objectiv B.V.
"""
import datetime
from typing import List, Any

import numpy
import pandas as pd
import pytest
from sqlalchemy.engine import Engine

from sql_models.util import is_athena
from tests.functional.bach.test_data_and_utils import assert_equals_data, get_df_with_test_data,\
    get_df_with_food_data


def floor_datetime(engine, dt: datetime.datetime) -> datetime.datetime:
    pdt = pd.Timestamp.fromtimestamp(dt.timestamp())
    if is_athena(engine):
        return pdt.floor(freq='ms')

    return pdt.floor(freq='us')


def test_timestamp_data(engine):
    mt = get_df_with_food_data(engine)[['moment']]
    mt['const1'] = datetime.datetime(1999, 12, 31, 23, 59, 59, 999999)
    mt['const2'] = numpy.datetime64('2022-02-03 12:34:56.789', 'ns')
    mt['const3'] = numpy.datetime64('2022-02-03 12:34:56.789123', 'ns')
    mt['const4'] = numpy.datetime64('2022-02-03 12:34:56.789123456', 'ns')
    expected_constants = [
        datetime.datetime(1999, 12, 31, 23, 59, 59, 999999),
        datetime.datetime(2022,  2,  3, 12, 34, 56, 789000),
        datetime.datetime(2022,  2,  3, 12, 34, 56, 789123),
        datetime.datetime(2022,  2,  3, 12, 34, 56, 789123),
    ]
    assert_equals_data(
        mt,
        # raw sqlAlchemy will give datetime with timezone UTC on some Databases, because of the used db types
        # so set use_to_pandas=True to do our data normalization in the DataFrame.to_pandas() function
        use_to_pandas=True,
        expected_columns=['_index_skating_order', 'moment', 'const1', 'const2', 'const3', 'const4'],
        expected_data=[
            [1, datetime.datetime(2021, 5, 3, 11, 28, 36, 388000)] + expected_constants,
            [2, datetime.datetime(2021, 5, 4, 23, 28, 36, 388000)] + expected_constants,
            [4, datetime.datetime(2022, 5, 3, 14, 13, 13, 388000)] + expected_constants
        ]
    )


def test_to_pandas(engine):
    bt = get_df_with_test_data(engine)
    bt['dt'] = datetime.datetime(2021, 5, 3, 11, 28, 36, 388000)
    result_pdf = bt.to_pandas()
    assert result_pdf['dt'].to_numpy()[0] == [numpy.array(['2021-05-03T11:28:36.388000000'], dtype='datetime64[ns]')]


@pytest.mark.parametrize("asstring", [True, False])
def test_timestamp_comparator(engine, asstring: bool):
    mt = get_df_with_food_data(engine)[['moment']]
    from datetime import datetime
    dt = datetime(2021, 5, 4, 23, 28, 36, 388000)

    if asstring:
        dt = str(dt)

    mt['eq'] = mt['moment'] == dt
    mt['gte'] = mt['moment'] >= dt
    mt['gt'] = mt['moment'] > dt
    mt['lte'] = mt['moment'] <= dt
    mt['lt'] = mt['moment'] < dt

    assert_equals_data(
        mt,
        # raw sqlAlchemy will give datetime with timezone UTC on some Databases, because of the used db types
        # so set use_to_pandas=True to do our data normalization in the DataFrame.to_pandas() function
        use_to_pandas=True,
        expected_columns=[
            '_index_skating_order', 'moment', 'eq', 'gte', 'gt', 'lte', 'lt'
        ],
        expected_data=[
            [1, datetime(2021, 5, 3, 11, 28, 36, 388000), False, False, False, True, True],
            [2, datetime(2021, 5, 4, 23, 28, 36, 388000), True, True, False, True, False],
            [4, datetime(2022, 5, 3, 14, 13, 13, 388000), False, True, True, False, False],
        ]
    )


def test_timestamp_value_to_literal(engine):
    mt = get_df_with_food_data(engine)[['moment']]

    with pytest.raises(ValueError, match=r'Not a valid string literal'):
        mt['string'] = '2022-02-03 12:34:56.789123456'
        mt['string'] = mt['string'].astype('timestamp')

    mt['string'] = '2022-02-03 12:34:56.789123'
    mt['string'] = mt['string'].astype('timestamp')
    mt['none'] = None
    mt['none'] = mt['none'].astype('timestamp')
    mt['np_datetime64'] = numpy.datetime64('2022-01-01 12:34:56.7800')
    mt['datetime'] = datetime.datetime(2021, 5, 3, 11, 28, 36, 388000)
    result = mt.loc[mt.index['_index_skating_order'] == 1][['string', 'none', 'np_datetime64', 'datetime']]
    # TODO: when date is supported for athena
    # mt['date'] = datetime.date(2020, 3, 11)

    assert_equals_data(
        result,
        # raw sqlAlchemy will give datetime with timezone UTC on some Databases, because of the used db types
        # so set use_to_pandas=True to do our data normalization in the DataFrame.to_pandas() function
        use_to_pandas=True,
        expected_columns=[
            '_index_skating_order', 'string', 'none', 'np_datetime64', 'datetime',
        ],
        expected_data=[
            [
                1,
                datetime.datetime(2022, 2, 3, 12, 34, 56, 789123),
                pd.NaT,
                datetime.datetime(2022, 1, 1, 12, 34, 56, 780000),
                datetime.datetime(2021, 5, 3, 11, 28, 36, 388000),
            ],

        ]
    )


def test_timestamp_arithmetic(engine):
    data = [
        ['d', datetime.date(2020, 3, 11), 'date', (None, None)],
        ['t', datetime.time(23, 11, 5), 'time', (None, None)],
        ['td', datetime.timedelta(days=321, seconds=9877), 'timedelta', ('timestamp', 'timestamp')],
        ['dt', datetime.datetime(2021, 5, 3, 11, 28, 36, 388000), 'timestamp', (None, 'timedelta')]
    ]
    types_plus_min(engine, data, datetime.datetime(2019, 8, 16, 2, 54, 39, 166000), 'timestamp')


def types_plus_min(engine: Engine, data: List[list], base_value: Any, base_type: str):
    """
    Function to test all + and - operation combinations of data vs base, to make sure
    that all operations supported in python are supported in Bach and vice versa.
    Values returned by the DB as well as dtypes are checked.

    data is a list made up of lists, where the internal list are as follows:
    [ name, value, value_dtype, tuple(dtype_after_plus, dtype_after_min) ]
    - name is only for reference
    - value is the actual value in Python
    - value_dtype is the dtype in Bach for the value in Python
    - the tuple(dtype_after_plus, dtype_after_min) contains the dtypes that the resulting series should have.
    """
    bt = get_df_with_test_data(engine=engine, full_data_set=True)[['inhabitants']]

    base_name = 'base'
    bt[base_name] = base_value
    expected = [base_value]
    expected_types = [base_type]

    for name, value, value_type, (plus_type, min_type) in data:

        bt[name] = value
        expected.append(value)
        expected_types.append(value_type)

        try:
            # Do the python operation. Will raise TypeError is not supported
            expected.append(base_value + value)
        except TypeError as e:
            # Did we expected this operation to fail?
            assert(plus_type is None)

            with pytest.raises(TypeError):
                # it should also fail in Bach
                bt[base_name] + bt[name]
        else:
            # python operation finished successfully, now do the Bach one.
            bt[f'{base_name}_plus_{name}'] = bt[base_name] + bt[name]
            assert bt[f'{base_name}_plus_{name}'].dtype == plus_type

        try:
            # Do the python operation. Will raise TypeError is not supported
            expected.append(base_value - value)
        except TypeError as e:
            # Did we expected this operation to fail?
            assert(min_type is None)

            with pytest.raises(TypeError):
                # it should also fail in Bach
                bt[base_name] - bt[name]
        else:
            # python operation finished successfully, now do the Bach one.
            bt[f'{base_name}_min_{name}'] = bt[base_name] - bt[name]
            assert bt[f'{base_name}_min_{name}'].dtype == min_type

    assert_equals_data(
        bt.sort_index()[:1],
        expected_columns=list(bt.all_series.keys()),
        expected_data=[
            [1, 93485, *expected],
        ],
        use_to_pandas=True,
    )
    return bt, expected, expected_types