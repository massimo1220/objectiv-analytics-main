"""
Copyright 2021 Objectiv B.V.
"""
import datetime
from abc import ABC
from enum import Enum
from typing import Union, cast, List, Tuple, Optional, Any

import numpy
import pandas
from sqlalchemy.engine import Dialect

from bach import DataFrame
from bach.series import Series, SeriesString, SeriesBoolean, SeriesFloat64, SeriesInt64
from bach.expression import Expression, join_expressions, StringValueToken
from bach.series.series import WrappedPartition, ToPandasInfo
from bach.series.utils.datetime_formats import parse_c_standard_code_to_postgres_code, \
    parse_c_code_to_bigquery_code, parse_c_code_to_athena_code, warn_non_supported_format_codes
from bach.types import DtypeOrAlias, StructuredDtype
from sql_models.constants import DBDialect
from sql_models.util import is_postgres, is_bigquery, DatabaseNotSupportedException, is_athena


class DatePart(str, Enum):
    DAY = 'days'
    HOUR = 'hours'
    MINUTE = 'minutes'
    SECOND = 'seconds'
    MILLISECOND = 'milliseconds'
    MICROSECOND = 'microseconds'


# conversions for date parts to seconds
# when adjusting intervals, 30-day time periods are represented as months
# BigQuery seems to follow Postgres threshold
# https://www.postgresql.org/docs/current/functions-datetime.html#:~:text=justify_days%20(%20interval%20)%20%E2%86%92%20interval,mon%205%20days
# For example 395 days is equal to 1 year, 1 month and 5 days.
_TOTAL_SECONDS_PER_DATE_PART = {
    DatePart.DAY:  24 * 60 * 60,
    DatePart.HOUR: 60 * 60,
    DatePart.MINUTE: 60,
    DatePart.SECOND: 1,
    DatePart.MILLISECOND: 1e-3,
    DatePart.MICROSECOND: 1e-6,
}

AllSupportedDateTimeTypes = Union[
    datetime.datetime,
    numpy.datetime64,
    datetime.date,
    str,
    None,
    datetime.timedelta,
    numpy.timedelta64,
]


class DateTimeOperation:
    def __init__(self, series: 'SeriesAbstractDateTime'):
        self._series = series

    def strftime(self, format_str: str) -> SeriesString:
        """
        Allow formatting of this Series (to a string type).

        :param format_str: The format to apply to the date/time column. See Supported Format Codes below for
            more information on what is supported.

        :returns: a SeriesString containing the formatted date.

        **Supported Format Codes**

        A subset of the C standard format codes is supported. See the python documentation for the
        code semantics: https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes

        The subset of codes that are supported across all databases is:
            `%A`, `%B`, `%F`, `%H`, `%I`, `%M`, `%R`, `%S`, `%T`, `%Y`, `%a`, `%b`, `%d`, `%j`, `%m`, `%y`,
            `%%`

        Additionally one specific combination is supported: `%S.%f`

        **Example**

        .. code-block:: python

            df['year'] = df.some_date_series.dt.strftime('%Y')  # return year
            df['date'] = df.some_date_series.dt.strftime('%Y%m%d')  # return date
        """
        engine = self._series.engine
        series = self._series

        # Warn user if he is using non-supported format codes
        warn_non_supported_format_codes(format_str)

        if is_postgres(engine):
            parsed_format_str = parse_c_standard_code_to_postgres_code(format_str)
            expression = Expression.construct(
                'to_char({}, {})', series, Expression.string_value(parsed_format_str)
            )
        elif is_athena(engine):
            parsed_format_str = parse_c_code_to_athena_code(format_str)
            expression = Expression.construct(
                'date_format({}, {})', series, Expression.string_value(parsed_format_str)
            )
        elif is_bigquery(engine):
            # BigQuery will ignore some formatting codes when applied to a date.
            # For example, rather than returning '00' as value for '%H' (hour) it will return '%H'.
            # To avoid this problem, we convert to timestamp.
            series = cast(SeriesTimestamp, series.astype('timestamp'))

            parsed_format_str = parse_c_code_to_bigquery_code(format_str)
            expression = Expression.construct(
                'format_date({}, {})', Expression.string_value(parsed_format_str), series
            )
        else:
            raise DatabaseNotSupportedException(engine)

        str_series = series.copy_override_type(SeriesString).copy_override(expression=expression)
        return str_series

    def date_trunc(self, date_part: str) -> Series:
        """
        Truncates date value based on a specified date part.
        The value is always rounded to the beginning of date_part.

        This operation can be applied only on SeriesDate or SeriesTimestamp.

        :param date_part: Allowed values are 'second', 'minute',
            'hour', 'day', 'week', 'month', 'quarter', and 'year'.

        .. code-block:: python

            # return the date corresponding to the Monday of that week
            df['week'] = df.some_date_or_timestamp_series.dt.date_trunc('week')
            # return the first day of the quarter
            df['quarter'] = df.some_date_or_timestamp_series.dt.date_trunc('quarter')

        :returns: the truncated timestamp value with a granularity of date_part.

        """

        available_formats = ['second', 'minute', 'hour', 'day', 'week',
                             'month', 'quarter', 'year']
        if date_part not in available_formats:
            raise ValueError(f'{date_part} format is not available.')

        if not (isinstance(self._series, SeriesDate) or
                isinstance(self._series, SeriesTimestamp)):
            raise ValueError(f'{type(self._series)} type is not supported.')

        engine = self._series.engine

        # Truncating Postgres date type will include timezone in final value
        # therefore we should cast it into TIMESTAMP WITHOUT TIMEZONE
        _td_series = self._series.astype(SeriesTimestamp.dtype)
        if is_postgres(engine) or is_athena(engine):
            expression = Expression.construct(
                'date_trunc({}, {})',
                Expression.string_value(date_part),
                _td_series,
            )
        elif is_bigquery(engine):
            if date_part == 'week':
                date_part = 'week(monday)'
            expression = Expression.construct(
                'timestamp_trunc({}, {})',
                _td_series,
                Expression.raw(date_part),
            )
        else:
            raise DatabaseNotSupportedException(engine)

        return _td_series.copy_override(expression=expression)


