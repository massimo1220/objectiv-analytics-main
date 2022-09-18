"""
Copyright 2021 Objectiv B.V.
"""
import datetime

import pandas as pd
import pytest

from bach import SeriesDate, DataFrame
from tests.functional.bach.test_data_and_utils import assert_equals_data,\
    assert_postgres_type, get_df_with_test_data, get_df_with_food_data
from tests.functional.bach.test_series_timestamp import types_plus_min

from bach.series.utils.datetime_formats import _C_STANDARD_CODES_X_POSTGRES_DATE_CODES, \
    CODES_SUPPORTED_IN_ALL_DIALECTS, STRINGS_SUPPORTED_IN_ALL_DIALECTS


@pytest.mark.parametrize("asstring", [True, False])
def test_date_comparator(asstring: bool, engine):
    mt = get_df_with_food_data(engine)[['date']]

    # import code has no means to distinguish between date and timestamp
    mt['date'] = mt['date'].astype('date')

    assert_postgres_type(mt['date'], 'date', SeriesDate)

    from datetime import date
    dt = date(2021, 5, 4)

    if asstring:
        dt = str(dt)

    mt['eq'] = mt['date'] == dt
    mt['gte'] = mt['date'] >= dt
    mt['gt'] = mt['date'] > dt
    mt['lte'] = mt['date'] <= dt
    mt['lt'] = mt['date'] < dt

    result = mt[['eq', 'gte', 'gt', 'lte', 'lt']]
    assert_equals_data(
        result,
        expected_columns=['_index_skating_order', 'eq', 'gte', 'gt', 'lte', 'lt'],
        expected_data=[
            [1, False, False, False, True, True],
            [2, True, True, False, True, False],
            [4, False, True, True, False, False]
        ]
    )


def test_date_format(engine, recwarn):
    timestamp = datetime.datetime(2021, 5, 3, 11, 28, 36, 388000)
    date = datetime.date(2022, 1, 1)

    pdf = pd.DataFrame({'timestamp_series': [timestamp], 'date_series': [date]})
    df = DataFrame.from_pandas(engine=engine, df=pdf, convert_objects=True).reset_index(drop=True)

    # Create format string that contains all codes that we claim to support.
    # This string will looks like: %%a: %a | %%b: %b | %%c: %c | ...
    format_str_all_supported_codes = ' | '.join(
        f'{c[1].replace("%", "%%")}: {c}'
        for c in sorted(CODES_SUPPORTED_IN_ALL_DIALECTS)
    )
    # Create format string that contains all strings that we claim to support in addition to the codes above.
    format_str_all_supported_strings = ' | '.join(STRINGS_SUPPORTED_IN_ALL_DIALECTS)

    all_formats = [
        # tuple, types: (str, bool). Content: format, whether the format should raise a warning
        ('Year: %Y', False),
        ('%Y', False),
        ('%y%Y', False),
        ('%Y-%m-%d', False),
        ('%Y%m%d-%Y%m-%m%d-%d', False),
        ('%Y%m-%d%d', False),
        ('%Y%Y%Y', False),
        ('%Y-%%%m-%d', False),
        ('abc %Y def%', True),
        ('"abc" %Y "def"%', True),  # % is not a supported code, should use %%
        ('HH24:MI:SS MS', False),
        ('%H:%M:%S.%f', False),
        # non-existing codes:
        ('%q %1 %_', True),
        # all codes that we claim to support for all databases
        (format_str_all_supported_codes, False),
        (format_str_all_supported_strings, False),
    ]

    for idx, fmt_tuple in enumerate(all_formats):
        fmt, expected_warning = fmt_tuple
        with pytest.warns(None) as record:
            df[f'date_f{idx}'] = df['date_series'].dt.strftime(fmt)
            df[f'timestamp_f{idx}'] = df['timestamp_series'].dt.strftime(fmt)
        assert_msg = f'{fmt_tuple}, expected warning: {expected_warning}, num warning: {len(record)}'
        assert (len(record) > 0) == expected_warning, assert_msg
    expected_columns = df.columns[2:]

    assert_equals_data(
        df[expected_columns],
        expected_columns=expected_columns,
        expected_data=[
            [
                'Year: 2022', 'Year: 2021',
                '2022', '2021',
                '222022', '212021',
                '2022-01-01', '2021-05-03',
                '20220101-202201-0101-01', '20210503-202105-0503-03',
                '202201-0101', '202105-0303',
                '202220222022', '202120212021',
                '2022-%01-01', '2021-%05-03',
                'abc 2022 def%', 'abc 2021 def%',
                '"abc" 2022 "def"%', '"abc" 2021 "def"%',
                'HH24:MI:SS MS', 'HH24:MI:SS MS',
                '00:00:00.000000', '11:28:36.388000',
                '%q %1 %_', '%q %1 %_',
                '%: % | A: Saturday | B: January | F: 2022-01-01 | H: 00 | I: 12 | M: 00 | R: 00:00 | S: 00 | T: 00:00:00 | Y: 2022 | a: Sat | b: Jan | d: 01 | j: 001 | m: 01 | y: 22',
                '%: % | A: Monday | B: May | F: 2021-05-03 | H: 11 | I: 11 | M: 28 | R: 11:28 | S: 36 | T: 11:28:36 | Y: 2021 | a: Mon | b: May | d: 03 | j: 123 | m: 05 | y: 21',
                '00.000000', '36.388000'
            ],
        ],
    )


