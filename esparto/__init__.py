# -*- coding: utf-8 -*-
"""
esparto
=======

Simple HTML page and PDF generator for Python.

Please visit https://domvwt.github.io/esparto/ for documentation and examples.

"""

from importlib.util import find_spec as _find_spec
from pathlib import Path as _Path
from typing import Set as _Set

__author__ = """Dominic Thorn"""
__email__ = "dominic.thorn@gmail.com"
__version__ = "2.0.0"

_MODULE_PATH: _Path = _Path(__file__).parent.absolute()


_OPTIONAL_DEPENDENCIES: _Set[str] = {
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

from esparto._cdnlinks import bootstrap_cdn_themes
from esparto._content import (
    DataFramePd,
    FigureBokeh,
    FigureMpl,
    FigurePlotly,
    Image,
    Markdown,
    RawHTML,
)
from esparto._layout import (
    Card,
    CardRow,
    CardRowEqual,
    CardSection,
    Column,
    Page,
    PageBreak,
    Row,
    Section,
    Spacer,
)
from esparto._options import options

options._autoload()
