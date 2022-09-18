"""
Copyright 2021 Objectiv B.V.
"""
from typing import List

import pytest

from sql_models.sql_query_parser import raw_sql_to_selects, CteTuple
from tests.unit.sql_models.util import assert_roughly_equal_sql


# mark all tests here as database independent. Perhaps in the future we'll have DB specific parsing, but
# currently having generic parsing is enough
pytestmark = [pytest.mark.db_independent]


def test_parse_select():
    sql = 'select x from y where z > 5 limit 3'
    result = raw_sql_to_selects(sql)
    assert result == [CteTuple(name=None, select_sql=sql)]

    sql = 'select x from y where z > 5 limit 3;'
    result = raw_sql_to_selects(sql)
    assert result == [CteTuple(name=None, select_sql=sql)]

    sql = '''
        select t1.a, t2.b, t2.c
        from table1 as t1
        join table2 as t2 on t1.a = t2.a
        where t2.z > 5
    '''
    result = raw_sql_to_selects(sql)
    assert result == [CteTuple(name=None, select_sql=sql)]


def test_parse_cte_select():
    sql = '''
        with cte_a as (
            select x from t1
        )
        select x from cte_a
        where z > 5 limit 3
    '''
    result = raw_sql_to_selects(sql)
    expected = [
        CteTuple(name='cte_a', select_sql='select x from t1'),
        CteTuple(name=None, select_sql='select x from cte_a where z > 5 limit 3')
    ]
    _assert_equals_cte_tuples(result, expected)


def test_parse_multiple_cte_select():
    sql = '''
        with cte_a as (
            select x from t1
        ), cte_b as (
            select col1, col2 from table2
        )
        select x
        from cte_a
        inner join cte_b on cte_a.x = cte_b.col1
        where z > 5
        limit 3
    '''
    result = raw_sql_to_selects(sql)
    expected = [
        CteTuple(name='cte_a', select_sql='select x from t1'),
        CteTuple(name='cte_b', select_sql='select col1, col2 from table2'),
        CteTuple(name=None, select_sql='''
                    select x
                    from cte_a
                    inner join cte_b on cte_a.x = cte_b.col1
                    where z > 5
                    limit 3
                ''')
    ]
    _assert_equals_cte_tuples(result, expected)


def _assert_equals_cte_tuples(actual: List[CteTuple], expected: List[CteTuple]):
    assert len(actual) == len(expected)
    for a, e in zip(actual, expected):
        assert a.name == e.name
        # remove all whitespace, and check that sql is the same. This is not a perfect check
        # TODO check sql better
        assert_roughly_equal_sql(a.select_sql, e.select_sql)

# todo: tests for error cases, e.g. invalid syntax, or update statements
