import time
from typing import TYPE_CHECKING, List, Optional, Set, Union

from jinja2 import Environment, PackageLoader, select_autoescape  # type: ignore

if TYPE_CHECKING:  # pragma: no cover
    from esparto._layout import Layout
    from esparto._content import Content

from esparto import _INSTALLED_MODULES

_ENV = Environment(
    loader=PackageLoader("esparto", "resources/jinja"),
    autoescape=select_autoescape(["xml"]),
)

_BASE_TEMPLATE = _ENV.get_template("base.html")
_BOOTSTRAP_CDN = (
    '<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css" '
    + 'integrity="sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh" crossorigin="anonymous">'
)
_JS_DEPS = {"bokeh", "plotly"}

if "bokeh" in _INSTALLED_MODULES:
    import bokeh  # type: ignore

    bokeh_version = bokeh.__version__
    _BOKEH_CDN = f"""\
        <script src='https://cdn.bokeh.org/bokeh/release/bokeh-{bokeh_version}.min.js'
                crossorigin='anonymous'></script>
        <script src='https://cdn.bokeh.org/bokeh/release/bokeh-widgets-{bokeh_version}.min.js'
                crossorigin='anonymous'></script>
        <script src='https://cdn.bokeh.org/bokeh/release/bokeh-tables-{bokeh_version}.min.js'
                crossorigin='anonymous'></script>
        """

if "plotly" in _INSTALLED_MODULES:
    plotly_version = "latest"
    _PLOTLY_CDN = f"""\
        <script src='https://cdn.plot.ly/plotly-{plotly_version}.min.js'></script>
        """


def _get_head_deps(required_deps: Set[str]) -> List[str]:
    include_deps: List[str] = []

    if "bootstrap" in required_deps:
        include_deps.append(_BOOTSTRAP_CDN)

    if "plotly" in required_deps:
        include_deps.append(_PLOTLY_CDN)

    return include_deps


def _get_tail_deps(required_deps: Set[str]) -> List[str]:
    include_deps: List[str] = []

    if "bokeh" in required_deps:
        include_deps.append(_BOKEH_CDN)

    return include_deps


def publish_html(
    document: "Layout",
    filepath: Optional[str] = "./esparto-doc.html",
    return_html: bool = False,
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
    head_deps = _get_head_deps(required_deps)
    tail_deps = _get_tail_deps(required_deps)

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
        raise ImportError("Install weasyprint for PDF support.")
    else:
        import weasyprint as weasy  # type: ignore

        doc_js_deps = _JS_DEPS & document._required_dependencies()
        if doc_js_deps:
            raise NotImplementedError(
                f"PDF format unsupported for interactive content - document requires: {doc_js_deps}"
            )

        html = publish_html(document=document, filepath=None, return_html=True)
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
    if "IPython" in _INSTALLED_MODULES:
        from IPython.display import HTML, Javascript, display  # type: ignore

        from esparto._layout import Layout

        required_deps: set = set()

        if isinstance(item, Layout):
            required_deps = item._required_dependencies()
        elif hasattr(item, "_dependencies"):
            required_deps = item._dependencies

        head_deps = "\n".join(_get_head_deps(required_deps))
        tail_deps = "\n".join(_get_tail_deps(required_deps))
        content_html = f"<div class='container' style='width: 100%; height: 100%;'>\n{item.to_html()}\n</div>"

        render_html = (
            f"<!doctype html>\n<html>\n<head>{head_deps}</head>\n"
            f"<body>\n{content_html}\n{tail_deps}\n</body>\n</html>\n"
        )

        print()
        # This allows time to download plotly.js from the CDN - otherwise cell renders empty
        if "plotly" in required_deps:
            display(
                HTML(f"<head>\n{head_deps}\n</head>\n"), metadata=dict(isolated=True)
            )
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
    else:
        raise ModuleNotFoundError("IPython")


def _prettify_html(html: str) -> str:
    """Prettify HTML."""
    if "bs4" in _INSTALLED_MODULES:
        from bs4 import BeautifulSoup  # type: ignore

        html = str(BeautifulSoup(html, features="html.parser").prettify())

    return html
