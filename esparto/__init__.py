# -*- coding: utf-8 -*-
"""
esparto
=======

Data driven report builder for the PyData ecosystem.

Please visit https://domvwt.github.io/esparto/ for documentation and examples.

"""

from importlib.util import find_spec as _find_spec
from pathlib import Path as _Path
from typing import Set as _Set

__author__ = """Dominic Thorn"""
__email__ = "dominic.thorn@gmail.com"
__version__ = "4.1.0"

_MODULE_PATH: _Path = _Path(__file__).parent.absolute()


_OPTIONAL_DEPENDENCIES: _Set[str] = {
    "PIL",  # Only used for type checking and conversion
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

from esparto._options import OutputOptions, options
from esparto.design.content import (
    DataFramePd,
    FigureBokeh,
    FigureMpl,
    FigurePlotly,
    Image,
    Markdown,
    RawHTML,
)
from esparto.design.layout import (
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