class TimedeltaOperation(DateTimeOperation):
    def _get_conversion_df(self) -> 'DataFrame':
        """
        generates a dataframe containing the amounts of seconds a supported date part has.
        """
        from bach import DataFrame
        conversion_df = pandas.DataFrame(
            data=[
                {
                    self._format_converted_series_name(dp): ts
                    for dp, ts in _TOTAL_SECONDS_PER_DATE_PART.items()
                },
            ]
        )
        convert_df = DataFrame.from_pandas(df=conversion_df, engine=self._series.engine, convert_objects=True)
        return convert_df.reset_index(drop=True)

    @staticmethod
    def _format_converted_series_name(date_part: DatePart) -> str:
        return f'_SECONDS_IN_{date_part.name}'.lower()

    @property
    def components(self) -> DataFrame:
        """
        :returns: a DataFrame containing all date parts from the timedelta.
        """
        df = self.total_seconds.to_frame()
        df = df.merge(self._get_conversion_df(), how='cross')

        # justifies total seconds into the units of each date component
        # after adjustment, it converts it back into seconds
        for date_part in DatePart:
            converted_series_name = self._format_converted_series_name(DatePart(date_part))
            df[f'ts_{date_part}'] = df['total_seconds'] // df[converted_series_name]
            df[f'ts_{date_part}'] *= df[converted_series_name]

        # materialize to avoid complex subquery
        df = df.materialize(node_name='justified_date_components')

        components_series_names = []
        prev_ts = ''

        # extract actual date component from justified seconds
        # by getting the difference between current and previous components
        # this helps on normalizing negative time deltas and have only negative values
        # in days.
        for date_part in DatePart:
            converted_series_name = self._format_converted_series_name(DatePart(date_part))

            component_name = f'{date_part}'
            current_ts = f'ts_{date_part}'

            if not prev_ts:
                df[component_name] = df[current_ts] / df[converted_series_name]
            else:
                df[component_name] = (df[current_ts] - df[prev_ts]) / df[converted_series_name]

            df[component_name] = cast(SeriesFloat64, df[component_name]).round(decimals=0)

            components_series_names.append(component_name)
            prev_ts = current_ts

        return df[components_series_names].astype('int64')

    @property
    def days(self) -> SeriesInt64:
        """
        converts total seconds into days and returns only the integral part of the result
        """
        day_series = self.total_seconds // _TOTAL_SECONDS_PER_DATE_PART[DatePart.DAY]

        day_series = day_series.astype('int64')
        return (
            day_series
            .copy_override_type(SeriesInt64)
            .copy_override(name='days')
        )

    @property
    def seconds(self) -> SeriesInt64:
        """
        removes days from total seconds (self.total_seconds % _SECONDS_IN_DAY)
        and returns only the integral part of the result
        """
        seconds_series = (self.total_seconds % _TOTAL_SECONDS_PER_DATE_PART[DatePart.DAY]) // 1

        seconds_series = seconds_series.astype('int64')
        return (
            seconds_series
            .copy_override_type(SeriesInt64)
            .copy_override(name='seconds')
        )

    @property
    def microseconds(self) -> SeriesInt64:
        """
        considers only the fractional part of the total seconds and converts it into microseconds
        """
        microseconds_series = (
            (self.total_seconds % 1) / _TOTAL_SECONDS_PER_DATE_PART[DatePart.MICROSECOND]
        )

        microseconds_series = microseconds_series.astype('int64')
        return (
            microseconds_series
            .copy_override_type(SeriesInt64)
            .copy_override(name='microseconds')
        )

    @property
    def total_seconds(self) -> SeriesFloat64:
        """
        returns the total amount of seconds in the interval

        .. note::
            Since Athena does not support interval types, series values are actually the total seconds.
        """
        expression = self._series.expression
        if is_postgres(self._series.engine):
            # extract(epoch from source) returns the total number of seconds in the interval
            expression = Expression.construct(f'extract(epoch from {{}})', self._series)
        elif is_bigquery(self._series.engine):
            # bq cannot extract epoch from interval
            expression = Expression.construct(
                (
                    f"UNIX_MICROS(CAST('1970-01-01' AS TIMESTAMP) + {{}}) "
                    f"* {_TOTAL_SECONDS_PER_DATE_PART[DatePart.MICROSECOND]}"
                ),
                self._series,
            )

        return (
            self._series
            .copy_override_type(SeriesFloat64)
            .copy_override(name='total_seconds', expression=expression)
        )


