"""
Copyright 2022 Objectiv B.V.
"""
import pytest

from sql_models.util import is_postgres, is_athena, is_bigquery, DatabaseNotSupportedException
from tests.unit.bach.util import get_fake_df_test_data


def test_unmaterializable_groupby_boolean_functions(dialect):
    # Windowing function are not allowed as boolean row selectors.
    bt = get_fake_df_test_data(dialect)
    btg_min_fnd = bt.groupby('municipality')['founding'].min()

    assert btg_min_fnd.base_node == bt.base_node
    assert btg_min_fnd.group_by != bt.group_by
    assert not btg_min_fnd.expression.is_single_value

    with pytest.raises(ValueError, match=r'dtypes of indexes to be merged should be the same'):
        # todo pandas: Can only compare identically-labeled Series objects
        bt[btg_min_fnd == bt.founding]

    with pytest.raises(ValueError, match=r'dtypes of indexes to be merged should be the same'):
        # todo pandas: Can only compare identically-labeled Series objects
        bt[bt.founding == btg_min_fnd]


def test_on_argument_sets(dialect):
    df = get_fake_df_test_data(dialect)
    group_by_argument = ('municipality',)
    if is_postgres(dialect) or is_athena(dialect):  # supported
        dfg = df.groupby(group_by_argument)
        assert dfg.group_by is not None
    elif is_bigquery(dialect):  # not supported
        with pytest.raises(DatabaseNotSupportedException, match='GroupingSets are not supported'):
            dfg = df.groupby(group_by_argument)
    else:
        raise Exception(f'Test does not yet support {dialect}')


def test_on_argument_lists(dialect):
    df = get_fake_df_test_data(dialect)
    group_by_argument = [['municipality',]]
    if is_postgres(dialect) or is_athena(dialect):  # supported
        dfg = df.groupby(group_by_argument)
        assert dfg.group_by is not None
    elif is_bigquery(dialect):  # not supported
        with pytest.raises(DatabaseNotSupportedException, match='GroupingLists are not supported'):
            dfg = df.groupby(group_by_argument)
    else:
        raise Exception(f'Test does not yet support {dialect}')
