import functools as ft
import mimetypes as mt
from pathlib import Path
from typing import Any, Dict, Union

from esparto import _INSTALLED_MODULES
from esparto.design.content import (
    Content,
    DataFramePd,
    FigureBokeh,
    FigureMpl,
    FigurePlotly,
    Image,
    Markdown,
)
from esparto.design.layout import Layout


@ft.singledispatch
def content_adaptor(content: Content) -> Union[Content, Layout, Dict[str, Any]]:
    """
    Wrap content in the required class. If Layout object is passed, return unchanged.

    Args:
      content (Any): Any content to be added to the document.

    Returns:
      Content: Appropriately wrapped content.

    """
    if not issubclass(type(content), Content):
        raise TypeError(f"Unsupported content type: {type(content)}")
    return content


@content_adaptor.register(str)
@content_adaptor.register(Path)
def content_adaptor_core(content: Union[str, Path]) -> Content:
    """Convert text or image to Markdown or Image content."""
    content = str(content)
    guess = mt.guess_type(content)
    if guess and isinstance(guess[0], str):
        file_type = guess[0].split("/")[0]
        if file_type == "image":
            return Image(content)
        elif file_type == "text":
            content = Path(content).read_text()
        else:
            raise TypeError(f"{content}: {file_type}")
    return Markdown(content)


@content_adaptor.register(Layout)
def content_adaptor_layout(content: Layout) -> Layout:
    """If Layout object is passed, return unchanged."""
    return content


@content_adaptor.register(dict)
def content_adaptor_dict(content: Dict[str, Any]) -> Dict[str, Any]:
    """Pass through dict of `{"title": content}`."""
    if not (len(content) == 1 and isinstance(list(content.keys())[0], str)):
        raise ValueError("Content dict must be passed as {'title': content}")
    return content


# Function only available if Pandas is installed.
if "pandas" in _INSTALLED_MODULES:
    from pandas.core.frame import DataFrame  # type: ignore

    @content_adaptor.register(DataFrame)
    def content_adaptor_df(content: DataFrame) -> DataFramePd:
        """Convert Pandas DataFrame to DataFramePD content."""
        return DataFramePd(content)


# Function only available if Matplotlib is installed.
if "matplotlib" in _INSTALLED_MODULES:
    from matplotlib.figure import Figure  # type: ignore

    @content_adaptor.register(Figure)
    def content_adaptor_mpl(content: Figure) -> FigureMpl:
        """Convert Matplotlib Figure to FigureMpl content."""
        return FigureMpl(content)


# Function only available if Bokeh is installed.
if "bokeh" in _INSTALLED_MODULES:
    from bokeh.layouts import LayoutDOM as BokehObject  # type: ignore

    @content_adaptor.register(BokehObject)
    def content_adaptor_bokeh(content: BokehObject) -> FigureBokeh:
        """Convert Bokeh Layout to FigureBokeh content."""
        return FigureBokeh(content)


# Function only available if Plotly is installed.
if "plotly" in _INSTALLED_MODULES:
    from plotly.graph_objs._figure import Figure as PlotlyFigure  # type: ignore

    @content_adaptor.register(PlotlyFigure)
    def content_adaptor_plotly(content: PlotlyFigure) -> FigurePlotly:
        """Convert Plotly Figure to FigurePlotly content."""
        return FigurePlotly(content)
