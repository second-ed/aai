from contextlib import nullcontext as does_not_raise

import pytest

from src.aai.data_structures import ImageLink, MarkdownPoint


@pytest.fixture
def get_markdown_point_instance() -> MarkdownPoint:
    return MarkdownPoint("1.1.1", "this is a point", "www.some.source")


@pytest.fixture
def get_image_link_instance() -> ImageLink:
    return ImageLink("1.1", "some_image.png", "www.someother_site.com")


@pytest.mark.parametrize(
    "fixture_name, refs, expected_result, expected_context",
    [
        pytest.param(
            "get_markdown_point_instance",
            {},
            "This is a point [[1]](www.some.source). ",
            does_not_raise(),
        ),
        pytest.param(
            "get_markdown_point_instance",
            {"site_1": 1},
            "This is a point [[2]](www.some.source). ",
            does_not_raise(),
        ),
        pytest.param(
            "get_image_link_instance",
            {},
            "![image](some_image.png) [[1]](www.someother_site.com)\n\n",
            does_not_raise(),
        ),
        pytest.param(
            "get_image_link_instance",
            {"image_1": 1},
            "![image](some_image.png) [[2]](www.someother_site.com)\n\n",
            does_not_raise(),
        ),
    ],
)
def test_create_source_link(
    request, fixture_name, refs, expected_result, expected_context
) -> None:
    with expected_context:
        point = request.getfixturevalue(fixture_name)
        assert point.create_source_link(refs) == expected_result


