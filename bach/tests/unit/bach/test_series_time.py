"""
Copyright 2022 Objectiv B.V.
"""
import datetime

import numpy
import pytest

from bach import SeriesTime
from bach.expression import Expression


@pytest.mark.skip_bigquery('Athena specific test; test_supported_value_to_literal() below covers BigQuery')
@pytest.mark.skip_postgres('Athena specific test; test_supported_value_to_literal() below covers Postgres')
def test_supported_value_to_literal_athena(dialect):
    def assert_call(value, expected_token_value: float):
        result = SeriesTime.supported_value_to_literal(dialect=dialect, value=value, dtype='time')
        assert result == Expression.string_value(str(expected_token_value))

    # ## time
    assert_call(datetime.time(13, 37, 1, 23), 49021.000023)
    assert_call(datetime.time(1, 2, 3, 00),   3723.)
    assert_call(datetime.time(7, 7, 7, 7),    25627.000007)

    # ## datetime
    assert_call(datetime.datetime(1999, 1, 15, 13, 37, 1, 23), 49021.000023)
    assert_call(datetime.datetime(1969, 12, 31, 1, 2, 3, 00),  3723.)
    assert_call(datetime.datetime(2050, 7, 7, 7, 7, 7, 7),     25627.000007)

    # TODO: datetime with timezone set

    # ## np.datetime64
    assert_call(numpy.datetime64('2022-01-01 12:34:56.7800'),                      45296.78)
    assert_call(numpy.datetime64('2022-01-03'),                                          0.)
    assert_call(numpy.datetime64('1995-03-31 01:33:37.123456'),                 5617.123456)
    # datetime64 objects with differing precision. We only support up to milliseconds
    assert_call(numpy.datetime64('1995-03-31 01:33:37.1234567'),                5617.123456)
    assert_call(numpy.datetime64('1995-03-31 01:33:37.123456789012', 's'),      5617.)
    assert_call(numpy.datetime64('1995-03-31 01:33:37.123456789012', 'ms'),     5617.123)
    assert_call(numpy.datetime64('1995-03-31 01:33:37.123456789012', 'us'),     5617.123456)
    assert_call(numpy.datetime64('1995-03-31 01:33:37.123456789012', 'ns'),     5617.123456)
    # rounding can be a bit unexpected because of limited precision, therefore we always truncate excess precision
    assert_call(numpy.datetime64('1995-03-31 01:33:37.123456001', 'ns'),        5617.123456)
    assert_call(numpy.datetime64('1995-03-31 01:33:37.123456499', 'ns'),        5617.123456)
    assert_call(numpy.datetime64('1995-03-31 01:33:37.123456500', 'ns'),        5617.123456)
    assert_call(numpy.datetime64('1995-03-31 01:33:37.123456569', 'ns'),        5617.123456)
    assert_call(numpy.datetime64('1995-03-31 01:33:37.123456999', 'ns'),        5617.123456)

    # Special case: Not-a-Time will be represented as NULL
    nat = numpy.datetime64('NaT')
    dtype = 'time'
    assert SeriesTime.supported_value_to_literal(dialect, nat, dtype) == Expression.construct('NULL')

    # ## strings
    assert_call('2022-01-01 12:34:56.7800',    45296.78)
    assert_call('1995-03-31 01:33:37.123456',  5617.123456)
    assert_call('1999-12-31 23:59:59',         86399.)
    assert_call('1999-12-31 23:59',            86340.)
    assert_call('2022-01-03',                  0.)

    # ## None
    assert SeriesTime.supported_value_to_literal(dialect, None, dtype) == Expression.construct('NULL')


