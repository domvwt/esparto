import pytest
from typing import Optional

from html5lib import HTMLParser

from tests.conftest import content_list, layout_list

import esparto._publish as pu

htmlparser = HTMLParser(strict=True)


def html_is_valid(html: Optional[str], fragment: bool = False):
    try:
        if fragment:
            htmlparser.parseFragment(html)
        else:
            htmlparser.parse(html)
        success = True
    except Exception as e:
        print(e)
        success = False
    return success


@pytest.mark.parametrize("content", (*content_list, *layout_list))
def test_content_html_valid(content):
    html = content.to_html()
    assert html_is_valid(html, fragment=True)


def test_rendered_html_valid(page_layout, tmp_path):
    path = str(tmp_path / "my_page.html")
    html = pu.publish(page_layout, path, return_html=True)
    assert html_is_valid(html)


def test_saved_html_valid(page_layout, tmp_path):
    path = str(tmp_path / "my_page.html")
    page_layout.save(path)
    with open(path, "r") as f:
        html = f.read()
    assert html_is_valid(html)


def test_notebook_html_valid(page_layout):
    html = pu.nb_display(page_layout, return_html=True)
    assert html_is_valid(html, fragment=True)
