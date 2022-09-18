"""
Copyright 2022 Objectiv B.V.
"""
import pytest

from bach.expression import Expression
from bach.sql_model import BachSqlModel
from sql_models.model import CustomSqlModelBuilder, Materialization


@pytest.mark.db_independent
def test_bach_sql_model_copy():
    # test that if we call a function that should return a copy on a BachSqlModel instance, that we get
    # a BachSqlModel instance again.
    model = BachSqlModel(
        model_spec=CustomSqlModelBuilder(sql='SELECT * FROM test where b = {val}', name='test'),
        placeholders={'val': 123},
        references={},
        materialization=Materialization.CTE,
        materialization_name=None,
        column_expressions={
            'a': Expression.column_reference('a'),
            'b': Expression.column_reference('b'),
        },
    )
    assert model.placeholders == {'val': 123}
    assert model.__class__ == BachSqlModel

    model = model.copy_set({'val': 234})
    assert model.placeholders == {'val': 234}
    assert model.__class__ == BachSqlModel

    model = model.set(tuple(), val=345)
    assert model.placeholders == {'val': 345}
    assert model.__class__ == BachSqlModel
