"""
Copyright 2022 Objectiv B.V.
"""
import pytest

from bach.from_pandas import _assert_column_names_valid
from tests.unit.bach.test_utils import ColNameValid
from tests.unit.bach.util import get_pandas_df


def test__assert_column_names_valid_generic(dialect):
    # check for duplicates and for non-named columns
    data = [[1, 2, 3], [3, 4, 5]]
    column_names = ['a', 'b', 'c']
    pdf = get_pandas_df(dataset=data, columns=column_names)
    # OK, columns are 'a', 'b', and 'c'
    _assert_column_names_valid(dialect=dialect, df=pdf)

    # Not OK: column name 'a' appears twice
    pdf.columns = ['a', 'b', 'a']
    with pytest.raises(ValueError, match='Duplicate column names'):
        _assert_column_names_valid(dialect=dialect, df=pdf)

    # Not OK: column names are not all strings
    pdf.columns = ['a', 'b', 0]
    with pytest.raises(ValueError, match='Not all columns names are strings'):
        _assert_column_names_valid(dialect=dialect, df=pdf)


    # Not OK: second column has no name
    pdf.columns = ['a', None, 'c']
    with pytest.raises(ValueError, match='Not all columns names are strings'):
        _assert_column_names_valid(dialect=dialect, df=pdf)


def test__assert_column_names_valid_db_specific(dialect):
    # test whether column names are allowed for specific dialects
    # We'll just test a few combinations here
    tests = [
        #            column name              PG    Athena BQ
        ColNameValid('test',                  True,  True,  True),
        ColNameValid('test' * 15 + 'test',    False, True,  True),   # 64 characters
        ColNameValid('abcdefghij' * 30 + 'a', False, False, False),  # 301 characters
        ColNameValid('#@*&O*JALDSJK',         True,  False, False),
    ]
    for test in tests:
        data = [[1, 2, 3], [3, 4, 5]]
        column_names = ['a', 'b', test.name]
        pdf = get_pandas_df(dataset=data, columns=column_names)
        expected = getattr(test, dialect.name)
        if expected:
            _assert_column_names_valid(dialect=dialect, df=pdf)
        else:
            with pytest.raises(ValueError, match='Invalid column names: .* for SQL dialect'):
                _assert_column_names_valid(dialect=dialect, df=pdf)
