# -*- coding: utf-8 -*-
"""
esparto
=======

Simple HTML and PDF document generator for Python.

Please visit https://domvwt.github.io/esparto/ for documentation and examples.

Basic Usage
-----------

import esparto as es

# Instantiating a Page
page = es.Page(title="Research")

# Page layout hierarchy:
# Page -> Section -> Row -> Column -> Content

# Add or update content
# Keys are used as titles
page["Introduction"]["Part One"]["Item A"] = "./text/content.md"
page["Introduction"]["Part One"]["Item B"] = "./pictures/image1.jpg"

# Add content without a title
page["Introduction"]["Part One"][""] = "Hello, Wolrd!"

# Replace child at index - useful if no title given
page["Introduction"]["Part One"][-1] = "Hello, World!"

# Set content and return input object
# Useful in Jupyter Notebook as it will be displayed in cell output
page["Methodology"]["Part One"]["Item A"] << "dolor sit amet"
# >>> "dolor sit amet"

# Set content and return new layout
page["Methodology"]["Part Two"]["Item B"] >> "foobar"
# >>> {'Item B': ['Markdown']}

# Show document structure
page.tree()
# >>> {'Research': [{'Introduction': [{'Part One': [{'Item A': ['Markdown']},
#                                                   {'Item B': ['Image']}]}]},
#                   {'Methodology': [{'Part One': [{'Item A': ['Markdown']}]},
#                                    {'Part Two': [{'Item A': ['Markdown']}]}]}]}

# Remove content
del page["Methodology"]["Part One"]["Item A"]
del page.methodology.part_two.item_b

# Access existing content as an attribute
page.introduction.part_one.item_a = "./pictures/image2.jpg"
page.introduction.part_one.tree()
# >>> {'Part One': [{'Item A': ['Image']},
#                   {'Item B': ['Image']},
#                   {'Column 2': ['Markdown']}]}

# Save the document
page.save_html("my-page.html")
page.save_pdf("my-page.pdf")

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
    CardGrid,
    CardRow,
    Column,
    ColumnGrid,
    Page,
    PageBreak,
    Row,
    Section,
    Spacer,
)
from esparto._options import options

options._autoload()