@pytest.mark.skip_athena('Athena is skipped because time values are represented with floats.')
def test_supported_value_to_literal(dialect):
    def assert_call(value, expected_token_value: str):
        result = SeriesTime.supported_value_to_literal(dialect=dialect, value=value, dtype='time')
        assert result == Expression.string_value(expected_token_value)

    # ## time
    assert_call(datetime.time(13, 37, 1, 23), '13:37:01.000023')
    assert_call(datetime.time(1, 2, 3, 00),   '01:02:03.000000')
    assert_call(datetime.time(7, 7, 7, 7),    '07:07:07.000007')

    # ## datetime
    assert_call(datetime.datetime(1999, 1, 15, 13, 37, 1, 23), '13:37:01.000023')
    assert_call(datetime.datetime(1969, 12, 31, 1, 2, 3, 00),  '01:02:03.000000')
    assert_call(datetime.datetime(2050, 7, 7, 7, 7, 7, 7),     '07:07:07.000007')

    # TODO: datetime with timezone set

    # ## np.datetime64
    assert_call(numpy.datetime64('2022-01-01 12:34:56.7800'),                   '12:34:56.780000')
    assert_call(numpy.datetime64('2022-01-03'),                                 '00:00:00.000000')
    assert_call(numpy.datetime64('1995-03-31 01:33:37.123456'),                 '01:33:37.123456')
    # datetime64 objects with differing precision. We only support up to milliseconds
    assert_call(numpy.datetime64('1995-03-31 01:33:37.1234567'),                '01:33:37.123456')
    assert_call(numpy.datetime64('1995-03-31 01:33:37.123456789012', 's'),      '01:33:37.000000')
    assert_call(numpy.datetime64('1995-03-31 01:33:37.123456789012', 'ms'),     '01:33:37.123000')
    assert_call(numpy.datetime64('1995-03-31 01:33:37.123456789012', 'us'),     '01:33:37.123456')
    assert_call(numpy.datetime64('1995-03-31 01:33:37.123456789012', 'ns'),     '01:33:37.123456')
    # rounding can be a bit unexpected because of limited precision, therefore we always truncate excess precision
    assert_call(numpy.datetime64('1995-03-31 01:33:37.123456001', 'ns'),        '01:33:37.123456')
    assert_call(numpy.datetime64('1995-03-31 01:33:37.123456499', 'ns'),        '01:33:37.123456')
    assert_call(numpy.datetime64('1995-03-31 01:33:37.123456500', 'ns'),        '01:33:37.123456')
    assert_call(numpy.datetime64('1995-03-31 01:33:37.123456569', 'ns'),        '01:33:37.123456')
    assert_call(numpy.datetime64('1995-03-31 01:33:37.123456999', 'ns'),        '01:33:37.123456')

    # Special case: Not-a-Time will be represented as NULL
    nat = numpy.datetime64('NaT')
    dtype = 'time'
    assert SeriesTime.supported_value_to_literal(dialect, nat, dtype) == Expression.construct('NULL')

    # ## strings
    assert_call('2022-01-01 12:34:56.7800',    '12:34:56.780000')
    assert_call('1995-03-31 01:33:37.123456',  '01:33:37.123456')
    assert_call('1999-12-31 23:59:59',         '23:59:59.000000')
    assert_call('1999-12-31 23:59',            '23:59:00.000000')
    assert_call('2022-01-03',                  '00:00:00.000000')

    # ## None
    assert SeriesTime.supported_value_to_literal(dialect, None, dtype) == Expression.construct('NULL')


def test_supported_value_to_literal_str_non_happy_path(dialect):
    dtype = 'timestamp'
    with pytest.raises(ValueError, match=r'Not a valid string literal: .* for time'):
        SeriesTime.supported_value_to_literal(dialect, 'aa:bb', dtype)

    with pytest.raises(ValueError, match=r'Not a valid string literal: .* for time'):
        SeriesTime.supported_value_to_literal(dialect, '12:13:0111', dtype)

    with pytest.raises(ValueError, match=r'Not a valid string literal: .* for time'):
        SeriesTime.supported_value_to_literal(dialect, '2:1300', dtype)
