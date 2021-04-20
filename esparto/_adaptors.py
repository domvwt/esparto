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
        raise TypeError("Unsupported content type.")

    return content


@content_adaptor.register(str)
def content_adaptor_core(content: str) -> Content:
    """Called through dynamic dispatch."""
    guess = guess_type(content)
    if guess and "image" in str(guess[0]):
        return Image(content)

    return Markdown(content)


# Function only available if Pandas is installed.
if "pandas" in _INSTALLED_MODULES:
    from pandas.core.frame import DataFrame  # type: ignore

    @content_adaptor.register(DataFrame)
    def content_adaptor_df(content: DataFrame) -> DataFramePd:
        """Called through dynamic dispatch."""
        return DataFramePd(content)


# Function only available if Matplotlib is installed.
if "matplotlib" in _INSTALLED_MODULES:
    from matplotlib.figure import Figure  # type: ignore

    @content_adaptor.register(Figure)
    def content_adaptor_fig(content: Figure) -> FigureMpl:
        """Called through dynamic dispatch."""
        return FigureMpl(content)


# Function only available if Bokeh is installed.
if "bokeh" in _INSTALLED_MODULES:
    from bokeh.plotting import Figure as BokehFigure  # type: ignore

    @content_adaptor.register(BokehFigure)
    def content_adaptor_bokeh(content: BokehFigure) -> FigureBokeh:
        """Called through dynamic dispatch."""
        return FigureBokeh(content)


# Function only available if Plotly is installed.
if "plotly" in _INSTALLED_MODULES:
    from plotly.graph_objs._figure import Figure as PlotlyFigure  # type: ignore

    @content_adaptor.register(PlotlyFigure)
    def content_adaptor_plotly(content: PlotlyFigure) -> FigurePlotly:
        """Called through dynamic dispatch."""
        return FigurePlotly(content)
