from typing import NamedTuple

import pytest

from bach.expression import Expression
from bach.sql_model import BachSqlModel
from bach.utils import get_merged_series_dtype, is_valid_column_name, SortColumn, validate_node_column_references_in_sorting_expressions
from sql_models.model import Materialization, CustomSqlModelBuilder


@pytest.mark.db_independent
def test_get_merged_series_dtype() -> None:
    assert get_merged_series_dtype({'string', 'int64'}) == 'string'
    assert get_merged_series_dtype({'int64'}) == 'int64'
    assert get_merged_series_dtype({'float64', 'int64'}) == 'float64'


class ColNameValid(NamedTuple):
    name: str
    postgresql: bool
    awsathena: bool
    bigquery: bool


def test_is_valid_column_name(dialect):
    tests = [
        #            column name                              PG     Athena BQ
        ColNameValid('test',                                  True,  True,  True),
        ColNameValid('test' * 15 + 'tes',                     True,  True,  True),   # 63 characters
        ColNameValid('test' * 15 + 'test',                    False, True,  True),   # 64 characters
        ColNameValid('abcdefghij' * 30 ,                      False, False, True),   # 300 characters
        ColNameValid('abcdefghij' * 30 + 'a',                 False, False, False),  # 301 characters
        ColNameValid('_index_skating_order',                  True,  True,  True),
        ColNameValid('1234',                                  True,  True,  False),
        ColNameValid('1234_test_test',                        True,  True,  False),
        ColNameValid('With_Capitals',                         True,  False, True),
        ColNameValid('__SADHDasdfasfASAUIJLKJKAHK',           True,  False, True),
        ColNameValid('with{format}{{strings}}{{}%%@#KLJLC',   True,  False, False),
        ColNameValid('Aa_!#!$*(aA®Řﬦ‎	⛔',                  True,  False, False),
        # Reserved prefixes in BigQuery
        ColNameValid('_TABLE_test',                           True,  False, False),
        ColNameValid('_FILE_test',                            True,  False, False),
        ColNameValid('_PARTITIONtest',                        True,  False, False),
        ColNameValid('_ROW_TIMESTAMPtest',                    True,  False, False),
        ColNameValid('__ROOT__test',                          True,  False, False),
        ColNameValid('_COLIDENTIFIERtest',                    True,  False, False),
    ]
    for test in tests:
        expected = getattr(test, dialect.name)
        column_name = test.name
        assert is_valid_column_name(dialect, column_name) is expected


@pytest.mark.db_independent
def test_validate_sorting_expressions() -> None:
    model = BachSqlModel(
        model_spec=CustomSqlModelBuilder(sql='SELECT * FROM test', name='test'),
        placeholders={},
        references={},
        materialization=Materialization.CTE,
        materialization_name=None,
        column_expressions={
            'a': Expression.column_reference('a'),
            'b': Expression.column_reference('b'),
        },
    )

    with pytest.raises(ValueError, match=r'Sorting contains expressions referencing'):
        validate_node_column_references_in_sorting_expressions(
            model, [SortColumn(expression=Expression.column_reference('c'), asc=True)],
        )

    validate_node_column_references_in_sorting_expressions(
        node=model,
        order_by=[
            SortColumn(
                expression=Expression(
                    data=[
                        Expression.column_reference('b'), Expression.raw('+'), Expression.column_reference('a'),
                    ],
                ),
                asc=True
            )
        ]
    )
