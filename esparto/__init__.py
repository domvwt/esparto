# -*- coding: utf-8 -*-
"""Top-level package for esparto."""

from importlib.util import find_spec as _find_spec
from pathlib import Path as _Path
from typing import Set as _Set

__author__ = """Dominic Thorn"""
__email__ = "dominic.thorn@gmail.com"
__version__ = "0.2.3"

_MODULE_PATH: _Path = _Path(__file__).parent.absolute()


_OPTIONAL_DEPENDENCIES: set = {
    "bs4",
    "IPython",
    "matplotlib",
    "pandas",
    "bokeh",
    "plotly",
    "weasyprint",
}

_INSTALLED_MODULES: _Set[str] = {
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
from esparto._options import options
