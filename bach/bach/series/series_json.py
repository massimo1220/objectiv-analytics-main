"""
Copyright 2021 Objectiv B.V.
"""
import json
import operator
from functools import reduce
from typing import Dict, Union, TYPE_CHECKING, Tuple, cast, Optional, List, Any, TypeVar, Generic

from sqlalchemy.engine import Dialect

from bach import SortColumn
from bach.series import Series
from bach.expression import Expression, join_expressions
from bach.series.series import WrappedPartition, ToPandasInfo, value_to_series
from bach.sql_model import BachSqlModel
from bach.types import DtypeOrAlias, StructuredDtype, AllSupportedLiteralTypes
from sql_models.constants import DBDialect
from sql_models.model import Materialization
from sql_models.util import quote_string, is_postgres, DatabaseNotSupportedException, is_bigquery, is_athena

if TYPE_CHECKING:
    from bach.series import SeriesBoolean, SeriesString, SeriesInt64
    from bach.partitioning import GroupBy


class SeriesJson(Series):
    """
    A Series that represents the JSON type and its specific operations.


    **Database support and types**

    * On Postgres this utilizes the native 'jsonb' database type.
    * On Athena this utilizes the native 'json' database type.
    * On BigQuery this utilizes the generic 'STRING' database type.

    .. note::
        On Postgres, SeriesJson does not use the 'json' database type, but the 'jsonb' type, As the 'json'
        type has limited functionality.

        This class is the standard and recommended type to use for handling json like data. Having said that,
        there is a special SeriesJsonPostgres type that uses the 'json' data type on Postgres, but internally
        that casts all data to 'jsonb' too.

    **Getting data**

    It is possible to get a selection of data from the json in the json type column. For selecting data from
    json, arrays and objects are supported. The data can be selected using `.json[]` on the json column

    Selecting data from an array is based on position. It works similar to slicing through python lists.

    .. note::

        Slicing is only possible if *all* values in the column are lists or None.

    Selecting from objects is possible by key.

    Examples:

     .. testsetup:: json
        :skipif: engine is None

        data = ['["a","b","c"]', '["d","e","f","g"]', '[{"h":"i","j":"k"},{"l":["m","n","o"]},{"p":"q"}]']
        pdf = pd.DataFrame(data=data, columns=['jsonb_column'])
        df = DataFrame.from_pandas(engine, pdf, convert_objects=True)
        df['jsonb_column'] = df.jsonb_column.astype('json')

    .. doctest:: json
        :skipif: engine is None

        >>> pdf
                                                jsonb_column
        0                                      ["a","b","c"]
        1                                  ["d","e","f","g"]
        2  [{"h":"i","j":"k"},{"l":["m","n","o"]},{"p":"q"}]

    .. doctest:: json
        :skipif: engine is None

        >>> df = DataFrame.from_pandas(engine, pdf, convert_objects=True)
        >>> df['jsonb_column'] = df.jsonb_column.astype('json')
        >>> # load some json strings and convert them to jsonb type
        >>> # slice and show with .head()
        >>> df.jsonb_column.json[:2].head()
        _index_0
        0                                            [a, b]
        1                                            [d, e]
        2    [{'h': 'i', 'j': 'k'}, {'l': ['m', 'n', 'o']}]
        Name: jsonb_column, dtype: object

    .. doctest:: json
        :skipif: engine is None

        >>> df.jsonb_column.json[1].head()
        _index_0
        0                         b
        1                         e
        2    {'l': ['m', 'n', 'o']}
        Name: jsonb_column, dtype: object

    .. doctest:: json
        :skipif: engine is None

        >>> # selecting from objects is done by entering a key:
        >>> df.jsonb_column.json[1].json['l'].head()
        _index_0
        0         None
        1         None
        2    [m, n, o]
        Name: jsonb_column, dtype: object

    A last case is selecting based on the objects *in* an array.
    With this method, a dict is passed in the `.json[]` selector. The value of the first match with the dict
    to the objects in a json array is returned for the `.json[]` selector. A match is when all key/value pairs
    of the dict are found in an object. This can be used for selecting a subset of a json array with objects.

    .. doctest:: json
        :skipif: engine is None

        >>> # selecting from arrays by searching objects in the array.
        >>> df.jsonb_column.json[:{"j":"k"}].head()
        _index_0
        0                        []
        1                        []
        2    [{'h': 'i', 'j': 'k'}]
        Name: jsonb_column, dtype: object

    .. doctest:: json
        :skipif: engine is None

        >>> # or:
        >>> df.jsonb_column.json[{"l":["m","n","o"]}:].head()
        _index_0
        0                                      []
        1                                      []
        2    [{'l': ['m', 'n', 'o']}, {'p': 'q'}]
        Name: jsonb_column, dtype: object
    """

    # TODO: support instance_dtype to return better types
    dtype = 'json'
    dtype_aliases: Tuple[DtypeOrAlias, ...] = tuple()
    supported_db_dtype = {
        DBDialect.POSTGRES: 'jsonb',
        DBDialect.ATHENA: 'json',
        # on BigQuery we use STRING for JSONs. Of course SeriesString is the default class for that, so
        # here we set None
        DBDialect.BIGQUERY: None
    }
    supported_value_types = (dict, list, str, float, int, bool)

    supported_source_dtypes = ('json', 'json_postgres', 'string')

    @property
    def json(self) -> 'JsonAccessor':
        """
        Get access to json operations via the class that's returned through this accessor.
        Use as `my_series.json.get_value()` or `my_series.json[:2]`

        .. autoclass:: bach.series.series_json.JsonAccessor
            :members:

        """
        return JsonAccessor(series_object=self)

    @property
    def elements(self):
        return self.json

    @classmethod
    def get_db_dtype(cls, dialect: Dialect) -> Optional[str]:
        if is_bigquery(dialect):
            from bach.series import SeriesString
            return SeriesString.get_db_dtype(dialect)
        return super().get_db_dtype(dialect)

    @classmethod
    def supported_literal_to_expression(cls, dialect: Dialect, literal: Expression) -> Expression:
        if is_postgres(dialect):
            return super().supported_literal_to_expression(dialect=dialect, literal=literal)
        if is_athena(dialect):
            return Expression.construct('json_parse({})', literal)
        if is_bigquery(dialect):
            from bach import SeriesString
            return SeriesString.supported_literal_to_expression(dialect=dialect, literal=literal)
        raise DatabaseNotSupportedException(dialect)

    @classmethod
    def supported_value_to_literal(
            cls,
            dialect: Dialect,
            value: Union[dict, list],
            dtype: StructuredDtype
    ) -> Expression:
        cls.assert_engine_dialect_supported(dialect)
        json_value = json.dumps(value)
        return Expression.string_value(json_value)

    @classmethod
    def dtype_to_expression(cls, dialect: Dialect, source_dtype: str, expression: Expression) -> Expression:
        if is_postgres(dialect):
            if source_dtype in ('json', 'json_postgres'):
                # SeriesJsonPostgres is a special case: SeriesJsonPostgres.expression already contains a cast
                # to the database type 'jsonb', so we actually don't need to do any conversion
                return expression
            if source_dtype == 'string':
                return Expression.construct(f'cast({{}} as {cls.get_db_dtype(dialect)})', expression)
            raise ValueError(f'cannot convert {source_dtype} to json')
        if is_athena(dialect):
            if source_dtype == 'json':
                return expression
            if source_dtype == 'string':
                return Expression.construct('json_parse({})', expression)
            raise ValueError(f'cannot convert {source_dtype} to json')
        if is_bigquery(dialect):
            if source_dtype in ('json', 'string'):
                return expression
            elif source_dtype in ('dict', 'list'):
                # BQ can convert most types into json format, and since we use string as the container
                # in our BQ implementation, this is basically a cast.
                # https://cloud.google.com/bigquery/docs/reference/standard-sql/json_functions#to_json_string
                return Expression.construct(f'to_json_string({{}})', expression)
            else:
                raise ValueError(f'cannot convert {source_dtype} to json')
        raise DatabaseNotSupportedException(dialect)

    def to_pandas_info(self) -> Optional['ToPandasInfo']:
        if is_bigquery(self.engine):
            # All data is stored as string, so if we actually want the objects, we need to load the string
            # as json.
            return ToPandasInfo('object', self._json_loads)
        return None

    @staticmethod
    def _json_loads(data: Optional[str]) -> Optional[Any]:
        """ Helper of to_pandas_info """
        if data is None:
            return None
        try:
            return json.loads(data)
        except ValueError as exc:
            raise ValueError(f'invalid json content in result: {data}') from exc

    def _comparator_operation(
        self,
        other: Union['Series', AllSupportedLiteralTypes],
        comparator: str,
        other_dtypes=tuple(),
        strict_other_dtypes=tuple()
    ) -> 'SeriesBoolean':
        if is_postgres(self.engine):
            other_dtypes = ('json_postgres', 'json', 'string')
            strict_other_dtypes = tuple(['json_postgres'])
        elif is_athena(self.engine):
            other_dtypes = ('json', 'string')
            strict_other_dtypes = tuple(['json'])
        elif is_bigquery(self.engine):
            other_dtypes = ('json', 'string')
        else:
            raise DatabaseNotSupportedException(self.engine)

        result = self._binary_operation(
            other, operation=f"comparator '{comparator}'",
            fmt_str=f'{{}} {comparator} {{}}',
            other_dtypes=other_dtypes, dtype='bool', strict_other_dtypes=strict_other_dtypes
        )
        return cast('SeriesBoolean', result)  # we told _binary_operation to return dtype='bool'

    def __le__(self, other: Union['Series', AllSupportedLiteralTypes]) -> 'SeriesBoolean':
        raise NotImplementedError()

    def __ge__(self, other: Union['Series', AllSupportedLiteralTypes]) -> 'SeriesBoolean':
        raise NotImplementedError()

    def min(self, partition: WrappedPartition = None, skipna: bool = True):
        """ INTERNAL: Only here to not trigger errors from describe """
        raise NotImplementedError()

    def max(self, partition: WrappedPartition = None, skipna: bool = True):
        """ INTERNAL: Only here to not trigger errors from describe """
        raise NotImplementedError()


