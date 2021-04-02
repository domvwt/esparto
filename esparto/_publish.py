from pathlib import Path
from typing import TYPE_CHECKING, Optional, Union

from jinja2 import Environment, PackageLoader, select_autoescape  # type: ignore

if TYPE_CHECKING:  # pragma: no cover
    from esparto._layout import Layout
    from esparto._content import Content

from esparto import _installed_modules

_env = Environment(
    loader=PackageLoader("esparto", "templates"),
    autoescape=select_autoescape(["xml"]),
)

_base_template = _env.get_template("base.html")
_bootstrap_cdn = (
    '<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css" '
    + 'integrity="sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh" crossorigin="anonymous">'
)

_default_filename = "esparto-page-"
_ext = ".html"


def publish(
    document: "Layout", filepath: Optional[str] = None, return_html: bool = False
) -> Optional[str]:
    """

    Args:
      document (Layout):
      filepath (str):
      return_html (bool):

    Returns:
      str:

    """
    filepath = _determine_filepath(filepath)

    # Jinja requires dict for accessing properties
    doc_dict = document.to_dict()
    html_rendered: str = _base_template.render(content=doc_dict)
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
    """

    Args:
      item (Layout, Content):
      return_html (bool):

    Returns:
      str:

    """
    if "IPython" in _installed_modules:
        from IPython.core.display import HTML, display  # type: ignore

        html = f"<div class='container'>\n{item.to_html()}\n</div>\n"
        bootstrap_css = _bootstrap_cdn
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
    """

    Args:
      html (str):

    Returns:
      str:

    """
    if "bs4" in _installed_modules:
        from bs4 import BeautifulSoup  # type: ignore

        html = str(BeautifulSoup(html, features="html.parser").prettify())

        if "prettierfier" in _installed_modules:
            from prettierfier import prettify_html  # type: ignore

            html = prettify_html(html)

    return html


def _determine_filepath(filepath: Optional[str]) -> str:
    """

    Args:
      filepath (str):

    Returns:
      str:

    """
    if not filepath:
        i = 0
        while Path(f"{_default_filename}{i}{_ext}").is_file():
            i += 1
        filename = f"{_default_filename}{i}{_ext}"
        filepath = str(Path(".").parent.absolute() / filename)
    return filepath
