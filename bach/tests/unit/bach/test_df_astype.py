"""
Copyright 2022 Objectiv B.V.
"""
import numpy

from tests.unit.bach.util import get_fake_df_test_data


def test_astype_dtype_aliases(dialect):
    bt = get_fake_df_test_data(dialect)
    bt = bt[['inhabitants']]
    # Using an alias of 'int64' in the call to `astype()` should result in the same DataFrame
    bt_int0 = bt.astype('int64')
    bt_int1 = bt.astype('bigint')
    bt_int2 = bt.astype(int)
    bt_int3 = bt.astype(numpy.int64)
    assert bt_int0 == bt_int1
    assert bt_int0 == bt_int2
    assert bt_int0 == bt_int3