class SeriesJsonPostgres(SeriesJson):
    """
    A special Series that represents the 'json' database type on Postgres.

    .. note::
        Generally, it is advised to use :class:`JsonSeries` instead. Given a `SeriesJsonPostgres` object,
        calling `json_series_pg.astype('json')` will return a `JsonSeries` class representing the same data.

    When `json` data is encountered in a sql table, this dtype is used. On Postgres for all operations the
    data is first cast to jsonb type. Therefore, it is recommended to cast to :class:`JsonSeries` directly.

    The public interface of this class is the same as the :py:class:`SeriesJson` class. See the docstring
    of that class for more information.
    """

    dtype = 'json_postgres'
    dtype_aliases: Tuple[DtypeOrAlias, ...] = tuple()
    supported_db_dtype = {
        DBDialect.POSTGRES: 'json',
    }

    def __init__(self,
                 engine,
                 base_node: BachSqlModel,
                 index: Dict[str, 'Series'],
                 name: str,
                 expression: Expression,
                 group_by: 'GroupBy',
                 order_by: Optional[List[SortColumn]],
                 instance_dtype: StructuredDtype,
                 **kwargs):

        super().__init__(engine=engine,
                         base_node=base_node,
                         index=index,
                         name=name,
                         expression=Expression.construct(f'cast({{}} as jsonb)', expression),
                         group_by=group_by,
                         order_by=order_by,
                         instance_dtype=instance_dtype,
                         **kwargs)

    @property
    def json(self) -> 'JsonAccessor':
        """
        Get access to json operations via the class that's returned through this accessor.
        Use as `my_series.json.get_value()` or `my_series.json[:2]`

        .. autoclass:: bach.series.series_json.JsonAccessor
            :members:
        """
        json_series = self.astype('json')
        assert isinstance(json_series, SeriesJson)  # help mypy
        return json_series.json

    def materialize(
            self,
            node_name='manual_materialize',
            limit: Any = None,
            distinct: bool = False,
            materialization: Union[Materialization, str] = Materialization.CTE
    ):
        """
        Instance of this Series cannot be materialized, as the base expression is not just the column name
        but a cast to 'jsonb'.

        Use class:`SeriesJson` instead, which can be materialized.
        """
        raise Exception(f'{self.__class__.__name__} cannot be materialized.')


