from typing import TYPE_CHECKING, Optional, Union

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

    # Jinja requires dict for accessing properties
    doc_dict = document.to_dict()
    html_rendered: str = _BASE_TEMPLATE.render(content=doc_dict)
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
        from IPython.core.display import HTML, display  # type: ignore

        html = f"<div class='container'>\n{item.to_html()}\n</div>\n"
        bootstrap_css = _BOOTSTRAP_CDN
        html = bootstrap_css + html

        print()
        display(HTML(html), metadata=dict(isolated=True))
        print()

        # Prevent output scrolling
        js = "<script>$('.output_scroll').removeClass('output_scroll')</script>"
        display(HTML(js))

        if return_html:
            return html + js
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
