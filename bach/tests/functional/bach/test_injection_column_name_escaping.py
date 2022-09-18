"""
Copyright 2021 Objectiv B.V.
"""
import pytest
from sqlalchemy.engine import Engine

from sql_models.util import is_bigquery, is_athena
from tests.functional.bach.test_data_and_utils import assert_equals_data, get_df_with_test_data


def test_column_names(engine):
    # Athena and BigQuery don't allow 'weird' characters, so we just expect an error about the names.
    if is_athena(engine) or is_bigquery(engine):
        with pytest.raises(ValueError, match='Column name ".*" is not valid for SQL dialect'):
            bt = _get_dataframe_with_weird_column_names(engine)
        return
    # Postgres does allow 'weird' characters, if properly escaped. Test the escaping
    bt = _get_dataframe_with_weird_column_names(engine)
    expected_columns = ['_index_skating_order',
                        'city', 'With_Capitals', 'with_capitals',
                        'With A Space Too', '""with"_quotes""', 'with%percentage',
                        'with{format}{{strings}}{{}', 'Aa_!#!$*(aA®Řﬦ‎	⛔']
    expected_data = [
        [1, 'Ljouwert', 1, 1, 1, 1, 1, 1, 1],
        [2, 'Snits',  1, 1, 1, 1, 1, 1, 1],
        [3, 'Drylts',  1, 1, 1, 1, 1, 1, 1]
    ]
    assert_equals_data(bt, expected_columns=expected_columns, expected_data=expected_data)
    # Make sure that after materializing the columns are unchanged.
    bt = bt.materialize()
    assert_equals_data(bt, expected_columns=expected_columns, expected_data=expected_data)


@pytest.mark.skip_bigquery_todo('#1209 We do not yet support special characters in column names on BigQuery')
@pytest.mark.skip_athena_todo('#1209 We do not yet support special characters in column names on Athena')
def test_column_names_merge(engine):
    # When merging we construct a specific sql query that names each column, so test that separately here
    bt = _get_dataframe_with_weird_column_names(engine)
    bt2 = get_df_with_test_data(engine)[['city']]
    bt = bt.merge(bt2, on='city')
    expected_columns = ['_index_skating_order_x', '_index_skating_order_y',
                        'city', 'With_Capitals', 'with_capitals',
                        'With A Space Too', '""with"_quotes""', 'with%percentage',
                        'with{format}{{strings}}{{}', 'Aa_!#!$*(aA®Řﬦ‎	⛔']
    expected_data = [
        [1, 1, 'Ljouwert', 1, 1, 1, 1, 1, 1, 1],
        [2, 2, 'Snits',  1, 1, 1, 1, 1, 1, 1],
        [3, 3, 'Drylts',  1, 1, 1, 1, 1, 1, 1]
    ]
    assert_equals_data(bt, expected_columns=expected_columns, expected_data=expected_data)


def _get_dataframe_with_weird_column_names(engine: Engine):
    bt = get_df_with_test_data(engine)[['city']]
    bt['With_Capitals'] = 1
    bt['with_capitals'] = 1
    bt['With A Space Too'] = 1
    bt['""with"_quotes""'] = 1
    bt['with%percentage'] = 1
    bt['with{format}{{strings}}{{}'] = 1
    bt['Aa_!#!$*(aA®Řﬦ‎	⛔'] = 1
    return bt

# TODO: tests for groupby and windowing