TSeriesJson = TypeVar('TSeriesJson', bound='SeriesJson')


class JsonAccessor(Generic[TSeriesJson]):
    """
    Class with accessor methods to JSON type data.
    """

    # We have different implementations for different databases. This class is a facade, that will call the
    # actual implementing class based on the used database engine.
    # Having this facade (instead of having subclasses per engine) makes it possible to have classes inherit
    # from this class.

    def __init__(self, series_object: 'TSeriesJson'):
        self._series_object = series_object

        # _implementation implements the actual functionality.
        engine = self._series_object.engine
        self._implementation: Union[
            JsonPostgresAccessorImpl, JsonAthenaAccessorImpl, JsonBigQueryAccessorImpl
        ]
        if is_postgres(engine):
            self._implementation = JsonPostgresAccessorImpl(series_object)
        elif is_athena(engine):
            self._implementation = JsonAthenaAccessorImpl(series_object)
        elif is_bigquery(engine):
            self._implementation = JsonBigQueryAccessorImpl(series_object)
        else:
            raise DatabaseNotSupportedException(engine)

    def __getitem__(self, key: Union[str, int, slice]) -> 'TSeriesJson':
        """
        Get item(s) from the JSON data in pythonic ways.
        The way item(s) are looked up depends on the type of key.

        If key is an integer, then this returns an item from the json array.
        The key is treated as a 0-based index. If negative this will count from the end of the array (one
            based). If the index does not exists this will render None/NULL.
        This assumes the top-level item in the json is an array

        If key is a slice, then this returns a slice from the json array.
        This assumes the top-level item in the json is an array

        If key is a string, then this returns an item from the json object. The item belonging to the given
            key is returned, or None/NULL if not found.
        This assumes the top-level item in the json is an object
        """
        # TODO: leverage instance_dtype information here, if we have that
        if isinstance(key, int):
            return self._implementation.get_array_item(key)

        elif isinstance(key, str):
            return self._implementation.get_dict_item(key)

        elif isinstance(key, slice):
            return self._implementation.get_array_slice(key)

        raise TypeError('Key should either be a string, integer, or slice.')

    def get_value(self, key: str, as_str: bool = False) -> Union['SeriesString', 'TSeriesJson']:
        """
        Get item from toplevel object by key.

        :param key: the key to return the values for.
        :param as_str: if True, it returns a string Series, json otherwise. Particular useful if the returned
            value is in fact a string. In json the string will be represented as a quoted string, if this
            field is set to true, the returned SeriesString will not have additional quotes.
        :returns: series with the selected object value.
        """
        return self._implementation.get_value(key=key, as_str=as_str)

    def get_array_length(self) -> 'SeriesInt64':
        """
        Get the length of the toplevel array.

        This assumes the top-level item in the json is an array. Will result in an exception (later on) if
        that's not the case!
        """
        # Implementing a more generic __len__() function is not trivial as a json object can be (among
        # others) an array, a dict, or a string, all of which should be supported by a generic __len__().
        # So for now we have a dedicated len function for arrays.
        return self._implementation.get_array_length()

    def array_contains(self, item: Union[int, float, bool, str, None]) -> 'SeriesBoolean':
        """
        Find if item is contained in the array.

        :param item: item to be verified if it is contained by the array. Only supports scalar values.
        :returns: boolean series indicating if the array contains the element.

        This assumes the top-level item in the json is an array.
        """

        return self._implementation.array_contains(item)

    def flatten_array(self) -> Tuple['TSeriesJson', 'SeriesInt64']:
        """
        Converts elements in an array into a set of rows.

        Since the operation might destroy the order of the elements,
        a series containing the offset is also returned.

        :returns: Tuple with SeriesJson (element from the array) and SeriesInt64 (offset of the element)

        .. note::
            Both returned series objects will share same base node, but this node is not
            the same as the unflatten Series.

        This assumes the top-level item in the json is an array.
        """
        return self._implementation.flatten_array()