class SeriesAbstractDateTime(Series, ABC):
    """
    A Series that represents the generic date/time type and its specific operations. Selected arithmetic
    operations are accepted using the usual operators.

    **Date/Time Operations**

    On any of the subtypes, you can access date operations through the `dt` accessor.
    """

    # list of formats used for parsing string literals to date object supported by Series
    _VALID_DATE_TIME_FORMATS = [
        '%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y-%m-%d'
    ]

    # format used for all literals when casting them to this Series
    _FINAL_DATE_TIME_FORMAT = ''

    @property
    def dt(self) -> DateTimeOperation:
        """
        Get access to date operations.

        .. autoclass:: bach.series.series_datetime.DateTimeOperation
            :members:

        """
        return DateTimeOperation(self)

    @classmethod
    def dtype_to_expression(cls, dialect: Dialect, source_dtype: str, expression: Expression) -> Expression:
        if source_dtype == cls.dtype:
            return expression

        if source_dtype not in cls.supported_source_dtypes:
            raise ValueError(f'cannot convert {source_dtype} to {cls.dtype}')

        if expression.is_constant and source_dtype == 'string':
            return cls._constant_expression_to_dtype_expression(dialect, expression)

        return Expression.construct(f'cast({{}} as {cls.get_db_dtype(dialect)})', expression)

    def _comparator_operation(self, other, comparator,
                              other_dtypes=('timestamp', 'date', 'time', 'string'),
                              strict_other_dtypes=tuple()) -> 'SeriesBoolean':
        return super()._comparator_operation(
            other, comparator, other_dtypes, strict_other_dtypes=tuple(self.dtype)
        )

    @classmethod
    def _cast_and_round_to_date(cls, series: 'SeriesDate') -> 'Series':
        # Most of engines return timestamp in all cases were we expect date
        # Make sure we cast properly, and round similar to python datetime: add 12 hours and cast to date
        td_12_hours = datetime.timedelta(seconds=3600 * 12)
        series_12_hours = SeriesTimedelta.from_value(base=series, value=td_12_hours, name='tmp')
        expr_12_hours = series_12_hours.expression

        expr = "cast({} + {} as date)"

        # time intervals are not supported in athena, we need to use unix time instead
        if is_athena(series.engine):
            expr = "cast(from_unixtime(to_unixtime({}) + {}) as date)"

        return series.copy_override(
            expression=Expression.construct(expr, series, expr_12_hours)
        )

    @classmethod
    def _get_date_format_for_literal_value(cls, value: str) -> str:
        """
        Returns the correct date format for a string literal. If value has a non-supported format,
        an exception will be raised.
        """
        for str_format in cls._VALID_DATE_TIME_FORMATS:
            try:
                datetime.datetime.strptime(value, str_format)
            except ValueError:
                continue
            else:
                return str_format

        raise ValueError(
            f'Not a valid string literal: {value} for {cls.dtype} dtype.'
            f'Supported formats: {cls._VALID_DATE_TIME_FORMATS}'
        )

    @classmethod
    def _constant_expression_to_dtype_expression(cls, dialect, expression) -> Expression:
        """
        Parses constant expression to respective dtype expression. Child classes must be
        in charge of validating if string literals have the expected date format.
        """
        # check if string literal has correct format
        literal_expr_tokens = []
        for token in expression.data:
            if not isinstance(token, StringValueToken):
                literal_expr_tokens.append(token)
                continue

            val = token.value if token.value != 'NULL' else None
            val_to_lit_expr = cls.supported_value_to_literal(dialect, val, cls.dtype)
            literal_expr_tokens.append(val_to_lit_expr)
        return cls.supported_literal_to_expression(dialect, Expression(literal_expr_tokens))

    @classmethod
    def supported_value_to_literal(
        cls,
        dialect: Dialect,
        value: AllSupportedDateTimeTypes,
        dtype: StructuredDtype
    ) -> Expression:
        if value is None:
            return Expression.raw('NULL')

        dt_value: Union[datetime.datetime, datetime.date, datetime.time, None] = None

        if isinstance(value, str):
            # get the right date format of the string
            str_format = cls._get_date_format_for_literal_value(value)
            dt_value = datetime.datetime.strptime(value, str_format)

        if isinstance(value, numpy.datetime64):
            if numpy.isnat(value):
                return Expression.raw('NULL')

            dt_value = _convert_numpy_datetime_to_utc_datetime(value)

        if isinstance(value, (datetime.datetime, datetime.date, datetime.time)):
            dt_value = value

        if not dt_value or not isinstance(value, cls.supported_value_types):
            raise ValueError(f'Not a valid {cls.dtype} literal: {value}')

        str_value = dt_value.strftime(cls._FINAL_DATE_TIME_FORMAT)
        return Expression.string_value(str_value)


