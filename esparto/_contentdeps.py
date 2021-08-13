"""Content dependency management."""

from collections import UserDict
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Set

from esparto import _INSTALLED_MODULES
from esparto._options import options


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
    bootstrap_inline = Path(options.bootstrap_css).read_text()
    bootstrap_inline = f"<style>\n{bootstrap_inline}\n</style>"

    content_dependency_dict = ContentDependencyDict()
    content_dependency_dict += ContentDependency(
        "bootstrap", options.bootstrap_cdn, bootstrap_inline, "head"
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


def resolve_deps(required_deps: Set[str], source: Optional[str]) -> ResolvedDeps:
    resolved_deps = ResolvedDeps()

    if source not in {"cdn", "inline"}:
        raise ValueError("Dependency source must be 'cdn' or 'inline'")

    source = options.dependency_source

    for dep in required_deps:
        dep_details: ContentDependency = lazy_content_dependency_dict()[dep]
        getattr(resolved_deps, dep_details.target).append(getattr(dep_details, source))

    return resolved_deps
