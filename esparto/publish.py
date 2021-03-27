import importlib
from typing import Optional, TYPE_CHECKING
from pathlib import Path
from jinja2 import Environment, PackageLoader, select_autoescape

if TYPE_CHECKING:
    from esparto.layout import LayoutElement

_optional_deps = ["bs4", "prettierfier", "IPython"]
_found_opt_deps = [
    x.name for x in [importlib.util.find_spec(dep) for dep in _optional_deps] if x  # type: ignore
]

_env = Environment(
    loader=PackageLoader("esparto", "templates"),
    autoescape=select_autoescape(["xml"]),
)

_base_template = _env.get_template("base.html")
_bootstrap_cdn = '<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css" integrity="sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh" crossorigin="anonymous">'

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


def nb_display(content: "LayoutElement"):
    if "IPython" in _found_opt_deps:
        from IPython.core.display import display, HTML

        bootstrap_css = _bootstrap_cdn
        html = content.to_html()
        html = bootstrap_css + html
        display(HTML(html), metadata=dict(isolated=True))
    else:
        raise ModuleNotFoundError


def _prettify_html(html):
    if "bs4" in _found_opt_deps:
        from bs4 import BeautifulSoup

        html = str(BeautifulSoup(html, features="html.parser").prettify())
    if "prettierfier" in _found_opt_deps:
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
