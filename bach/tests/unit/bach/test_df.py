"""
Copyright 2021 Objectiv B.V.
"""
from typing import List

import pytest

from bach import SortColumn, DataFrame
from bach.expression import Expression
from bach.partitioning import GroupBy
from bach.savepoints import Savepoints
from bach.sql_model import BachSqlModel
from sql_models.model import CustomSqlModelBuilder
from tests.unit.bach.util import get_fake_df


def test__eq__(dialect):
    def get_df(index_names: List[str], data_names: List[str]):
        return get_fake_df(dialect=dialect, index_names=index_names, data_names=data_names)

    assert get_df(['a'], ['b', 'c']) != 123
    assert get_df(['a'], ['b', 'c']) != 'a'
    assert get_df(['a'], ['b', 'c']) != (['a'], ['b', 'c'])

    result = get_df(['a'], ['b', 'c']) == get_df(['a'], ['b', 'c'])
    # Assert that we get a boolean (e.g. for Series this is not the case since we overloaded __eq__ in a
    # different way)
    assert result is True

    assert get_df(['a'], ['b', 'c']) == get_df(['a'], ['b', 'c'])
    assert get_df(['a', 'b'], ['c']) == get_df(['a', 'b'], ['c'])
    # 'b' is index or data column
    assert get_df(['a', 'b'], ['c']) != get_df(['a'], ['b', 'c'])
    # switched order index columns
    assert get_df(['b', 'a'], ['c']) != get_df(['a', 'b'], ['c'])
    # switched order data columns
    assert get_df(['a'], ['b', 'c']) != get_df(['a'], ['c', 'b'])

    left = get_df(['a'], ['b', 'c'])
    right = get_df(['a'], ['b', 'c'])
    assert left == right
    # use fake value for engine and basenode to check that the values are tested
    left._engine = 'test'
    assert left != right
    right._engine = 'test'
    assert left == right
    right._base_node = 'test'
    assert left != right
    left._base_node = 'test'
    assert left == right
    right._order_by = [SortColumn(expression=Expression.column_reference('a'), asc=True)]
    assert left != right
    left._order_by = [SortColumn(expression=Expression.column_reference('a'), asc=False)]
    assert left != right
    left._order_by = [SortColumn(expression=Expression.column_reference('a'), asc=True)]
    assert left == right

    # reset left, right
    left, right = get_df(['a'], ['b', 'c']),  get_df(['a'], ['b', 'c'])

    left = left.set_variable('a', 1234)
    right = right.set_variable('a', '1234')
    assert left != right
    left = left.set_variable('a', '1234')
    right = right.set_variable('a', 1234)
    assert left == right


def test_init_conditions(dialect):
    df = get_fake_df(dialect, ['a'], ['b', 'c'])
    df2 = get_fake_df(dialect, ['a', 'b'], ['c', 'd'])
    columns = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h')
    other_base_node = BachSqlModel.from_sql_model(
        sql_model=CustomSqlModelBuilder('select * from y', name='base')(),
        column_expressions={c: Expression.column_reference(c) for c in columns},
    )

    # Check that with 'normal' parameters the __init__ function does not complain
    DataFrame(
        engine=df.engine,
        base_node=df.base_node,
        index=df.index,
        series=df.data,
        group_by=None,
        order_by=[],
        savepoints=Savepoints()
    )

    # Now check that with wrong values __init__ raises ValueErrors
    with pytest.raises(ValueError, match="Indices in `series` should match dataframe"):
        DataFrame(
            engine=df.engine,
            base_node=df.base_node,
            index=df2.index,
            series=df.data,
            group_by=None,
            order_by=[],
            savepoints=Savepoints()
        )

    with pytest.raises(ValueError, match="Keys in `series` should match the name of series"):
        DataFrame(
            engine=df.engine,
            base_node=df.base_node,
            index=df.index,
            series={k + 'suffix': v for k, v in df.data.items()},
            group_by=None,
            order_by=[],
            savepoints=Savepoints()
        )

    with pytest.raises(ValueError, match="Group_by in `series` should match dataframe"):
        DataFrame(
            engine=df.engine,
            base_node=df.base_node,
            index=df.index,
            series=df.data,
            group_by=GroupBy([df.b]),
            order_by=[],
            savepoints=Savepoints()
        )

    with pytest.raises(ValueError, match="Base_node in `series` should match dataframe"):
        DataFrame(
            engine=df.engine,
            base_node=other_base_node,
            index=df.index,
            series=df.data,
            group_by=None,
            order_by=[],
            savepoints=Savepoints()
        )

    # df2.c has an index of itself
    other_index = {'a': df2.c}
    with pytest.raises(ValueError, match="Index series can not have non-empty index property"):
        DataFrame(
            engine=df.engine,
            base_node=df.base_node,
            index=other_index,
            series={k: v.copy_override(index=other_index) for k, v in df.data.items()},
            group_by=None,
            order_by=[],
            savepoints=Savepoints()
        )

    other_index = {'b': df.index['a']}
    with pytest.raises(ValueError,
                       match="The names of the index series and data series should not intersect"):
        DataFrame(
            engine=df.engine,
            base_node=df.base_node,
            index=other_index,
            series={k: v.copy_override(index=other_index) for k, v in df.data.items()},
            group_by=None,
            order_by=[],
            savepoints=Savepoints()
        )
    # there are a few __init__ checks that we don't check here, as they are also checked when creating a
    # Series object, and are thus hard to actually trigger.
