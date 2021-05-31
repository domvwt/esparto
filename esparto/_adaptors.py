from functools import singledispatch
from mimetypes import guess_type

from esparto import _INSTALLED_MODULES
from esparto._content import (
    Content,
    DataFramePd,
    FigureBokeh,
    FigureMpl,
    FigurePlotly,
    Image,
    Markdown,
)


@singledispatch
def content_adaptor(content: Content) -> Content:
    """
    Wrap content in the required class.

    Args:
      content (Any): Any content to be added to the document.

    Returns:
      Content: Approriately wrapped content.

    """
    if not issubclass(type(content), Content):
        raise TypeError(f"Unsupported content type: {type(content)}")
    return content


@content_adaptor.register(str)
def content_adaptor_core(content: str) -> Content:
    """Convert markdown or image to Markdown or Image content."""
    guess = guess_type(content)
    if guess and "image" in str(guess[0]):
        return Image(content)
    return Markdown(content)


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
