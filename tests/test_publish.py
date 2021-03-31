import pytest

from tests.conftest import content_list, layout_list


@pytest.mark.parametrize("content", (*content_list, *layout_list))
def test_content_html_valid(content, htmlparser):
    try:
        htmlparser.parseFragment(content.to_html())
        success = True
    except Exception as e:
        print(e)
        success = False
    assert success


def test_output_html_valid(page_layout, tmp_path, htmlparser):
    path = str(tmp_path / "my_page.html")
    page_layout.save(path)
    with open(path, "r") as f:
        try:
            htmlparser.parse(f)
            success = True
        except Exception as e:
            print(e)
            success = False
    assert success
