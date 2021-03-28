# -*- coding: utf-8 -*-

"""Top-level package for esparto."""

__author__ = """Dominic Thorn"""
__email__ = "dominic.thorn@gmail.com"
__version__ = "0.1.0"


from importlib.util import find_spec

optional_dependencies = ["bs4", "prettierfier", "IPython", "matplotlib"]
installed_optional_dependencies = [
    x.name for x in [find_spec(dep) for dep in optional_dependencies] if x
]

from esparto.layout import Page, Section, Row, Column

from esparto.content import Markdown, Image, DataFramePd, FigureMpl, Spacer
