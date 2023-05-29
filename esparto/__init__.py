# -*- coding: utf-8 -*-
"""
esparto
=======

Data driven report builder for the PyData ecosystem.

Please visit https://domvwt.github.io/esparto/ for documentation and examples.

"""

import dataclasses as _dc
from importlib.util import find_spec as _find_spec
from pathlib import Path as _Path

__author__ = """Dominic Thorn"""
__email__ = "dominic.thorn@gmail.com"
__version__ = "4.3.0"

_MODULE_PATH: _Path = _Path(__file__).parent.absolute()


@_dc.dataclass(frozen=True)
class _OptionalDependencies:
    PIL: bool = _find_spec("PIL") is not None
    IPython: bool = _find_spec("IPython") is not None
    matplotlib: bool = _find_spec("matplotlib") is not None
    pandas: bool = _find_spec("pandas") is not None
    bokeh: bool = _find_spec("bokeh") is not None
    plotly: bool = _find_spec("plotly") is not None
    weasyprint: bool = _find_spec("weasyprint") is not None

    def all_extras(self) -> bool:
        return all(_dc.astuple(self))


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
