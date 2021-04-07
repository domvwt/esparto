from functools import singledispatch
from mimetypes import guess_type

from esparto import _installed_modules
from esparto._content import Content, DataFramePd, FigureMpl, Image, Markdown


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
    else:
        return Markdown(content)


# Function only available if Pandas is installed.
if "pandas" in _installed_modules:
    from pandas.core.frame import DataFrame  # type: ignore

    @content_adaptor.register(DataFrame)
    def content_adaptor_df(content: DataFrame) -> DataFramePd:
        """Called through dynamic dispatch."""
        return DataFramePd(content)


# Function only available if Matplotlib is installed.
if "matplotlib" in _installed_modules:
    from matplotlib.figure import Figure  # type: ignore

    @content_adaptor.register(Figure)
    def content_adaptor_fig(content: Figure) -> FigureMpl:
        """Called through dynamic dispatch."""
        return FigureMpl(content)
