from collections import UserDict
from dataclasses import dataclass
from pathlib import Path
from typing import Set

from esparto import _INSTALLED_MODULES, _MODULE_PATH
from esparto._options import _get_source_from_options


@dataclass
class ContentDependency:
    name: str
    cdn: str
    inline: str
    target: str


class ResolvedDeps:
    def __init__(self):
        self.head = list()
        self.tail = list()


class ContentDependencyDict(UserDict):
    def __init__(self):
        super().__init__()

    def __add__(self, other: ContentDependency):
        self.data[other.name] = other
        return self


JS_DEPS = {"bokeh", "plotly"}

BOOTSTRAP_CDN = (
    '<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css" '
    + 'integrity="sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh" crossorigin="anonymous">'
)
BOOTSTRAP_INLINE = Path(_MODULE_PATH, "resources/css/bootstrap.min.css").read_text()
BOOTSTRAP_INLINE = f"<style>\n{BOOTSTRAP_INLINE}\n</style>"

CONTENT_DEPENDENCY_DICT = ContentDependencyDict()
CONTENT_DEPENDENCY_DICT += ContentDependency(
    "bootstrap", BOOTSTRAP_CDN, BOOTSTRAP_INLINE, "head"
)


if "bokeh" in _INSTALLED_MODULES:
    import bokeh.resources as bk_resources  # type: ignore

    BOKEH_CDN = bk_resources.CDN.render_js()
    BOKEH_INLINE = bk_resources.INLINE.render_js()

    CONTENT_DEPENDENCY_DICT += ContentDependency(
        "bokeh", BOKEH_CDN, BOKEH_INLINE, "tail"
    )

if "plotly" in _INSTALLED_MODULES:
    from plotly import offline as plotly_offline  # type: ignore

    plotly_version = "latest"
    PLOTLY_CDN = (
        f"<script src='https://cdn.plot.ly/plotly-{plotly_version}.min.js'></script>"
    )
    PLOTLY_INLINE = plotly_offline.get_plotlyjs()
    PLOTLY_INLINE = f"<script>\n{PLOTLY_INLINE}\n</script>"

    CONTENT_DEPENDENCY_DICT += ContentDependency(
        "plotly", PLOTLY_CDN, PLOTLY_INLINE, "head"
    )


def resolve_deps(
    required_deps: Set[str], source: str = "esparto.options"
) -> ResolvedDeps:
    resolved_deps = ResolvedDeps()

    source = _get_source_from_options(source)

    for dep in required_deps:
        dep_details: ContentDependency = CONTENT_DEPENDENCY_DICT[dep]
        getattr(resolved_deps, dep_details.target).append(getattr(dep_details, source))

    return resolved_deps
