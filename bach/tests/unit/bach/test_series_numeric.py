"""
Copyright 2022 Objectiv B.V.
"""
import pytest

from tests.unit.bach.util import get_fake_df_test_data


def test_dataframe_agg_dd_parameter(dialect):
    # test full parameter traversal
    bt = get_fake_df_test_data(dialect)[['inhabitants']]

    for agg in ['sem', 'std', 'var']:
        with pytest.raises(NotImplementedError):
            # currently not supported anywhere, so needs to raise
            bt.agg(agg, ddof=123)


def test_dataframe_agg_skipna_parameter(dialect):
    # test full parameter traversal
    bt = get_fake_df_test_data(dialect)[['inhabitants']]

    numeric_agg = ['sum', 'mean']
    stats_agg = ['sem', 'std', 'var']
    for agg in numeric_agg + stats_agg:
        with pytest.raises(NotImplementedError):
            # currently not supported anywhere, so needs to raise
            bt.agg(agg, skipna=False)

    numeric_agg = ['prod', 'product']
    stats_agg = ['kurt', 'kurtosis', 'skew', 'mad']
    for agg in numeric_agg + stats_agg:
        with pytest.raises(AttributeError):
            # methods not present at all, so needs to raise
            bt.agg(agg, skipna=False)
