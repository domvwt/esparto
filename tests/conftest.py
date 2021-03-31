from pathlib import Path
from io import BytesIO

import matplotlib.pyplot as plt  # type: ignore
import pandas as pd  # type: ignore
import pytest
from html5lib import HTMLParser  # type: ignore


import esparto._content as co
import esparto._layout as la

pytestmark = pytest.mark.filterwarnings("ignore:Row titles are not rendered")

_irises_path = str(Path("tests/resources/irises.jpg").absolute())

with Path(_irises_path).open("rb") as f:
    _irises_binary = f.read()

# Add new content classes here
content_list = [
    (co.Markdown("A")),
    (co.Image(_irises_path)),
    (co.Spacer()),
    (co.DataFramePd(pd.DataFrame({"a": range(1, 11), "b": range(11, 21)}))),
    (co.FigureMpl(plt.figure())),
]

# Add new layout classes here
layout_list = [
    (la.Page(*content_list)),
    (la.Section(*content_list)),
    (la.Row(*content_list)),
    (la.Column(*content_list)),
]

# Add new adaptor types here
adaptor_list = [
    ("this is markdown", co.Markdown),
    (_irises_path, co.Image),
    (pd.DataFrame({"a": range(1, 11), "b": range(11, 21)}), co.DataFramePd),
    (plt.figure(), co.FigureMpl),
]


@pytest.fixture
def content_list_fn():
    return content_list


@pytest.fixture
def layout_list_fn():
    return layout_list


@pytest.fixture
def page_layout(content_list_fn) -> la.Page:
    return la.Page(la.Section(la.Row(*[la.Column(x) for x in content_list_fn])), title="jazz")


@pytest.fixture
def section_layout(image_content) -> la.Section:
    return la.Section(image_content)


@pytest.fixture
def markdown_content() -> co.Markdown:
    return co.Markdown("A")


@pytest.fixture
def image_content() -> co.Image:
    return co.Image(_irises_path)


@pytest.fixture
def htmlparser():
    return HTMLParser(strict=True)