@pytest.mark.skip_bigquery('Postgres specific test')
@pytest.mark.skip_athena('Postgres specific test')
def test_date_format_all_supported_pg_codes(engine, recwarn):
    # We use recwarn here, because some of the format codes we support on Postgres are not supported on other
    # databases. Those format codes will raise a warning.

    timestamp = datetime.datetime(2021, 5, 3, 11, 28, 36, 388000, tzinfo=datetime.timezone.utc)
    pdf = pd.DataFrame({'timestamp_series': [timestamp]})
    df = DataFrame.from_pandas(engine=engine, df=pdf, convert_objects=True).reset_index(drop=True)

    for c_code in _C_STANDARD_CODES_X_POSTGRES_DATE_CODES.keys():
        # strrftime does not support quarter, and currently we are not considering timezone info
        if c_code in ('%Q', '%z', '%Z'):
            continue

        df[c_code] = df['timestamp_series'].dt.strftime(c_code)
        pdf[c_code] = pdf['timestamp_series'].dt.strftime(c_code)

    pdf['%w'] = (pdf['%w'].astype(int) + 1).astype(str)  # weekday number starts from 1 in Postgres
    # datetime divides year by 100 and truncates integral part, postgres considers '2001' as start of 21st century
    pdf['%C'] = '21'
    pd.testing.assert_frame_equal(pdf, df.to_pandas(), check_dtype=False)
    assert len(recwarn) > 0


def test_date_trunc(engine):
    mt = get_df_with_food_data(engine)
    mt['date'] = mt['date'].astype('date')

    result = mt.copy()
    series_x_date_parts = {
        'moment': [
            'second',
            'minute',
            'hour',
            'day',
            'week',
        ],
        'date': [
            'month',
            'quarter',
            'year',
        ]
    }
    for series, date_parts in series_x_date_parts.items():
        for dp in date_parts:
            col = f'{series}_{dp}'
            result[col] = mt[series].dt.date_trunc(dp)

    expected_columns = [
        '_index_skating_order',
        'moment_second', 'moment_minute', 'moment_hour', 'moment_day', 'moment_week',
        'date_month', 'date_quarter', 'date_year',
    ]

    from datetime import date
    expected_data = [
        [
            1,
            datetime.datetime(2021, 5, 3, 11, 28, 36),
            datetime.datetime(2021, 5, 3, 11, 28),
            datetime.datetime(2021, 5, 3, 11),
            datetime.datetime(2021, 5, 3),
            datetime.datetime(2021, 5, 3),
            date(2021, 5, 1),
            date(2021, 4, 1),
            date(2021, 1, 1),
        ],
        [
            2,
            datetime.datetime(2021, 5, 4, 23, 28, 36),
            datetime.datetime(2021, 5, 4, 23, 28),
            datetime.datetime(2021, 5, 4, 23),
            datetime.datetime(2021, 5, 4),
            datetime.datetime(2021, 5, 3),
            date(2021, 5, 1),
            date(2021, 4, 1),
            date(2021, 1, 1),
        ],
        [
            4,
            datetime.datetime(2022, 5, 3, 14, 13, 13),
            datetime.datetime(2022, 5, 3, 14, 13),
            datetime.datetime(2022, 5, 3, 14),
            datetime.datetime(2022, 5, 3),
            datetime.datetime(2022, 5, 2),
            date(2022, 5, 1),
            date(2022, 4, 1),
            date(2022, 1, 1),
        ],
    ]
    assert_equals_data(
        result[expected_columns[1:]],
        expected_columns=expected_columns,
        expected_data=expected_data,
        use_to_pandas=True,
    )

    with pytest.raises(ValueError, match='some_wrong_format format is not available.'):
        mt.date.dt.date_trunc('some_wrong_format')

    # not supported series type
    mt['time'] = datetime.time(21, 10, 5)
    with pytest.raises(ValueError, match="<class 'bach.series.series_datetime.SeriesTime'>"
                                         " type is not supported."):
        mt['time'].dt.date_trunc('hour')


def test_date_arithmetic(engine):
    data = [
        ['d', datetime.date(2020, 3, 11), 'date', (None, 'timedelta')],
        ['t', datetime.time(23, 11, 5), 'time', (None, None)],
        ['td', datetime.timedelta(days=321, seconds=9877), 'timedelta', ('date', 'date')],
        ['dt', datetime.datetime(2021, 5, 3, 11, 28, 36, 388000), 'timestamp', (None, None)]
    ]
    types_plus_min(engine, data, datetime.date(2021, 7, 23), 'date')


def test_to_pandas(engine):
    bt = get_df_with_test_data(engine)
    bt['d'] = datetime.date(2020, 3, 11)
    pdf_result = bt.to_pandas()
    assert pdf_result[['d']].to_numpy()[0] == [datetime.date(2020, 3, 11)]
