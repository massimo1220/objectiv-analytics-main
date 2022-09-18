import pytest

from bach.operations.concat import DataFrameConcatOperation, SeriesConcatOperation
from bach.expression import Expression
from tests.unit.bach.util import get_fake_df


@pytest.mark.db_independent
def test_concat_empty_objects() -> None:
    with pytest.raises(ValueError, match=r'no objects to concat'):
        DataFrameConcatOperation(objects=[])()

    with pytest.raises(ValueError, match=r'no objects to concat'):
        SeriesConcatOperation(objects=[])()


def test_concat_one_object(dialect) -> None:
    df = get_fake_df(dialect, [], ['b', 'c'])
    result = DataFrameConcatOperation(objects=[df])()

    assert df.all_series == result.all_series

    result2 = DataFrameConcatOperation(objects=[df.b])()

    assert df.b.dtype == result2.dtype
    assert df.b.expression == result2.expression


def test_get_overridden_objects_error(dialect) -> None:
    df = get_fake_df(dialect, [], ['c', 'd'])
    with pytest.raises(Exception, match='Cannot concat Series to DataFrame'):
        DataFrameConcatOperation(objects=[df, df.c])._get_overridden_objects()

    with pytest.raises(Exception, match='Cannot concat DataFrame to Series'):
        SeriesConcatOperation(objects=[df, df.c])._get_overridden_objects()


def test_dataframe_concat_join_series_expressions(dialect) -> None:
    df1 = get_fake_df(dialect, ['a'], ['b'])
    df2 = get_fake_df(dialect, ['a'], ['b', 'e'])
    result = DataFrameConcatOperation(objects=[df1, df2])._join_series_expressions(df1)

    assert isinstance(result, Expression)
    assert len(result.data) == 5


def test_dataframe_concat_get_indexes(dialect) -> None:
    df1 = get_fake_df(dialect, ['a'], ['b'])
    df2 = get_fake_df(dialect, ['a', 'b'], ['c', 'd'])

    with pytest.raises(ValueError, match=r'concatenation with diff'):
        DataFrameConcatOperation(objects=[df1, df2])._get_indexes()

    df2 = df2.reset_index(level='b', drop=False)
    result = DataFrameConcatOperation(objects=[df1, df2])._get_indexes()
    assert set(result.keys()) == {'a'}


def test_dataframe_concat_get_series(dialect) -> None:
    df1 = get_fake_df(dialect, [], ['a', 'x', 'y'])
    df2 = get_fake_df(dialect, [], ['c', 'd'])

    result = DataFrameConcatOperation(objects=[df1, df2])._get_series()
    assert set(result.keys()) == {'a', 'x', 'y', 'c', 'd'}
