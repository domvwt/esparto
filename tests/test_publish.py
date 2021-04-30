from pathlib import Path
from typing import Optional

import pytest
from html5lib import HTMLParser  # type: ignore

import esparto as es
import esparto._publish as pu
from tests.conftest import _EXTRAS, content_list, layout_list

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
    html = pu.publish_html(page_layout, path, return_html=True)
    assert html_is_valid(html)


def test_saved_html_valid(page_layout, tmp_path):
    path: Path = tmp_path / "my_page.html"
    page_layout.save_html(str(path))
    html = path.read_text()
    assert html_is_valid(html)


if _EXTRAS:

    def test_notebook_html_valid(page_layout):
        html = pu.nb_display(page_layout, return_html=True)
        assert html_is_valid(html)

    def test_pdf_output(content_list_fn, tmp_path):
        content_list = [x for x in content_list_fn if not pu.JS_DEPS & x._deps]
        page = es.Page(content_list)
        path: Path = tmp_path / "my_page.pdf"
        page.save_pdf(str(path))
        size = path.stat().st_size
        assert size > 500_000
