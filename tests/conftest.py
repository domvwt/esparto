import sys
from io import BytesIO
from pathlib import Path

import pytest

import esparto._content as co
import esparto._layout as la
from esparto import _INSTALLED_MODULES, _OPTIONAL_DEPENDENCIES

_EXTRAS = _OPTIONAL_DEPENDENCIES <= _INSTALLED_MODULES

_irises_path = str(Path("tests/resources/irises.jpg").absolute())

with Path(_irises_path).open("rb") as f:
    _irises_binary = BytesIO(f.read())


# Add new content classes here
content_list = [
    (co.Markdown("this _is_ some **markdown**")),
    (co.Image(_irises_path)),
    (co.RawHTML("<p>Raw HTML</p>")),
]

# Add new layout classes here
layout_list = [
    (la.Page(children=[*content_list])),
    (la.Section(children=[*content_list])),
    (la.Row(children=[*content_list])),
    (la.Column(children=[*content_list])),
    (la.Spacer()),
    (la.PageBreak()),
]

# Add new adaptor types here
adaptor_list = [
    ("this is markdown", co.Markdown),
    (_irises_path, co.Image),
]

if _EXTRAS:
    import bokeh.layouts as bkl  # type: ignore
    import bokeh.plotting as bkp  # type: ignore
    import matplotlib.pyplot as plt  # type: ignore
    import pandas as pd  # type: ignore
    import plotly.express as px  # type: ignore

    if sys.version.startswith("3.6."):
        import matplotlib as mpl  # type: ignore

        mpl.use("Agg")

    # svg output format cannot be parsed in testing
    content_extra = [
        (co.DataFramePd(pd.DataFrame({"a": range(1, 11), "b": range(11, 21)}))),
        (co.FigureMpl(plt.Figure(), output_format="png")),
        (co.FigureBokeh(bkp.figure())),
        (co.FigureBokeh(bkl.column(bkp.figure()))),
        (co.FigurePlotly(px.line(x=range(10), y=range(10)))),  # type: ignore
    ]

    content_list += content_extra

    content_pdf = content_list + [
        (co.FigureMpl(plt.Figure())),
        (co.FigureMpl(plt.Figure(), output_format="svg")),
    ]

    adaptors_extra = [
        (pd.DataFrame({"a": range(1, 11), "b": range(11, 21)}), co.DataFramePd),
        (plt.figure(), co.FigureMpl),
        (bkp.Figure(), co.FigureBokeh),
        (bkl.column(bkp.figure()), co.FigureBokeh),
        (px.line(x=range(10), y=range(10)), co.FigurePlotly),
    ]

    adaptor_list += adaptors_extra


@pytest.fixture
def content_list_fn():
    return content_list


@pytest.fixture
def layout_list_fn():
    return layout_list


@pytest.fixture
def adaptor_list_fn():
    return adaptor_list


@pytest.fixture
def page_layout(content_list_fn) -> la.Page:
    return la.Page(
        title="jazz",
        children=la.Section(
            children=la.Row(children=[la.Column(children=[x]) for x in content_list_fn])
        ),
    )


@pytest.fixture
def page_basic_layout() -> la.Page:
    page = la.Page(
        title="Test Page",
        children=la.Section(
            title="Section One",
            children=la.Row(
                title="Row One",
                children=la.Column(children=co.Markdown("markdown content")),
            ),
        ),
    )
    return page


@pytest.fixture
def section_layout(image_content) -> la.Section:
    return la.Section(image_content)


@pytest.fixture
def markdown_content() -> co.Markdown:
    return co.Markdown("A")


@pytest.fixture
def image_content() -> co.Image:
    return co.Image(_irises_path)