def dt_strip_timezone(value: Optional[datetime.datetime]) -> Optional[datetime.datetime]:
    if value is None:
        return None
    return value.replace(tzinfo=None)


class SeriesTimestamp(SeriesAbstractDateTime):
    """
    A Series that represents the timestamp/datetime type and its specific operations.

    Timestamps are assumed to be in UTC, or without a timezone, both cases are treated the same.
    These timestamps have a microsecond precision at best, in contrast to numpy's datetime64 which supports
    up to attoseconds precision.

    **Database support and types**

    * Postgres: utilizes the 'timestamp without time zone' database type.
    * BigQuery: utilizes the 'TIMESTAMP' database type.
    """
    dtype = 'timestamp'
    dtype_aliases = ('datetime64', 'datetime64[ns]', numpy.datetime64)
    supported_db_dtype = {
        DBDialect.POSTGRES: 'timestamp without time zone',
        DBDialect.BIGQUERY: 'TIMESTAMP',
        DBDialect.ATHENA: 'timestamp',
    }
    supported_value_types = (datetime.datetime, numpy.datetime64, datetime.date, str)

    supported_source_dtypes = ('string', 'date',)
    _FINAL_DATE_TIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f'

    @classmethod
    def supported_literal_to_expression(cls, dialect: Dialect, literal: Expression) -> Expression:
        if not is_athena(dialect):
            return super().supported_literal_to_expression(dialect, literal)

        # Athena will raise exceptions if literal has incorrect timestamp format
        return Expression.construct("date_parse({}, '%Y-%m-%d %H:%i:%S.%f')", literal)

    def to_pandas_info(self) -> Optional['ToPandasInfo']:
        if is_postgres(self.engine) or is_athena(self.engine):
            return ToPandasInfo('datetime64[ns]', None)

        if is_bigquery(self.engine):
            return ToPandasInfo('datetime64[ns, UTC]', dt_strip_timezone)
        return None

    def __add__(self, other) -> 'Series':
        _self = self.copy()
        fmt_str = '({}) + ({})'
        if is_athena(self.engine):
            # convert timestamp to unixtime and cast result back to timestamp
            _self = self.copy_override(
                expression=Expression.construct('to_unixtime({})', self)
            )
            fmt_str = f'from_unixtime({fmt_str})'

        return _self._arithmetic_operation(other, 'add', fmt_str, other_dtypes=tuple(['timedelta']))

    def __sub__(self, other) -> 'Series':
        type_mapping = {
            'timedelta': 'timestamp',
            'timestamp': 'timedelta'
        }

        _self = self.copy()
        _other = other.copy()

        fmt_str = '({}) - ({})'
        if is_athena(self.engine):
            # since we represent intervals with float values, we should consider unix time values instead
            _self = self.copy_override(
                expression=Expression.construct('to_unixtime({})', self)
            )
            fmt_str = f'round({fmt_str}, 3)'
            if other.dtype == 'timestamp':
                _other = _other.copy_override(
                    expression=Expression.construct('to_unixtime({})', _other)
                )

            else:
                # need to cast back to timestamp if we are subtracting by a timedelta
                fmt_str = f'from_unixtime({fmt_str})'

        return _self._arithmetic_operation(
            _other,
            operation='sub',
            fmt_str=fmt_str,
            other_dtypes=tuple(type_mapping.keys()),
            dtype=type_mapping,
        )


