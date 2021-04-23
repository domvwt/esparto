import time
from typing import TYPE_CHECKING, List, Optional, Set, Union

from jinja2 import Environment, PackageLoader, select_autoescape  # type: ignore

if TYPE_CHECKING:  # pragma: no cover
    from esparto._layout import Layout
    from esparto._content import Content

from esparto import _INSTALLED_MODULES

_ENV = Environment(
    loader=PackageLoader("esparto", "templates"),
    autoescape=select_autoescape(["xml"]),
)

_BASE_TEMPLATE = _ENV.get_template("base.html")
_BOOTSTRAP_CDN = (
    '<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css" '
    + 'integrity="sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh" crossorigin="anonymous">'
)

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


def publish(
    document: "Layout",
    filepath: Optional[str] = "./esparto-doc.html",
    return_html: bool = False,
) -> Optional[str]:
    """Save Layout element to HTML.

    Args:
      document (Layout): Any Layout object.
      filepath (str): Filepath to write to. (default = './esparto-doc.html')
      return_html (bool): Returns HTML string if True.

    Returns:
      str: HTML string if return_html is True.

    """

    if not filepath:
        filepath = "./esparto-doc.html"

    required_deps = document._required_dependencies()
    head_deps = _get_head_deps(required_deps)
    tail_deps = _get_tail_deps(required_deps)

    # Jinja requires dict for accessing properties
    doc_dict = document.to_dict()
    html_rendered: str = _BASE_TEMPLATE.render(
        content=doc_dict, head_deps=head_deps, tail_deps=tail_deps
    )
    html_prettified = _prettify_html(html_rendered)

    with open(filepath, "w") as f:
        f.write(html_prettified)

    if return_html:
        return html_prettified
    else:
        return None


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
        content_html = f"<div class='container-fluid' style='width: 100%; height: 100%;'>\n{item.to_html()}\n</div>"

        render_html = (
            f"<!doctype html>\n<html>\n<head>{head_deps}</head>\n"
            f"<body>\n{content_html}\n{tail_deps}\n</body>\n</html>\n"
        )

        print()
        display(HTML(render_html), metadata=dict(isolated=True))
        # This allows time to download plotly.js from the CDN - otherwise cell renders empty
        # TODO: Make this asynchronous
        if "plotly" in required_deps:
            time.sleep(1)
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
