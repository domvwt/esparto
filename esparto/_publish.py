"""Functions that render and save documents."""

import time
from pathlib import Path
from typing import TYPE_CHECKING, Optional, Union

from jinja2 import Template  # type: ignore

if TYPE_CHECKING:
    from esparto._layout import Page, Layout
    from esparto._content import Content

from esparto import _INSTALLED_MODULES
from esparto._contentdeps import resolve_deps
from esparto._options import options, resolve_config_option


def publish_html(
    page: "Page",
    filepath: Optional[str] = "./esparto-doc.html",
    return_html: bool = False,
    dependency_source: str = None,
    esparto_css: str = None,
    jinja_template: str = None,
    **kwargs,
) -> Optional[str]:
    """Save page to HTML.

    Args:
      page (Page): A Page object.
      filepath (str): Filepath to write to.
      return_html (bool): Returns HTML string if True.
      dependency_source (str): One of 'cdn' or 'inline' (default = None).
      esparto_css (str): Path to CSS stylesheet. (default = None).
      jinja_template (str): Path to Jinja template. (default = None).
      **kwargs (Dict[str, Any]): Arguments passed to `page.to_html()`.

    Returns:
      str: HTML string if return_html is True.

    """

    required_deps = page._required_dependencies()
    dependency_source = dependency_source or options.dependency_source
    resolved_deps = resolve_deps(required_deps, source=dependency_source)

    esparto_css = Path(resolve_config_option("esparto_css", esparto_css)).read_text()
    jinja_template_loaded = Template(
        Path(resolve_config_option("jinja_template", jinja_template)).read_text()
    )

    html_rendered: str = jinja_template_loaded.render(
        navbrand=page.navbrand,
        doc_title=page.title,
        esparto_css=esparto_css,
        content=page.to_html(**kwargs),
        head_deps=resolved_deps.head,
        tail_deps=resolved_deps.tail,
    )
    html_prettified = _prettify_html(html_rendered)

    if filepath:
        with open(filepath, "w") as f:
            f.write(html_prettified)

    if return_html:
        return html_prettified
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
    import weasyprint as weasy  # type: ignore

    temp_dir = Path(options._pdf_temp_dir)
    temp_dir.mkdir(parents=True, exist_ok=True)

    html_rendered = publish_html(
        page=page,
        filepath=None,
        return_html=True,
        dependency_source="inline",
        pdf_mode=True,
    )
    pdf_doc = weasy.HTML(string=html_rendered, base_url=options._pdf_temp_dir).render()
    pdf_doc.metadata.title = page.title
    pdf_doc.write_pdf(filepath)

    for f in temp_dir.iterdir():
        f.unlink()
    temp_dir.rmdir()

    html_prettified = _prettify_html(html_rendered)

    if return_html:
        return html_prettified
    return None


def nb_display(
    item: Union["Layout", "Content"],
    return_html: bool = False,
    dependency_source: str = None,
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

    from esparto._layout import Layout

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
    render_html = (
        f"<div class='container' style='width: 100%; height: 100%;'>\n{html}\n</div>\n"
    )
    render_html += f"<style>\n{esparto_css}\n</style>\n"

    render_html = (
        f"<!doctype html>\n<html>\n<head>{head_deps}</head>\n"
        f"<body>\n{render_html}\n{tail_deps}\n</body>\n</html>\n"
    )

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

    display(HTML(extra_css + render_html), metadata=dict(isolated=True))
    print()

    if return_html:
        return render_html
    return None


def _prettify_html(html: Optional[str]) -> str:
    """Prettify HTML."""
    if "bs4" in _INSTALLED_MODULES:
        from bs4 import BeautifulSoup  # type: ignore

        html = html or ""
        html = str(BeautifulSoup(html, features="html.parser").prettify())

    return html or ""
