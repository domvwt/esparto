import time
from typing import TYPE_CHECKING, Optional, Union

from jinja2 import Environment, PackageLoader, select_autoescape  # type: ignore

if TYPE_CHECKING:
    from esparto._layout import Layout
    from esparto._content import Content

from esparto import _INSTALLED_MODULES
from esparto._contentdeps import JS_DEPS, resolve_deps

_ENV = Environment(
    loader=PackageLoader("esparto", "resources/jinja"),
    autoescape=select_autoescape(["xml"]),
)

_BASE_TEMPLATE = _ENV.get_template("base.html")


def publish_html(
    document: "Layout",
    filepath: Optional[str] = "./esparto-doc.html",
    return_html: bool = False,
    dependency_source="cdn",
) -> Optional[str]:
    """Save document to HTML.

    Args:
      document (Layout): Any Layout object.
      filepath (str): Filepath to write to. (default = './esparto-doc.html')
      return_html (bool): Returns HTML string if True.

    Returns:
      str: HTML string if return_html is True.

    """

    required_deps = document._required_dependencies()
    resolved_deps = resolve_deps(required_deps, source=dependency_source)
    head_deps = resolved_deps.head
    tail_deps = resolved_deps.tail

    # Jinja requires dict for accessing properties
    doc_dict = document.to_dict()
    html_rendered: str = _BASE_TEMPLATE.render(
        content=doc_dict, head_deps=head_deps, tail_deps=tail_deps
    )
    html_prettified = _prettify_html(html_rendered)

    if filepath:
        with open(filepath, "w") as f:
            f.write(html_prettified)

    if return_html:
        return html_prettified
    else:
        return None


def publish_pdf(
    document: "Layout",
    filepath: str = "./esparto-doc.pdf",
) -> None:
    """Save document to PDF.

    Args:
      document (Layout): Any Layout object.
      filepath (str): Filepath to write to. (default = './esparto-doc.pdf')

    """
    if "weasyprint" not in _INSTALLED_MODULES:
        raise ModuleNotFoundError("Install weasyprint for PDF support")
    else:
        import weasyprint as weasy  # type: ignore

        doc_js_deps = JS_DEPS & document._required_dependencies()
        if doc_js_deps:
            raise NotImplementedError(
                f"PDF format unsupported for interactive content - document requires: {doc_js_deps}"
            )

        html = publish_html(
            document=document,
            filepath=None,
            return_html=True,
            dependency_source="inline",
        )
        weasy.HTML(string=html).write_pdf(filepath)


def nb_display(
    item: Union["Layout", "Content"], return_html: bool = False
) -> Optional[str]:
    """Display Layout or Content to Jupyter Notebook cell.

    Args:
      item (Layout, Content): A Layout or Content item.
      return_html (bool): Returns HTML string if True.

    Returns:
      str: HTML string if return_html is True.

    """
    from IPython.display import HTML, Javascript, display  # type: ignore

    from esparto._layout import Layout

    required_deps: set = set()

    if isinstance(item, Layout):
        required_deps = item._required_dependencies()
    elif hasattr(item, "_dependencies"):
        required_deps = item._dependencies

    resolved_deps = resolve_deps(required_deps)
    head_deps = "\n".join(resolved_deps.head)
    tail_deps = "\n".join(resolved_deps.tail)
    content_html = f"<div class='container' style='width: 100%; height: 100%;'>\n{item.to_html()}\n</div>"

    render_html = (
        f"<!doctype html>\n<html>\n<head>{head_deps}</head>\n"
        f"<body>\n{content_html}\n{tail_deps}\n</body>\n</html>\n"
    )

    print()
    # This allows time to download plotly.js from the CDN - otherwise cell renders empty
    if "plotly" in required_deps:
        display(HTML(f"<head>\n{head_deps}\n</head>\n"), metadata=dict(isolated=True))
        time.sleep(2)

    display(HTML(render_html), metadata=dict(isolated=True))
    print()

    # Prevent output scrolling
    js = "$('.output_scroll').removeClass('output_scroll')"
    display(Javascript(js))

    if return_html:
        return render_html
    else:
        return None


def _prettify_html(html: str) -> str:
    """Prettify HTML."""
    if "bs4" in _INSTALLED_MODULES:
        from bs4 import BeautifulSoup  # type: ignore

        html = str(BeautifulSoup(html, features="html.parser").prettify())

    return html