class SeriesDate(SeriesAbstractDateTime):
    """
    A Series that represents the date type and its specific operations

    **Database support and types**

    * Postgres: utilizes the 'date' database type.
    * BigQuery: utilizes the 'DATE' database type.
    """
    dtype = 'date'
    dtype_aliases: Tuple[DtypeOrAlias, ...] = tuple()
    supported_db_dtype = {
        DBDialect.POSTGRES: 'date',
        DBDialect.BIGQUERY: 'DATE',
        DBDialect.ATHENA: 'date',
    }
    supported_value_types = (datetime.datetime, numpy.datetime64, datetime.date, str)

    supported_source_dtypes = ('string', 'timestamp',)
    _FINAL_DATE_TIME_FORMAT = '%Y-%m-%d'

    def __add__(self, other) -> 'Series':
        _self = self.astype('timestamp')
        _other = other.copy()

        result = _self + _other
        # current result is timestamp dtype, cast it back to date
        # (without explicitly casting db type, as time units are required for rounding)
        result = result.copy_override_type(SeriesDate)
        return self._cast_and_round_to_date(result)

    def __sub__(self, other) -> 'Series':
        # python will raise a TypeError when trying arithmetic operations
        # that are not date or timedelta type

        if other.dtype not in ('date', 'timedelta'):
            raise TypeError(f'arithmetic operation sub not supported for '
                            f'{self.__class__} and {other.__class__}')

        _self = self.astype('timestamp')
        _other = other.astype('timestamp') if other.dtype == 'date' else other.copy()

        result = _self - _other
        if other.dtype == 'date':
            # will return an interval
            return result

        # current result is timestamp dtype, cast it back to date
        # (without explicitly casting db type, as time units are required for rounding)
        result = result.copy_override_type(SeriesDate)
        return self._cast_and_round_to_date(result)


