# -*- coding: utf-8 -*-
from importlib.util import find_spec as _find_spec
from esparto.layout import Page, Section, Row, Column

from esparto.content import Markdown, Image, DataFramePd, FigureMpl, Spacer

"""Top-level package for esparto."""

__author__ = """Dominic Thorn"""
__email__ = "dominic.thorn@gmail.com"
__version__ = "0.1.0"


_optional_dependencies: list = ["bs4", "prettierfier", "IPython", "matplotlib"]
_installed_optional_dependencies: list = [
    x.name for x in [_find_spec(dep) for dep in _optional_dependencies] if x
]
