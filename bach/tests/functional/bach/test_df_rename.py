"""
Copyright 2021 Objectiv B.V.
"""
from sql_models.util import is_bigquery, is_athena
from tests.functional.bach.test_data_and_utils import assert_equals_data, get_df_with_test_data

EXPECTED_DATA = [
    [1, 1, 'Ljouwert', 'Leeuwarden', 93485, 1285],
    [2, 2, 'Snits', 'Súdwest-Fryslân', 33520, 1456],
    [3, 3, 'Drylts', 'Súdwest-Fryslân', 3055, 1268]
]


def test_rename_basic(engine):
    bt = get_df_with_test_data(engine)
    nbt = bt.rename(columns={'city': 'stad'})
    nnbt = nbt.rename(columns={'stad': 'city'})

    expected_cols_original = ['_index_skating_order', 'skating_order', 'city', 'municipality', 'inhabitants', 'founding']
    expected_cols_changed = ['_index_skating_order', 'skating_order', 'stad', 'municipality', 'inhabitants', 'founding']

    assert_equals_data(bt, expected_columns=expected_cols_original, expected_data=EXPECTED_DATA)
    assert_equals_data(nbt, expected_columns=expected_cols_changed, expected_data=EXPECTED_DATA)
    assert_equals_data(nnbt, expected_columns=expected_cols_original, expected_data=EXPECTED_DATA)


def test_rename_complex(engine):
    # test: mapping function, mapping to same name, and circular mapping
    # test on non-bigquery: to name with 'special character'
    bt = get_df_with_test_data(engine)

    new_name = 'stêd'
    if is_athena(engine) or is_bigquery(engine):
        # Athena and BigQuery limit the allowed column names.
        # See also tests.unit.bach.test_utils.test_is_valid_column_name
        new_name = 'stad'

    def rename_func(old: str) -> str:
        if old == 'city':
            return new_name
        if old == 'municipality':
            return 'founding'
        if old == 'founding':
            return 'municipality'
        return old

    nbt = bt.rename(columns=rename_func)
    assert_equals_data(
        nbt,
        expected_columns=['_index_skating_order', 'skating_order', new_name, 'founding', 'inhabitants', 'municipality'],
        expected_data=EXPECTED_DATA
    )
