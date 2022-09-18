import pandas as pd
import pytest

from bach import DataFrame
from tests.functional.bach.test_data_and_utils import assert_equals_data


def test_df_basic_drop_duplicates(engine) -> None:
    pdf = pd.DataFrame(
        data={
            'a': [1, 1, 2, 3, 4, 4, 5],
            'b': ['a', 'a', 'b', 'c', 'd', 'e', 'e'],
        }
    )

    df = DataFrame.from_pandas(engine=engine, df=pdf, convert_objects=True)
    result = df.drop_duplicates().sort_index()

    expected_pdf = pd.DataFrame(
        data=[
            [0, 1, 'a'],
            [2, 2, 'b'],
            [3, 3, 'c'],
            [4, 4, 'd'],
            [5, 4, 'e'],
            [6, 5, 'e'],
        ],
        columns=['_index_0', 'a', 'b'],
    )

    assert_equals_data(
        result,
        expected_columns=expected_pdf.columns.tolist(),
        expected_data=expected_pdf.to_numpy().tolist(),
    )
    pd.testing.assert_frame_equal(pdf.drop_duplicates(), result.to_pandas(), check_names=False)

    result_w_ignore_index = df.drop_duplicates(ignore_index=True).sort_values(by=['a', 'b'])
    assert_equals_data(
        result_w_ignore_index,
        expected_columns=['a', 'b'],
        expected_data=expected_pdf[['a', 'b']].to_numpy().tolist(),
    )
    pd.testing.assert_frame_equal(
        pdf.drop_duplicates(ignore_index=True).sort_values(by=['a', 'b']),
        result_w_ignore_index.to_pandas(),
        check_names=False,
    )


def test_df_basic_w_subset_drop_duplicates(engine) -> None:
    pdf = pd.DataFrame(
        data={
            'a': [1, 1, 2, 3, 4, 4, 5],
            'b': ['a', 'a', 'b', 'c', 'd', 'e', 'e'],
            'c': [0, 1, 2, 3, 4, 5, 6]
        }
    )
    subset = ['a', 'b']
    df = DataFrame.from_pandas(engine=engine, df=pdf, convert_objects=True)
    result = df.drop_duplicates(subset=subset).sort_index()

    expected_pdf = pd.DataFrame(
        data=[
            [0, 1, 'a', 0],
            [2, 2, 'b', 2],
            [3, 3, 'c', 3],
            [4, 4, 'd', 4],
            [5, 4, 'e', 5],
            [6, 5, 'e', 6],
        ],
        columns=['_index_0', 'a', 'b', 'c'],
    )

    assert_equals_data(
        result,
        expected_columns=expected_pdf.columns.tolist(),
        expected_data=expected_pdf.to_numpy().tolist(),
    )
    pd.testing.assert_frame_equal(pdf.drop_duplicates(subset), result.to_pandas(), check_names=False)

    result_w_ignore_index = df.drop_duplicates(subset=subset, ignore_index=True).sort_values(by='c')
    assert_equals_data(
        result_w_ignore_index,
        expected_columns=['a', 'b', 'c'],
        expected_data=expected_pdf[['a', 'b', 'c']].to_numpy().tolist(),
    )
    pd.testing.assert_frame_equal(
        pdf.drop_duplicates(subset, ignore_index=True).sort_values(by='c'),
        result_w_ignore_index.to_pandas(),
        check_names=False,
    )