class JsonBigQueryAccessorImpl(Generic[TSeriesJson]):
    """
    BigQuery specific implementation of JsonAccessor functions.
    """

    def __init__(self, series_object: 'TSeriesJson'):
        self._series_object = series_object

    def get_array_slice(self, key: slice) -> 'TSeriesJson':
        """ See implementation in parent class :class:`JsonAccessor` """
        if key.step:
            raise NotImplementedError('slice steps not supported')

        start_expression = self._get_slice_partial_expr(value=key.start, is_start=True)
        stop_expression = self._get_slice_partial_expr(value=key.stop, is_start=False)

        values_expression = Expression.construct(
            "select val "
            "from unnest(JSON_QUERY_ARRAY({}, '$')) val with offset as pos "
            "where pos >= {} and pos < {} "
            "order by pos",
            self._series_object, start_expression, stop_expression
        )
        json_str_expression = Expression.construct(
            "'[' || ARRAY_TO_STRING(ARRAY({}), ', ') || ']'",
            values_expression
        )
        return self._series_object\
            .copy_override(expression=json_str_expression)

    def _get_slice_partial_expr(
        self,
        value: Optional[Union[Dict[str, str], int]],
        is_start: bool,
    ) -> Expression:
        """
        Helper of get_array_slice(). return expression for either the lower bound or upper bound of a slice.

        Assumes that self._series_object is an array!

        :param value: slice.start or slice.stop
        :param is_start: whether value is the slice.start (True) or slice.stop (False) value
        :return: Expression that will evaluate to an integer that can be used to compare against positions
                    in the array.
        """
        if isinstance(value, dict):
            return self._find_in_json_list(value, is_start)

        if value is not None and not isinstance(value, int):
            raise TypeError(f'Slice value must be None or an integer, value: {value}')

        if value is None:
            if is_start:
                # return index of first item in the array
                return Expression.construct('0')
            else:
                # return index that is guaranteed to be beyond the last item in the array
                max_int = 2 ** 63 - 1
                return Expression.construct(f'{max_int}')
        elif value >= 0:
            return Expression.construct(f'{value}')
        else:
            array_len = self.get_array_length()
            return Expression.construct(f'({{}} {value})', array_len)

    def _find_in_json_list(self, filtering_slice: Dict[str, str], is_start: bool):
        """
        Return expression for the position of the element that contains the filtering values

        Assumes that self._series_object is an array and each element is a json!

        :param filtering_slice: dictionary containing the keys and values to use on filter.
        :param is_start: whether value is the slice.start (True) or slice.stop (False) value. If true,
            the first element containing the values is returned, otherwise the last.
        :return: Expression that gets the position of the element based on the slicing filters.
        """
        if not isinstance(filtering_slice, dict):
            raise TypeError(f'key should be a dict, actual type: {type(filtering_slice)}')

        # this way we can reuse code from the accessor without duplicating.
        # 'element' will be filled by iterating over the json array in the query below.
        element_json = self._series_object.copy_override(
            expression=Expression.construct('element'),
        )

        all_filters = [
            element_json.json.get_value(filter_key, as_str=True) == str(filter_value)
            for filter_key, filter_value in filtering_slice.items()
        ]
        slicing_mask = reduce(operator.and_, all_filters)
        fmt = (
            # end slicing is inclusive
            f"(select {'min' if is_start else '1 + max'}(case when {{}} then pos end) "
            f"from unnest(JSON_QUERY_ARRAY({{}}, '$')) element with offset as pos)"
        )
        return Expression.construct(fmt, slicing_mask, self._series_object)

    def get_array_item(self, key: int) -> 'TSeriesJson':
        """
        Returns an item from the json array.
        The key is treated as a 0-based index. If negative this will count from the end of the array (one
            based). If the index does not exist this will render None/NULL.
        This assumes the top-level item in the json is an array
        """
        if key < 0:
            # BigQuery doesn't (yet) natively support this, so we emulate this by reversing the array
            key = abs(key)
            expression = Expression.construct(
                f'ARRAY_REVERSE(JSON_QUERY_ARRAY({{}}))[SAFE_ORDINAL({key})]',
                self._series_object
            )
        else:
            expression = Expression.construct(f'''JSON_QUERY({{}}, '$[{key}]')''', self._series_object)
        return self._series_object.copy_override(expression=expression)

    def get_dict_item(self, key: str) -> 'TSeriesJson':
        """ For documentation, see implementation in parent class :class:`JsonAccessor` """
        return cast('TSeriesJson', self.get_value(key=key, as_str=False))

    def get_value(self, key: str, as_str: bool = False) -> Union['SeriesString', 'TSeriesJson']:
        """ For documentation, see function :meth:`JsonAccessor.get_value()` """
        # Special characters are tricky. According to the latest jsonpath spec draft we should use the
        # index selector [1] (e.g. `$['key with special characters']`). But BigQuery only supports the dot
        # selector [2][3]. However BigQuery does allow us to quote the key when using the dot selector [4],
        # which is not in the jsonpath draft spec. So we quote the key, and just raise an exception if
        # anybody tries to use a key that contains a quote.
        # [1] https://www.ietf.org/archive/id/draft-ietf-jsonpath-base-05.html#name-index-selector
        # [2] https://www.ietf.org/archive/id/draft-ietf-jsonpath-base-05.html#name-dot-selector
        # [3] https://cloud.google.com/bigquery/docs/reference/standard-sql/json_functions#JSONPath_format
        # [4] https://cloud.google.com/bigquery/docs/reference/standard-sql/json_functions
        if '"' in key:
            raise ValueError(f'key values containing double quotes are not supported. key: {key}')

        json_expression = Expression.construct(
            '''JSON_QUERY({}, '$."{}"')''',
            self._series_object,
            Expression.raw(key)
        )

        if not as_str:
            return self._series_object.copy_override(expression=json_expression)
        from bach.series import SeriesString
        # JSON_QUERY will return a string containing valid json. i.e. if the queried value is a string, then
        # it will be quoted. Here we remove the quotes
        value_expression = Expression.construct(
            f'REGEXP_REPLACE({{}}, {{}}, {{}})',
            json_expression,
            Expression.raw('r\'(^"|"$)\''),
            Expression.string_value(''),
        )
        return self._series_object.copy_override(
            expression=value_expression
        ).copy_override_type(SeriesString)

    def get_array_length(self) -> 'SeriesInt64':
        """ For documentation, see function :meth:`JsonAccessor.get_array_length()` """
        # Implementing a more generic __len__() function is not trivial as a json object can be (among
        # others) an array, a dict, or a string, all of which should be supported by a generic __len__().
        # So for now we have a dedicated len function for arrays.
        from bach.series import SeriesInt64
        expression = Expression.construct('ARRAY_LENGTH(JSON_QUERY_ARRAY({}))', self._series_object)
        return self._series_object \
            .copy_override_type(SeriesInt64) \
            .copy_override(expression=expression)

    def array_contains(self, item: Union[int, float, bool, str, None]) -> 'SeriesBoolean':
        """ For documentation, see implementation in class :class:`JsonAccessor` """
        item_json = json.dumps(item)
        in_expr = Expression.construct(
            '(SELECT {} IN UNNEST(JSON_QUERY_ARRAY({})))',
            Expression.string_value(item_json),
            self._series_object
        )
        expression = Expression.construct('IF({} IS NULL, NULL, {})', self._series_object, in_expr)
        from bach.series import SeriesBoolean
        return self._series_object\
            .copy_override(expression=expression)\
            .copy_override_type(SeriesBoolean)

    def flatten_array(self) -> Tuple['TSeriesJson', 'SeriesInt64']:
        """ For documentation, see implementation in class :class:`JsonAccessor` """
        from bach.series.array_operations.flattening import BigQueryArrayFlattening
        return BigQueryArrayFlattening(self._series_object)()


