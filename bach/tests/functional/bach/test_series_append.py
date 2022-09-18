import pytest

from bach import Series
from tests.functional.bach.test_data_and_utils import assert_equals_data, get_df_with_test_data


def test_series_append_same_dtype(engine) -> None:
    bt = get_df_with_test_data(engine, full_data_set=False)[['city', 'skating_order']]
    bt.skating_order = bt.skating_order.astype(str)

    result = bt.city.append(bt.skating_order)
    assert isinstance(result, Series)

    assert_equals_data(
        result.sort_values(),
        expected_columns=['_index_skating_order', 'city'],
        expected_data=[
            [1, '1'],
            [2, '2'],
            [3, '3'],
            [3, 'Drylts'],
            [1, 'Ljouwert'],
            [2, 'Snits'],
        ],
    )


@pytest.mark.skip_athena_todo()  # TODO: remove '.0' from stringified float
def test_series_append_different_dtype(engine) -> None:
    bt = get_df_with_test_data(engine, full_data_set=False)[['city', 'inhabitants', 'founding']]
    bt['founding'] = bt['founding'].astype('float64')

    result = bt.city.append(bt.founding)
    assert isinstance(result, Series)

    assert_equals_data(
        result.sort_values(),
        expected_columns=['_index_skating_order', 'city'],
        expected_data=[
            [3, '1268'],
            [1, '1285'],
            [2, '1456'],
            [3, 'Drylts'],
            [1, 'Ljouwert'],
            [2, 'Snits'],
        ]
    )

    result2 = bt.inhabitants.append(bt.founding)
    assert isinstance(result2, Series)

    assert_equals_data(
        result2.sort_values(ascending=False),
        expected_columns=['_index_skating_order', 'inhabitants'],
        expected_data=[
            [1, 93485.],
            [2, 33520.],
            [3, 3055.],
            [2, 1456.],
            [1, 1285.],
            [3, 1268.],
        ],
    )

    result3 = bt.city.append([bt.founding, bt.inhabitants])
    assert_equals_data(
        result3.sort_values(),
        expected_columns=['_index_skating_order', 'city'],
        expected_data=[
            [3, '1268'],
            [1, '1285'],
            [2, '1456'],
            [3, '3055'],
            [2, '33520'],
            [1, '93485'],
            [3, 'Drylts'],
            [1, 'Ljouwert'],
            [2, 'Snits'],
        ]
    )


def test_series_ignore_index(engine) -> None:
    bt = get_df_with_test_data(engine, full_data_set=False)[['city', 'skating_order']]
    bt.skating_order = bt.skating_order.astype(str)

    result = bt.city.append(bt.skating_order, ignore_index=True)
    assert isinstance(result, Series)

    assert_equals_data(
        result.sort_values(),
        expected_columns=['city'],
        expected_data=[
            ['1'],
            ['2'],
            ['3'],
            ['Drylts'],
            ['Ljouwert'],
            ['Snits'],
        ],
    )


def test_append_w_non_materialized_series(engine) -> None:
    bt = get_df_with_test_data(engine, full_data_set=False)[['city', 'skating_order']]

    city_series = bt.city.unique()
    skating_order_series = bt.set_index('city').skating_order

    result = city_series.append(skating_order_series)

    assert_equals_data(
        result.sort_values(),
        expected_columns=['city', 'city_unique'],
        expected_data=[
            ['Ljouwert', '1'],
            ['Snits', '2'],
            ['Drylts', '3'],
            ['Drylts', 'Drylts'],
            ['Ljouwert', 'Ljouwert'],
            ['Snits', 'Snits'],
        ],
    )
