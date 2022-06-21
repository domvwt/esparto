"""Functions that render and save documents."""

import time
from pathlib import Path
from typing import TYPE_CHECKING, Optional, Union

from bs4 import BeautifulSoup, Tag  # type: ignore
from jinja2 import Template

from esparto import _INSTALLED_MODULES
from esparto._options import options, resolve_config_option
from esparto.design.base import AbstractContent, AbstractLayout
from esparto.publish.contentdeps import resolve_deps

if TYPE_CHECKING:
    from esparto.design.layout import Page


def publish_html(
    page: "Page",
    filepath: Optional[str] = "./esparto-doc.html",
    return_html: bool = False,
    dependency_source: Optional[str] = None,
    esparto_css: Optional[str] = None,
    esparto_js: Optional[str] = None,
    jinja_template: Optional[str] = None,
    **kwargs: bool,
) -> Optional[str]:
    """Save page to HTML.

    Args:
      page (Page): A Page object.
      filepath (str): Filepath to write to.
      return_html (bool): Returns HTML string if True.
      dependency_source (str): One of 'cdn' or 'inline' (default = None).
      esparto_css (str): Path to CSS stylesheet. (default = None).
      esparto_js (str): Path to JavaScript code. (default = None).
      jinja_template (str): Path to Jinja template. (default = None).
      **kwargs (Dict[str, Any]): Arguments passed to `page.to_html()`.

    Returns:
      str: HTML string if return_html is True.

    """

    required_deps = page._required_dependencies()
    dependency_source = dependency_source or options.dependency_source
    resolved_deps = resolve_deps(required_deps, source=dependency_source)

    esparto_css = Path(resolve_config_option("esparto_css", esparto_css)).read_text()
    esparto_js = Path(resolve_config_option("esparto_js", esparto_js)).read_text()

    page_html = page.to_html(**kwargs)
    jinja_template_object = Template(
        Path(resolve_config_option("jinja_template", jinja_template)).read_text()
    )
    html_rendered: str = jinja_template_object.render(
        navbrand=page.navbrand,
        doc_title=page.title,
        esparto_css=esparto_css,
        esparto_js=esparto_js,
        content=page_html,
        head_deps=resolved_deps.head,
        tail_deps=resolved_deps.tail,
    )
    html_rendered = prettify_html(html_rendered)
    html_rendered = relocate_scripts(html_rendered)

    if filepath:
        Path(filepath).write_text(html_rendered)

    if return_html:
        return html_rendered
    return None


def publish_pdf(
    page: "Page", filepath: str = "./esparto-doc.pdf", return_html: bool = False
) -> Optional[str]:
    """Save page to PDF.

    Args:
      page (Layout): A Page object.
      filepath (str): Filepath to write to.
      return_html (bool): Returns HTML string if True.

    Returns:
      str: HTML string if return_html is True.

    """
    if "weasyprint" not in _INSTALLED_MODULES:
        raise ModuleNotFoundError("Install weasyprint for PDF support")
    import weasyprint as wp  # type: ignore

    temp_dir = Path(options._pdf_temp_dir)
    temp_dir.mkdir(parents=True, exist_ok=True)

    html_rendered = publish_html(
        page=page,
        filepath=None,
        return_html=True,
        dependency_source="inline",
        pdf_mode=True,
    )
    pdf_doc = wp.HTML(string=html_rendered, base_url=options._pdf_temp_dir).render()
    pdf_doc.metadata.title = page.title
    pdf_doc.write_pdf(filepath)

    for f in temp_dir.iterdir():
        f.unlink()
    temp_dir.rmdir()

    html_prettified = prettify_html(html_rendered)

    if return_html:
        return html_prettified
    return None


def nb_display(
    item: Union["AbstractLayout", "AbstractContent"],
    return_html: bool = False,
    dependency_source: Optional[str] = None,
) -> Optional[str]:
    """Display Layout or Content to Jupyter Notebook cell.

    Args:
      item (Layout, Content): A Layout or Content item.
      return_html (bool): Returns HTML string if True.
      dependency_source (str): One of 'cdn', 'inline', or 'esparto.options'.

    Returns:
      str: HTML string if return_html is True.

    """
    from IPython.display import HTML, display  # type: ignore

    from esparto.design.layout import Layout

    if isinstance(item, Layout):
        required_deps = item._required_dependencies()
    else:
        required_deps = getattr(item, "_dependencies", set())

    dependency_source = dependency_source or options.dependency_source
    resolved_deps = resolve_deps(required_deps, source=dependency_source)
    esparto_css = Path(options.esparto_css).read_text()
    head_deps = "\n".join(resolved_deps.head)
    tail_deps = "\n".join(resolved_deps.tail)
    html = item.to_html(notebook_mode=True)
    html_rendered = (
        f"<div class='container' style='width: 100%; height: 100%;'>\n{html}\n</div>\n"
    )
    html_rendered += f"<style>\n{esparto_css}\n</style>\n"

    html_rendered = (
        f"<!doctype html>\n<html>\n<head>{head_deps}</head>\n"
        f"<body>\n{html_rendered}\n{tail_deps}\n</body>\n</html>\n"
    )
    html_rendered = relocate_scripts(html_rendered)
    print()

    # This allows time to download plotly.js from the CDN - otherwise cell can render empty
    if "plotly" in required_deps and dependency_source == "cdn":
        display(HTML(f"<head>\n{head_deps}\n</head>\n"), metadata=dict(isolated=True))
        time.sleep(2)

    # Temporary solution to prevent Jupyter Notebook cell fully collapsing before content renders
    if "bokeh" in required_deps:
        extra_css = "<style>.container { min-height: 30em !important; }</style>"
    else:
        extra_css = ""

    display(HTML(extra_css + html_rendered), metadata=dict(isolated=True))
    print()

    if return_html:
        return html_rendered
    return None


def prettify_html(html: Optional[str]) -> str:
    """Prettify HTML."""
    html = html or ""
    html = str(BeautifulSoup(html, features="html.parser").prettify())

    return html


def relocate_scripts(html: str) -> str:
    """Move all JavaScript in page body to end of section."""
    soup = BeautifulSoup(html, "html.parser")
    body = soup.find("body")

    if isinstance(body, Tag):
        script_list = body.find_all("script")
        for script in script_list:
            body.insert(len(body), script)

    html = str(soup)

    return html
