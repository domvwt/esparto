from typing import Optional, Union, TYPE_CHECKING
from pathlib import Path
from jinja2 import Environment, PackageLoader, select_autoescape

if TYPE_CHECKING:
    from esparto.layout import LayoutElement
    from esparto.content import Adaptor

from esparto import installed_optional_dependencies

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


def publish(content: "LayoutElement", filepath: Optional[str] = None):
    """

    Args:
      content: Page:

    Returns:

    """
    filepath = _determine_filepath(filepath)

    # Jinja requires dict for accessing properties
    content_ = content.to_dict()
    html = _base_template.render(content=content_)
    html = _prettify_html(html)

    with open(filepath, "w") as f:
        f.write(html)


def nb_display(content: Union["LayoutElement", "Adaptor"]):
    if "IPython" in installed_optional_dependencies:
        from IPython.core.display import display, HTML

        html = f"<div class='container my-4'>\n{content.to_html()}\n</div>\n"
        bootstrap_css = _bootstrap_cdn
        html = bootstrap_css + html

        print()
        display(HTML(html), metadata=dict(isolated=True))
        print()

        # Prevent output scrolling
        js = "<script>$('.output_scroll').removeClass('output_scroll')</script>"
        display(HTML(js))
    else:
        raise ModuleNotFoundError("IPython")


def _prettify_html(html):
    if "bs4" in installed_optional_dependencies:
        from bs4 import BeautifulSoup

        html = str(BeautifulSoup(html, features="html.parser").prettify())

        if "prettierfier" in installed_optional_dependencies:
            from prettierfier import prettify_html

            html = prettify_html(html)

    return html


def _determine_filepath(filepath):
    if not filepath:
        i = 0
        while Path(f"{_default_filename}{i}{_ext}").is_file():
            i += 1
        filename = f"{_default_filename}{i}{_ext}"
        filepath = str(Path(".").parent.absolute() / filename)
    return filepath
