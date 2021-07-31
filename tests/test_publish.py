from pathlib import Path
from typing import Optional

import pytest

import esparto as es
import esparto._publish as pu
from tests.conftest import _EXTRAS, content_list, layout_list


def html_is_valid(html: Optional[str], fragment: bool = False):
    if _EXTRAS:
        from html5lib import HTMLParser  # type: ignore

        htmlparser = HTMLParser(strict=True)
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
    return True


@pytest.mark.parametrize("content", (*content_list, *layout_list))
def test_content_html_valid(content):
    html = content.to_html()
    assert html_is_valid(html, fragment=True)


def test_rendered_html_valid_cdn(page_layout: es.Page, tmp_path):
    path = str(tmp_path / "my_page.html")
    html = pu.publish_html(page_layout, path, return_html=True, dependency_source="cdn")
    assert html_is_valid(html)


def test_rendered_html_valid_inline(page_layout: es.Page, tmp_path):
    path = str(tmp_path / "my_page.html")
    html = pu.publish_html(
        page_layout, path, return_html=True, dependency_source="inline"
    )
    assert html_is_valid(html)


def test_saved_html_valid_cdn(page_layout: es.Page, tmp_path):
    path: Path = tmp_path / "my_page.html"
    page_layout.save_html(str(path), dependency_source="cdn")
    html = path.read_text()
    assert html_is_valid(html)


def test_saved_html_valid_inline(page_layout: es.Page, tmp_path):
    path: Path = tmp_path / "my_page.html"
    page_layout.save_html(str(path), dependency_source="inline")
    html = path.read_text()
    assert html_is_valid(html)


def test_saved_html_valid_options_cdn(page_layout: es.Page, tmp_path, monkeypatch):
    monkeypatch.setattr(es.options, "dependency_source", "cdn")
    path: Path = tmp_path / "my_page.html"
    page_layout.save_html(str(path))
    html = path.read_text()
    assert html_is_valid(html)


def test_saved_html_valid_options_inline(page_layout: es.Page, tmp_path, monkeypatch):
    monkeypatch.setattr(es.options, "dependency_source", "inline")
    path: Path = tmp_path / "my_page.html"
    page_layout.save_html(str(path))
    html = path.read_text()
    assert html_is_valid(html)


def test_saved_html_valid_bad_source(page_layout: es.Page, tmp_path):
    path: Path = tmp_path / "my_page.html"
    with pytest.raises(ValueError):
        page_layout.save_html(str(path), dependency_source="flapjack")


def test_rendered_html_valid_toc(page_layout: es.Page, tmp_path):
    path = str(tmp_path / "my_page.html")
    page_layout.table_of_contents = True
    html = pu.publish_html(page_layout, path, return_html=True, dependency_source="cdn")
    assert html_is_valid(html)


def test_saved_html_valid_toc(page_layout: es.Page, tmp_path):
    path: Path = tmp_path / "my_page.html"
    page_layout.table_of_contents = True
    page_layout.save_html(str(path), dependency_source="cdn")
    html = path.read_text()
    assert html_is_valid(html)


if _EXTRAS:
    from tests.conftest import content_pdf

    def test_notebook_html_valid_cdn(page_layout):
        html = pu.nb_display(page_layout, return_html=True, dependency_source="cdn")
        assert html_is_valid(html)

    def test_notebook_html_valid_inline(page_layout):
        html = pu.nb_display(page_layout, return_html=True, dependency_source="inline")
        assert html_is_valid(html)

    def test_notebook_html_valid_options_cdn(page_layout, monkeypatch):
        monkeypatch.setattr(es.options, "dependency_source", "cdn")
        html = pu.nb_display(page_layout, return_html=True)
        assert html_is_valid(html)

    def test_notebook_html_valid_online(page_layout, monkeypatch):
        monkeypatch.setattr(es.options, "dependency_source", "inline")
        html = pu.nb_display(page_layout, return_html=True)
        assert html_is_valid(html)

    @pytest.mark.parametrize("content", content_pdf)
    def test_pdf_output(content, tmp_path):
        if "bokeh" not in content._dependencies:
            page = es.Page(children=[content])
            path: Path = tmp_path / "my_page.pdf"
            page.save_pdf(str(path))
            size = path.stat().st_size
            assert size > 1000