class SeriesTime(SeriesAbstractDateTime):
    """
    A Series that represents the date time and its specific operations


    **Database support and types**

    * Postgres: utilizes the 'time without time zone' database type.
    * BigQuery: utilizes the 'TIME' database type.
    * Athena: utilizes the 'double' database type. Storing the number of seconds since `00:00:00`.

    """
    dtype = 'time'
    dtype_aliases: Tuple[DtypeOrAlias, ...] = tuple()
    supported_db_dtype = {
        DBDialect.POSTGRES: 'time without time zone',
        DBDialect.BIGQUERY: 'TIME',
        # Athena supports time database type, however we decided to represent
        # time values as floats (total seconds) due to the following reasons:
        # 1. Athena does not support writing time values into tables
        # 2. Time values have till millisecond precision, using floats we can support till microseconds.
        DBDialect.ATHENA: None,
    }
    supported_value_types = (datetime.datetime, numpy.datetime64, datetime.time, str)
    supported_source_dtypes = ('string', 'timestamp, ')

    _VALID_DATE_TIME_FORMATS = SeriesAbstractDateTime._VALID_DATE_TIME_FORMATS + ['%H:%M:%S', '%H:%M:%S.%f']
    _FINAL_DATE_TIME_FORMAT = '%H:%M:%S.%f'

    @classmethod
    def get_db_dtype(cls, dialect: Dialect) -> Optional[str]:
        if is_athena(dialect):
            from bach.series import SeriesString
            return SeriesFloat64.get_db_dtype(dialect)
        return super().get_db_dtype(dialect)

    @classmethod
    def supported_literal_to_expression(cls, dialect: Dialect, literal: Expression) -> Expression:
        if is_postgres(dialect) or is_bigquery(dialect):
            return super().supported_literal_to_expression(dialect=dialect, literal=literal)
        if is_athena(dialect):
            from bach import SeriesString
            return SeriesFloat64.supported_literal_to_expression(dialect=dialect, literal=literal)
        raise DatabaseNotSupportedException(dialect)

    @classmethod
    def supported_value_to_literal(
        cls,
        dialect: Dialect,
        value: AllSupportedDateTimeTypes,
        dtype: StructuredDtype
    ) -> Expression:
        val_is_null = value is None or (isinstance(value, numpy.datetime64) and numpy.isnat(value))
        if not is_athena(dialect) or val_is_null:
            return super().supported_value_to_literal(dialect=dialect, value=value, dtype=dtype)

        dt_value: Union[datetime.datetime, datetime.date, datetime.time, None] = None

        if isinstance(value, str):
            # get the right date format of the string
            str_format = cls._get_date_format_for_literal_value(value)
            dt_value = datetime.datetime.strptime(value, str_format)

        if isinstance(value, numpy.datetime64):
            dt_value = _convert_numpy_datetime_to_utc_datetime(value)

        if isinstance(value, (datetime.datetime, datetime.date, datetime.time)):
            dt_value = value

        if not dt_value or not isinstance(value, cls.supported_value_types):
            raise ValueError(f'Not a valid {cls.dtype} literal: {value}')

        total_seconds = 0.
        if isinstance(dt_value, (datetime.datetime, datetime.time)):
            total_seconds = (
                dt_value.hour * _TOTAL_SECONDS_PER_DATE_PART[DatePart.HOUR]
                + dt_value.minute * _TOTAL_SECONDS_PER_DATE_PART[DatePart.MINUTE]
                + dt_value.second
                + dt_value.microsecond * _TOTAL_SECONDS_PER_DATE_PART[DatePart.MICROSECOND]
            )

        from bach.series import SeriesFloat64
        return SeriesFloat64.supported_value_to_literal(dialect, value=total_seconds, dtype='float64')

    def to_pandas_info(self) -> Optional[ToPandasInfo]:
        if is_athena(self.engine):
            return ToPandasInfo('object', self._parse_time_in_seconds_value_athena)
        return None

    @staticmethod
    def _parse_time_in_seconds_value_athena(value) -> Optional[datetime.time]:
        if value is None:
            return value

        hours_w_fract = value / _TOTAL_SECONDS_PER_DATE_PART[DatePart.HOUR]
        normalized_hours = int(hours_w_fract // 1)

        minutes_w_fract = (hours_w_fract - normalized_hours) * 60
        normalized_minutes = int(minutes_w_fract // 1)

        # round till milliseconds
        seconds_w_fract = round((minutes_w_fract - normalized_minutes) * 60, 6)
        normalized_seconds = int(seconds_w_fract // 1)
        return datetime.time(
            hour=normalized_hours,
            minute=normalized_minutes,
            second=normalized_seconds,
            microsecond=int(seconds_w_fract % 1 / _TOTAL_SECONDS_PER_DATE_PART[DatePart.MICROSECOND]),
        )

    # python supports no arithmetic on Time


class SeriesTimedelta(SeriesAbstractDateTime):
    """
    A Series that represents the timedelta type and its specific operations

    **Database support and types**

    * Postgres: utilizes the 'interval' database type.
    * BigQuery: utilizes the 'interval' database type.
    * Athena: utilizes the 'double' database type.
    """

    dtype = 'timedelta'
    dtype_aliases = ('interval',)
    supported_db_dtype = {
        DBDialect.POSTGRES: 'interval',
        DBDialect.BIGQUERY: 'INTERVAL',
        # Athena supports interval database type, however we decided to represent
        # timedelta values as floats (total seconds) as Athena does not support writing
        # interval values into tables
        DBDialect.ATHENA: None,
    }
    supported_value_types = (datetime.timedelta, numpy.timedelta64, str)
    supported_source_dtypes = ('string',)

    @classmethod
    def get_db_dtype(cls, dialect: Dialect) -> Optional[str]:
        if is_athena(dialect):
            return SeriesFloat64.get_db_dtype(dialect)
        return super().get_db_dtype(dialect)

    @classmethod
    def supported_value_to_literal(
        cls,
        dialect: Dialect,
        value: AllSupportedDateTimeTypes,
        dtype: StructuredDtype
    ) -> Expression:
        if value is None:
            return Expression.construct('NULL')

        if isinstance(value, cls.supported_value_types):
            # pandas.Timedelta checks already that the string has the correct format
            # round it up to microseconds precision in order to avoid problems with BigQuery
            # pandas by default uses nanoseconds precision
            value_td = pandas.Timedelta(value).round(freq='us')

            if value_td is pandas.NaT:
                return Expression.construct('NULL')

            if is_athena(dialect):
                # athena does not support interval type, therefore we need to use epoch instead
                from bach.series import SeriesFloat64
                return SeriesFloat64.supported_value_to_literal(
                    dialect, value=value_td.total_seconds(), dtype='float64'
                )

            # interval values in iso format are allowed in SQL (both BQ and PG)
            # https://www.postgresql.org/docs/8.4/datatype-datetime.html#:~:text=interval%20values%20can%20also%20be%20written%20as%20iso%208601%20time%20intervals%2C
            return Expression.string_value(value_td.isoformat())

        raise ValueError(f'Not a valid {cls.dtype} literal: {value}')

    def to_pandas_info(self) -> Optional[ToPandasInfo]:
        if is_bigquery(self.engine):
            return ToPandasInfo(dtype='object', function=self._parse_interval_bigquery)

        if is_athena(self.engine):
            return ToPandasInfo(dtype='object', function=lambda value: pandas.Timedelta(seconds=value))

        return None

    def _parse_interval_bigquery(self, value: Optional[Any]) -> Optional[pandas.Timedelta]:
        if value is None:
            return None

        # BigQuery returns a MonthDayNano object
        # we need to normalize months to days (1 month == 30 day period)
        return pandas.Timedelta(
            days=value.days + value.months * 30,
            nanoseconds=value.nanoseconds,
        )

    def _comparator_operation(self, other, comparator,
                              other_dtypes=('timedelta', 'string'),
                              strict_other_dtypes=tuple()) -> SeriesBoolean:
        return super()._comparator_operation(other, comparator, other_dtypes, strict_other_dtypes)

    def __add__(self, other) -> 'Series':
        if isinstance(other, datetime.timedelta) or other.dtype == 'timedelta':
            return self._arithmetic_operation(
                other,
                'add',
                '({}) + ({})',
                other_dtypes=('timedelta', ),
                dtype={'timedelta': 'timedelta'}
            )
        # inverse the operands, so we call SeriesDate or SeriesTimestamp __add__
        return other + self

    def __sub__(self, other) -> 'Series':
        type_mapping = {
            'timedelta': 'timedelta',
        }
        return self._arithmetic_operation(other, 'sub', '({}) - ({})',
                                          other_dtypes=tuple(type_mapping.keys()),
                                          dtype=type_mapping)

    def __mul__(self, other) -> 'Series':
        return self._arithmetic_operation(other, 'mul', '({}) * ({})', other_dtypes=('int64', 'float64'))

    def __truediv__(self, other) -> 'Series':
        return self._arithmetic_operation(other, 'div', '({}) / ({})', other_dtypes=('int64', 'float64'))

    @property
    def dt(self) -> TimedeltaOperation:
        """
        Get access to date operations.

        .. autoclass:: bach.series.series_datetime.TimedeltaOperation
            :members:

        """
        return TimedeltaOperation(self)

    def sum(self, partition: WrappedPartition = None,
            skipna: bool = True, min_count: int = None) -> 'SeriesTimedelta':
        """
        :meta private:
        """
        result = self._derived_agg_func(
            partition=partition,
            expression='sum',
            skipna=skipna,
            min_count=min_count
        )
        return result.copy_override_type(SeriesTimedelta)

    def mean(self, partition: WrappedPartition = None, skipna: bool = True) -> 'SeriesTimedelta':
        """
        :meta private:
        """
        result = self._derived_agg_func(
            partition=partition,
            expression='avg',
            skipna=skipna
        )
        result = result.copy_override_type(SeriesTimedelta)

        if is_bigquery(self.engine):
            result = result._remove_nano_precision_bigquery()

        return result

    def _remove_nano_precision_bigquery(self) -> 'SeriesTimedelta':
        """
        Helper function that removes nano-precision from intervals.
        """
        series = self.copy()
        # https://cloud.google.com/bigquery/docs/reference/standard-sql/data-types#interval_type
        _BQ_INTERVAL_FORMAT = '%d-%d %d %d:%d:%d.%06.0f'
        _BQ_SUPPORTED_INTERVAL_PARTS = [
            'YEAR', 'MONTH', 'DAY', 'HOUR', 'MINUTE', 'SECOND'
        ]

        # aggregating intervals by average might generate a result with
        # nano-precision, which is not supported by BigQuery TimeStamps
        # therefore we need to make sure we always generate values up to
        # microseconds precision
        # https://cloud.google.com/bigquery/docs/reference/standard-sql/data-types#timestamp_type
        all_extracted_parts_expr = [
            Expression.construct(f'EXTRACT({date_part} FROM {{}})', series)
            for date_part in _BQ_SUPPORTED_INTERVAL_PARTS
        ]
        # convert nanoseconds to microseconds
        all_extracted_parts_expr.append(
            Expression.construct(f'EXTRACT(NANOSECOND FROM {{}}) / 1000', series)
        )
        format_arguments_expr = join_expressions(all_extracted_parts_expr)

        # All parts will create a string with following format
        # '%d-%d %d %d:%d:%d.%06.0f'
        # where the first 6 digits are date parts from YEAR to SECOND
        # Format specifier %06.0f will format fractional part of seconds with maximum width of 6 digits
        # for example:
        # nanoseconds = 1142857, converting them into microseconds is 1142.857
        # when applying string formatting, the value will be rounded into 1143 (.0 precision)
        # and will be left padded by 2 leading zeros: 001143 (0 flag and 6 minimum width)
        # for more information:
        # https://cloud.google.com/bigquery/docs/reference/standard-sql/string_functions#format_string
        format_expr = Expression.construct(
            f'format({{}}, {{}})',
            Expression.string_value(_BQ_INTERVAL_FORMAT),
            format_arguments_expr,
        )
        return series.copy_override(
            expression=self.dtype_to_expression(
                self.engine, source_dtype='string', expression=format_expr,
            )
        )

    def quantile(
        self, partition: WrappedPartition = None, q: Union[float, List[float]] = 0.5,
    ) -> 'SeriesTimedelta':
        """
        When q is a float or len(q) == 1, the resultant series index will remain
        In case multiple quantiles are calculated, the resultant series index will have all calculated
        quantiles as index values.
        """
        from bach.quantile import calculate_quantiles

        if not is_bigquery(self.engine):
            return (
                calculate_quantiles(series=self.copy(), partition=partition, q=q)
                .copy_override_type(SeriesTimedelta)
            )

        result = calculate_quantiles(series=self.dt.total_seconds, partition=partition, q=q)
        # result must be a timedelta
        return self._convert_total_seconds_to_timedelta(result.copy_override_type(SeriesFloat64))

    def mode(self, partition: WrappedPartition = None, skipna: bool = True) -> 'SeriesTimedelta':
        if not is_bigquery(self.engine):
            return super().mode(partition, skipna)

        # APPROX_TOP_COUNT does not support INTERVALS. So, we should calculate the mode based
        # on the total seconds
        total_seconds_mode = self.dt.total_seconds.mode(partition, skipna)
        return self._convert_total_seconds_to_timedelta(total_seconds_mode)

    def _convert_total_seconds_to_timedelta(
        self, total_seconds_series: 'SeriesFloat64',
    ) -> 'SeriesTimedelta':
        """
        helper function for converting series representing total seconds (epoch) to timedelta series.

        returns a SeriesTimedelta
        """

        # convert total seconds into microseconds
        # since TIMESTAMP_SECONDS accepts only integers, therefore
        # microseconds will be lost due to rounding
        total_microseconds_series = (
            total_seconds_series / _TOTAL_SECONDS_PER_DATE_PART[DatePart.MICROSECOND]
        )
        result = total_microseconds_series.copy_override(
            expression=Expression.construct(
                f"TIMESTAMP_MICROS({{}}) - CAST('1970-01-01' AS TIMESTAMP)",
                total_microseconds_series.astype('int64'),
            ),
            name=self.name,
        )
        return result.copy_override_type(SeriesTimedelta)


def _convert_numpy_datetime_to_utc_datetime(value: numpy.datetime64) -> datetime.datetime:
    # Weird trick: count number of microseconds in datetime, but only works on timedelta, so convert
    # to a timedelta first, by subtracting 0 (epoch = 1970-01-01 00:00:00)
    # Rounding can be unpredictable because of limited precision, so always truncate excess precision
    microseconds = int((value - numpy.datetime64('1970', 'us')) // numpy.timedelta64(1, 'us'))
    return datetime.datetime.utcfromtimestamp(microseconds / 1_000_000)
