"""
Copyright 2022 Objectiv B.V.
"""
import pytest

from tests.unit.bach.util import get_fake_df_test_data


def test_df_plot_hist_no_numeric_columns(dialect):
    bt = get_fake_df_test_data(dialect)[['city', 'municipality']]

    with pytest.raises(ValueError, match=r'hist method requires numerical columns, nothing to plot.'):
        bt.plot.hist()


def test_df_plot_hist_by_error(dialect):
    bt = get_fake_df_test_data(dialect)

    with pytest.raises(NotImplementedError, match=r'currently not supported'):
        bt.plot.hist(by='city')
