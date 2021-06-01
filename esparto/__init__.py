# -*- coding: utf-8 -*-
"""
esparto
=======

Simple HTML and PDF document generator for Python.

esparto represents documents as a tree structure consisting of Layout
elements at the top and middle levels and Content elements in the leaves.
These objects are arranged in a fixed hierarchy, so esparto always knows
how to deal with new content if it hasn't been explicitly wrapped, or how
to fix the structure if it doesn't adhere to the nesting requirements.
It helps to understand this hierarchy when using the API so that we know what
to expect when adding content that required implicit wrapping and formatting.

A document is created by first defining a Page object - this is the primary
interface for the library and all tasks should be achievable through methods
attached to the page.
Manipulating a page is similar to working with a Python dictionary:
square brackets are used for getting and setting items, while titles act as
keys and layout objects and content act as values.


Basic Usage
-----------

import esparto as es

# Instantiating a Page
page = es.Page(title="Research")

# Page layout hierarchy:
# Page -> Section -> Row -> Column -> Content

# Add or update content
# Keys are used as titles
page["Introduction"]["Part One"]["Item A"] = "lorem ipsum"
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

Documentation
-------------

Please visit https://domvwt.github.io/esparto/ for documentation and examples.

"""

from importlib.util import find_spec as _find_spec
from pathlib import Path as _Path
from typing import Set as _Set

__author__ = """Dominic Thorn"""
__email__ = "dominic.thorn@gmail.com"
__version__ = "1.0.1"

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