class JsonPostgresAccessorImpl(Generic[TSeriesJson]):
    """
    Postgres specific implementation of JsonAccessor functions.
    """

    def __init__(self, series_object: 'TSeriesJson'):
        self._series_object = series_object

    def _find_in_json_list(self, key: Union[str, Dict[str, str]]):
        if isinstance(key, (dict, str)):
            key = json.dumps(key)
            quoted_key = quote_string(self._series_object.engine, key)
            expression_str = f"""(select min(case when ({quoted_key}::jsonb) <@ value
            then ordinality end) -1 from jsonb_array_elements({{}}) with ordinality)"""
            return expression_str
        else:
            raise TypeError(f'key should be int or slice, actual type: {type(key)}')

    def get_array_slice(self, key: slice) -> 'TSeriesJson':
        """ See implementation in parent class :class:`JsonAccessor` """
        expression_references = 0
        if key.step:
            raise NotImplementedError('slice steps not supported')
        if key.stop is not None:
            negative_stop = ''
            if isinstance(key.stop, int):
                if key.stop < 0:
                    negative_stop = f'jsonb_array_length({{}})'
                    expression_references += 1
                stop = f'{negative_stop} {key.stop} - 1'
            elif isinstance(key.stop, (dict, str)):
                stop = self._find_in_json_list(key.stop)
                expression_references += 1
            else:
                raise TypeError('cant')
        if key.start is not None:
            if isinstance(key.start, int):
                negative_start = ''
                if key.start < 0:
                    negative_start = f'jsonb_array_length({{}})'
                    expression_references += 1
                start = f'{negative_start} {key.start}'
            elif isinstance(key.start, (dict, str)):
                start = self._find_in_json_list(key.start)
                expression_references += 1
            else:
                raise TypeError('cant')
            if key.stop is not None:
                where = f'between {start} and {stop}'
            else:
                where = f'>= {start}'
        else:
            if key.stop is not None:
                where = f'<= {stop}'
            else:
                # no start and no stop: we want to select all elements.
                where = 'is not null'  # should be true for all ordinalities.
        combined_expression = f"""(select jsonb_agg(x.value)
        from jsonb_array_elements({{}}) with ordinality x
        where ordinality - 1 {where})"""
        expression_references += 1
        non_null_expression = f"coalesce({combined_expression}, '[]'::jsonb)"
        return self._series_object \
            .copy_override(
                expression=Expression.construct(
                    non_null_expression,
                    *([self._series_object] * expression_references)
                )
            )

    def get_array_item(self, key: int) -> 'TSeriesJson':
        """
        Returns an item from the json array.
        The key is treated as a 0-based index. If negative this will count from the end of the array (one
            based). If the index does not exist this will render None/NULL.
        This assumes the top-level item in the json is an array
        """
        return self._series_object \
            .copy_override(expression=Expression.construct(f'{{}}->{key}', self._series_object))

    def get_dict_item(self, key: str) -> 'TSeriesJson':
        """ For documentation, see implementation in parent class :class:`JsonAccessor` """
        return cast('TSeriesJson', self.get_value(key=key, as_str=False))

    def get_value(self, key: str, as_str: bool = False) -> Union['SeriesString', 'TSeriesJson']:
        """ For documentation, see function :meth:`JsonAccessor.get_value()` """

        if '"' in key:
            raise ValueError(f'key values containing double quotes are not supported. key: {key}')

        return_as_string_operator = ''
        if as_str:
            return_as_string_operator = '>'
        expression = Expression.construct(f"{{}}->{return_as_string_operator}{{}}",
                                          self._series_object,
                                          Expression.string_value(key))
        result = self._series_object.copy_override(expression=expression)
        if as_str:
            from bach.series import SeriesString
            return result.copy_override_type(SeriesString)
        return result

    def get_array_length(self) -> 'SeriesInt64':
        """ For documentation, see function :meth:`JsonAccessor.get_array_length()` """
        from bach.series import SeriesInt64
        expression = Expression.construct('jsonb_array_length({})', self._series_object)
        return self._series_object \
            .copy_override_type(SeriesInt64) \
            .copy_override(expression=expression)

    def array_contains(self, item: Union[int, float, bool, str, None]) -> 'SeriesBoolean':
        """ For documentation, see implementation in class :class:`JsonAccessor` """
        return self._series_object._comparator_operation([item], "@>")

    def flatten_array(self) -> Tuple['TSeriesJson', 'SeriesInt64']:
        """ For documentation, see implementation in class :class:`JsonAccessor` """
        from bach.series.array_operations.flattening import PostgresArrayFlattening
        return PostgresArrayFlattening(self._series_object)()


