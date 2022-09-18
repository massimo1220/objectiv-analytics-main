"""
Copyright 2022 Objectiv B.V.
"""
import pytest

from bach.from_database import _get_bq_meta_data_table_from_table_name


@pytest.mark.db_independent('Function under test always assumes BQ; does not need dialect or engine param')
def test__get_bq_meta_data_table_from_table_name():
    assert _get_bq_meta_data_table_from_table_name('test_table') == ('INFORMATION_SCHEMA.COLUMNS', 'test_table')
    assert _get_bq_meta_data_table_from_table_name('dataset.test_table') == \
           ('dataset.INFORMATION_SCHEMA.COLUMNS', 'test_table')
    assert _get_bq_meta_data_table_from_table_name('project_id.dataset.test_table') == \
           ('project_id.dataset.INFORMATION_SCHEMA.COLUMNS', 'test_table')
    assert _get_bq_meta_data_table_from_table_name('objectiv-production.a-dataset.a_table') == \
           ('objectiv-production.a-dataset.INFORMATION_SCHEMA.COLUMNS', 'a_table')
