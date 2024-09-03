from contextlib import nullcontext as does_not_raise

import pytest

from src.aai import utils


@pytest.mark.parametrize(
    "src, idx, dst, expected_result, expected_context",
    [
        pytest.param(
            "root/sub1/sub2/sub3/file.ext",
            0,
            "some_other_file.ext",
            "root/sub1/sub2/sub3/some_other_file.ext",
            does_not_raise(),
        ),
        pytest.param(
            "root/sub1/sub2/sub3/file.ext",
            1,
            "some_other_file.ext",
            "root/sub1/sub2/some_other_file.ext",
            does_not_raise(),
        ),
        pytest.param(
            "root/sub1/sub2/sub3/file.ext",
            2,
            "some_other_file.ext",
            "root/sub1/some_other_file.ext",
            does_not_raise(),
        ),
    ],
)
def test_get_dir_path(
    src, idx, dst, expected_result, expected_context
) -> None:
    with expected_context:
        assert utils.get_dir_path(src, idx, dst) == expected_result


@pytest.mark.parametrize(
    "col, expected, expected_context",
    [
        pytest.param(
            "Column Name",
            "column_name",
            does_not_raise(),
            id="basic spaces",
        ),
        pytest.param(
            "Column@Name!",
            "columnname",
            does_not_raise(),
            id="special characters",
        ),
        pytest.param(
            "  Column Name  ",
            "column_name",
            does_not_raise(),
            id="leading and trailing spaces",
        ),
        pytest.param(
            "cOLuMn NamE",
            "column_name",
            does_not_raise(),
            id="mixed case",
        ),
        pytest.param(
            "Column1 Name2",
            "column1_name2",
            does_not_raise(),
            id="numbers",
        ),
        pytest.param(
            "Column_Name",
            "column_name",
            does_not_raise(),
            id="underscores",
        ),
        pytest.param(
            "Column   Name",
            "column_name",
            does_not_raise(),
            id="multiple spaces",
        ),
        pytest.param(
            "123_456",
            "123_456",
            does_not_raise(),
            id="no alphabetic characters",
        ),
        pytest.param("", "", does_not_raise(), id="empty string"),
        pytest.param(
            "Column名稱",
            "column",
            does_not_raise(),
            id="non-latin characters",
        ),
        pytest.param(
            1,
            None,
            pytest.raises(TypeError),
            id="raise TypeError",
        ),
    ],
)
def test_clean_column(col, expected, expected_context) -> None:
    with expected_context:
        assert utils._clean_column(col) == expected


@pytest.mark.parametrize(
    "cols, expected, expected_context",
    [
        (["col!", "col2 "], ["col", "col2"], does_not_raise()),
        pytest.param(
            1,
            None,
            pytest.raises(TypeError),
            id="raise TypeError",
        ),
    ],
)
def test_clean_columns(cols, expected, expected_context) -> None:
    with expected_context:
        assert utils._clean_columns(cols) == expected
