"""Content dependency management."""

from collections import UserDict
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Set

from esparto import _INSTALLED_MODULES, _MODULE_PATH
from esparto._options import get_source_from_options


@dataclass
class ContentDependency:
    name: str
    cdn: str
    inline: str
    target: str


@dataclass
class ResolvedDeps:
    head: List[str] = field(default_factory=list)
    tail: List[str] = field(default_factory=list)


class ContentDependencyDict(UserDict):
    def __add__(self, item: ContentDependency):
        super().__setitem__(item.name, item)
        return self


JS_DEPS = {"bokeh", "plotly"}


def lazy_content_dependency_dict() -> ContentDependencyDict:
    bootstrap_cdn = (
        '<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css" '
        + 'integrity="sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh" crossorigin="anonymous">'
    )
    bootstrap_inline = Path(_MODULE_PATH, "resources/css/bootstrap.min.css").read_text()
    bootstrap_inline = f"<style>\n{bootstrap_inline}\n</style>"

    content_dependency_dict = ContentDependencyDict()
    content_dependency_dict += ContentDependency(
        "bootstrap", bootstrap_cdn, bootstrap_inline, "head"
    )

    if "bokeh" in _INSTALLED_MODULES:
        import bokeh.resources as bk_resources  # type: ignore

        bokeh_cdn = bk_resources.CDN.render_js()
        bokeh_inline = bk_resources.INLINE.render_js()

        content_dependency_dict += ContentDependency(
            "bokeh", bokeh_cdn, bokeh_inline, "tail"
        )

    if "plotly" in _INSTALLED_MODULES:
        from plotly import offline as plotly_offline  # type: ignore

        plotly_version = "latest"
        plotly_cdn = f"<script src='https://cdn.plot.ly/plotly-{plotly_version}.min.js'></script>"
        plotly_inline = plotly_offline.get_plotlyjs()
        plotly_inline = f"<script>\n{plotly_inline}\n</script>"

        content_dependency_dict += ContentDependency(
            "plotly", plotly_cdn, plotly_inline, "head"
        )

    return content_dependency_dict


def resolve_deps(
    required_deps: Set[str], source: str = "esparto.options"
) -> ResolvedDeps:
    resolved_deps = ResolvedDeps()

    source = get_source_from_options(source)

    for dep in required_deps:
        dep_details: ContentDependency = lazy_content_dependency_dict()[dep]
        getattr(resolved_deps, dep_details.target).append(getattr(dep_details, source))

    return resolved_deps
