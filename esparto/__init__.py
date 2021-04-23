# -*- coding: utf-8 -*-
"""Top-level package for esparto."""

from importlib.util import find_spec as _find_spec
from typing import Set

__author__ = """Dominic Thorn"""
__email__ = "dominic.thorn@gmail.com"
__version__ = "0.2.0"


_OPTIONAL_DEPENDENCIES: set = {
    "bs4",
    "IPython",
    "matplotlib",
    "pandas",
    "bokeh",
    "plotly",
}

_INSTALLED_MODULES: Set[str] = {
    x.name for x in [_find_spec(dep) for dep in _OPTIONAL_DEPENDENCIES] if x
}

from esparto._content import (
    DataFramePd,
    FigureBokeh,
    FigureMpl,
    FigurePlotly,
    Image,
    Markdown,
)
from esparto._layout import Column, Page, Row, Section