class JsonAthenaAccessorImpl(Generic[TSeriesJson]):
    """
    Athena specific implementation of JsonAccessor functions.
    """

    def __init__(self, series_object: 'TSeriesJson'):
        self._series_object = series_object

    def get_array_slice(self, key: slice) -> 'TSeriesJson':
        """ See implementation in parent class :class:`JsonAccessor` """
        if key.step:
            raise NotImplementedError('slice steps not supported')

        start_expression = self._get_slice_partial_expr(value=key.start, is_start=True)
        stop_expression = self._get_slice_partial_expr(value=key.stop, is_start=False)

        values_expression = Expression.construct(
            "slice(cast({} as array(json)), {}, {})",
            self._series_object,
            start_expression,  # startpoint of slice
            Expression.construct('({} - {})', stop_expression, start_expression),  # length of slice
        )
        non_null_expr = Expression.construct('coalesce({}, ARRAY [])', values_expression)
        json_expression = Expression.construct('cast({} as json)', non_null_expr)
        return self._series_object\
            .copy_override(expression=json_expression)

    def _get_slice_partial_expr(
        self,
        value: Optional[Union[Dict[str, str], int]],
        is_start: bool,
    ) -> Expression:
        """
        Helper of get_array_slice(). return expression for either the lower bound or upper bound of a slice.

        Assumes that self._series_object is an array!

        :param value: slice.start or slice.stop
        :param is_start: whether value is the slice.start (True) or slice.stop (False) value
        :return: Expression that will evaluate to an integer that can be used as an one-based array index.
        """
        if isinstance(value, dict):
            return self._find_in_json_list(value, is_start)

        if value is not None and not isinstance(value, int):
            raise TypeError(f'Slice value must be None or an integer, value: {value}')

        if value is None:
            if is_start:
                # return index of first item in the array
                return Expression.construct('1')
            else:
                # return index that is guaranteed to be beyond the last item in the array, but no bigger
                # than a 32-bit integer. Experiments have shown that slice() will give empty results, if
                # the length is larger than a 32 bit integer.
                max_int = 2 ** 31 - 1
                return Expression.construct(f'{max_int}')
        elif value >= 0:
            return Expression.construct(f'{value + 1}')
        else:
            array_len = self.get_array_length()
            return Expression.construct(f'({{}} {value} + 1)', array_len)

    def _find_in_json_list(self, filtering_slice: Dict[str, str], is_start: bool):
        """
        Return expression for the position of the element that contains the filtering values. The element
        can contain more values than the filtering values, but it must contain all of the values in
        filtering_slice.

        Assumes that self._series_object is an array, each element is a json object!

        :param filtering_slice: dictionary containing the keys and values to use on filter.
            Must be a dictionary with strings as keys and values!
        :param is_start: whether value is the slice.start (True) or slice.stop (False) value. If true,
            the first element containing the values is returned, otherwise the last.
        :return: Expression that gets the position (one-based) of the element based on the slicing filters.
        """
        # Athena doesn't support correlated subqueries, so we cannot use a select here to find the position
        # of the element.
        # Strategy:
        # 1. convert to array of maps
        # 2. filter array of maps on the values we look for
        # 3.1 for is_start:
        #   find first position of first element from the filtered array in the original json array
        # 3.2 for not is_start:
        #   find last position of last element from the filtered array in the original json array

        if not isinstance(filtering_slice, dict):
            raise TypeError(f'Key should be a dict, actual type: {type(filtering_slice)}')
        if not all(isinstance(key, str) for key in filtering_slice.keys()):
            raise TypeError(f'Keys in the key dict, should all be strings')
        if not all(isinstance(value, str) for value in filtering_slice.values()):
            raise TypeError(f'Values in the key dict, should all be strings')

        array_expr = Expression.construct('cast({} as array(json))', self._series_object)
        array_map_expr = Expression.construct(
            'try(cast({} as array(map(varchar, json))))',
            self._series_object
        )
        filter_condition_exprs = [
            Expression.construct(
                "x[{}] = cast({} as json)",
                Expression.string_value(key),
                Expression.string_value(value)
            )
            for key, value in filtering_slice.items()
        ]
        # filter_array_map_expr: array of maps, but only with the maps that match the filter criteria
        filter_array_map_expr = Expression.construct(
            'filter({}, x -> ({}))',
            array_map_expr,
            join_expressions(filter_condition_exprs, ' and ')
        )
        # filter_array_expr: array with all json objects that match the filter criteria, in the same order
        # as they appear in the original json array
        filter_array_expr = Expression.construct('cast({} as array(json))', filter_array_map_expr)

        if is_start:
            # Find the position in the original array, of the first object that matches the filter criteria
            first_element_pos_expr = Expression.construct(
                'array_position({}, element_at({}, 1))',
                array_expr,
                filter_array_expr
            )
            return first_element_pos_expr
        # elif not is_start: Find the position in the reversed original array, of the last element that
        # matches the filter criteria. This is the last element that matches the criteria in the original
        # array.
        element_reverse_pos_expr = Expression.construct(
            'array_position(reverse({}), element_at({}, -1))',
            array_expr,
            filter_array_expr
        )
        # We need to translate the location in the reverse array to the position in the actual array.
        # Formula for this: `(array_length + 1 ) - element_reverse_pos_expr`
        # Additionally we need to add 1, because for historical reasons the end of a filtering slice
        # includes the last matched element (unlike a regular slice where the end element is not
        # included).
        last_element_pos_expr = Expression.construct(
            '({} + 2 ) - {}',
            self.get_array_length(),
            element_reverse_pos_expr
        )
        return last_element_pos_expr

    def get_array_item(self, key: int) -> 'TSeriesJson':
        """
        Returns an item from the json array.
        The key is treated as a 0-based index. If negative this will count from the end of the array (one
            based). If the index does not exist this will render None/NULL.
        This assumes the top-level item in the json is an array
        """
        # Athena also has a function `json_array_get()`. That function should do what we want, but it's
        # broken and of no use to us as it returns invalid json in some cases [1]. Instead, we cast the
        # json to a sql-array of jsons, and get the requested item from that.
        # [1] https://prestodb.io/docs/0.217/functions/json.html

        # sql-arrays use zero-based indexing for positive values.
        offset = key if key < 0 else key + 1
        expression = Expression.construct(
            f'element_at(try(cast({{}} as array(json))), {offset})',
            self._series_object
        )
        return self._series_object.copy_override(expression=expression)

    def get_dict_item(self, key: str) -> 'TSeriesJson':
        """ For documentation, see implementation in parent class :class:`JsonAccessor` """
        return cast('TSeriesJson', self.get_value(key=key, as_str=False))

    def get_value(self, key: str, as_str: bool = False) -> Union['SeriesString', 'TSeriesJson']:
        """ For documentation, see function :meth:`JsonAccessor.get_value()` """
        if '"' in key:
            raise ValueError(f'key values containing double quotes are not supported. key: {key}')

        json_expression = Expression.construct(
            '''json_extract({}, '$["{}"]')''',
            self._series_object,
            Expression.raw(key)
        )

        if not as_str:
            return self._series_object.copy_override(expression=json_expression)

        # TODO: use SeriesString.str.replace() when it supports regexp
        str_expression = Expression.construct('json_format({})', json_expression)
        value_expression = Expression.construct(
            f'regexp_replace({{}}, {{}}, {{}})',
            str_expression,
            Expression.raw('\'(^"|"$)\''),
            Expression.string_value(''),
        )
        from bach.series import SeriesString
        return self._series_object\
            .copy_override(expression=value_expression)\
            .copy_override_type(SeriesString)

    def get_array_length(self) -> 'SeriesInt64':
        """ For documentation, see function :meth:`JsonAccessor.get_array_length()` """
        from bach.series import SeriesInt64
        expression = Expression.construct('json_array_length({})', self._series_object)
        return self._series_object \
            .copy_override_type(SeriesInt64) \
            .copy_override(expression=expression)

    def array_contains(self, item: Union[int, float, bool, str, None]) -> 'SeriesBoolean':
        """ For documentation, see implementation in class :class:`JsonAccessor` """
        from bach.series import SeriesBoolean
        if item is None:
            # json_array_contains does not work when the item we are looking for is `null`, it will always
            # return a sql NULL in that case. So for that special case we fall back to the regular array
            # contains.
            expression = Expression.construct(
                "contains(cast({} as array(json)), json_parse('null'))",
                self._series_object
            )
        else:
            # Regular case.
            # The second argument to json_array_contains has to be an Athena native bigint, double, bool, or
            # varchar, not a json.
            item_expr = value_to_series(base=self._series_object, value=item).expression
            expression = Expression.construct('json_array_contains({}, {})', self._series_object, item_expr)
        return self._series_object \
            .copy_override_type(SeriesBoolean) \
            .copy_override(expression=expression)

    def flatten_array(self) -> Tuple['TSeriesJson', 'SeriesInt64']:
        """ For documentation, see implementation in class :class:`JsonAccessor` """
        from bach.series.array_operations.flattening import AthenaArrayFlattening
        return AthenaArrayFlattening(self._series_object)()