def test_df_keep_last_drop_duplicates(engine) -> None:
    pdf = pd.DataFrame(
        data={
            'a': [1, 1, 1, 3, 4, 1, 1],
            'b': ['a', 'b', 'b', 'c', 'd', 'a', 'a'],
        }
    )
    df = DataFrame.from_pandas(engine=engine, df=pdf, convert_objects=True)
    result = df.drop_duplicates(keep='last').sort_index()

    expected_df = pd.DataFrame(
        data=[
            [2, 1, 'b'],
            [3, 3, 'c'],
            [4, 4, 'd'],
            [6, 1, 'a'],
        ],
        columns=['_index_0', 'a', 'b'],
    )
    assert_equals_data(
        result,
        expected_columns=expected_df.columns.tolist(),
        expected_data=expected_df.to_numpy().tolist(),
    )
    pd.testing.assert_frame_equal(
        pdf.drop_duplicates(keep='last'),
        result.to_pandas(),
        check_names=False,
    )

    subset = ['a', 'b']
    result_w_ignore_index = df.drop_duplicates(keep='last', ignore_index=True).sort_values(by=subset)
    expected_df2 = expected_df[subset].sort_values(by=subset)
    assert_equals_data(
        result_w_ignore_index,
        expected_columns=subset,
        expected_data=expected_df2.to_numpy().tolist(),
    )
    pd.testing.assert_frame_equal(
        pdf[subset].drop_duplicates(keep='last', ignore_index=True).sort_values(by=subset).reset_index(drop=True),
        result_w_ignore_index.to_pandas(),
        check_names=False,
    )


def test_df_drop_all_duplicates(engine) -> None:
    pdf = pd.DataFrame(
        data={
            'a': [1, 1, 1, 3, 4, 1, 1],
            'b': ['a', 'b', 'b', 'c', 'd', 'a', 'a'],
        }
    )
    df = DataFrame.from_pandas(engine=engine, df=pdf, convert_objects=True)

    result = df.drop_duplicates(keep=False).sort_index()

    assert_equals_data(
        result,
        expected_columns=['_index_0', 'a', 'b'],
        expected_data=[
            [3, 3, 'c'],
            [4, 4, 'd'],
        ],
    )
    pd.testing.assert_frame_equal(pdf.drop_duplicates(keep=False), result.to_pandas(), check_names=False)

    result_w_no_index = df.drop_duplicates(keep=False, ignore_index=True).sort_values(by='a')
    assert_equals_data(
        result_w_no_index,
        expected_columns=['a', 'b'],
        expected_data=[
            [3, 'c'],
            [4, 'd'],
        ],
    )
    pd.testing.assert_frame_equal(
        pdf.sort_values(by='a').drop_duplicates(keep=False, ignore_index=True),
        result_w_no_index.to_pandas(),
        check_names=False,
    )


def test_drop_duplicates_w_sorting(engine) -> None:
    pdf = pd.DataFrame(
        data={
            'a': [1, 1, 1, 3, 4, 1, 1],
            'b': ['a', 'b', 'b', 'c', 'd', 'a', 'a'],
            'c': [1, 1, 2, 1, 1, 1, 2],
            'd': ['a', 'b', 'c', 'd', 'e', 'f', 'g'],
        },
    )

    df = DataFrame.from_pandas(engine=engine, df=pdf, convert_objects=True)
    result = df.drop_duplicates(subset=['a', 'b'], sort_by=['c'], ascending=False)

    assert_equals_data(
        result.sort_index(),
        expected_columns=['_index_0', 'a', 'b', 'c', 'd'],
        expected_data=[
            [2, 1, 'b', 2, 'c'],
            [3, 3, 'c', 1, 'd'],
            [4, 4, 'd', 1, 'e'],
            [6, 1, 'a', 2, 'g'],
        ],
    )

    result2 = df.sort_values(by='d').drop_duplicates(subset=['a', 'b'])
    assert_equals_data(
        result2.sort_index(),
        expected_columns=['_index_0', 'a', 'b', 'c', 'd'],
        expected_data=[
            [0, 1, 'a', 1, 'a'],
            [1, 1, 'b', 1, 'b'],
            [3, 3, 'c', 1, 'd'],
            [4, 4, 'd', 1, 'e'],
        ],
    )


def test_errors_drop_duplicates(engine) -> None:
    pdf = pd.DataFrame(
        data={
            'a': [1, 1, 1, 3, 4, 1, 1],
            'b': ['a', 'b', 'b', 'c', 'd', 'a', 'a'],
        }
    )
    df = DataFrame.from_pandas(engine=engine, df=pdf, convert_objects=True)
    with pytest.raises(ValueError, match=r'keep must be either'):
        df.drop_duplicates(keep='random')

    with pytest.raises(ValueError, match=r'subset param contains'):
        df.drop_duplicates(subset='random')
