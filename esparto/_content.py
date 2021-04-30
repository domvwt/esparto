"""Content classes for rendering common objects and markdown text to HTML."""

import base64
from abc import ABC, abstractmethod
from io import BytesIO
from typing import Any, Set, Union

import markdown as md
import PIL.Image as Img  # type: ignore
from PIL.Image import Image as PILImage

from esparto import _INSTALLED_MODULES
from esparto._publish import nb_display

if "pandas" in _INSTALLED_MODULES:
    from pandas import DataFrame  # type: ignore

if "matplotlib" in _INSTALLED_MODULES:
    from matplotlib.figure import Figure as MplFigure  # type: ignore

if "bokeh" in _INSTALLED_MODULES:
    from bokeh.embed import components  # type: ignore
    from bokeh.models.layouts import LayoutDOM as BokehObject  # type: ignore

if "plotly" in _INSTALLED_MODULES:
    from plotly.graph_objs._figure import Figure as PlotlyFigure  # type: ignore
    from plotly.io import to_html as plotly_to_html  # type: ignore


def _image_to_base64(image: PILImage) -> str:
    """
    Convert an image from PIL to base64 representation.

    Args:
      image (PIL.Image):

    Returns:
      str: Image encoded as a base64 utf-8 string.
    """
    buffer = BytesIO()
    image.save(buffer, format="png")
    image_encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return image_encoded


class Content(ABC):
    """Template for Content elements. All Content classes come with these methods and attributes.

    Attributes:
      content (Any): Text or image to be rendered - should match the encompassing Content class.
    """

    @property
    @abstractmethod
    def content(self) -> Any:
        """Text or image to be rendered - should match the encompassing Content class."""
        raise NotImplementedError

    @abstractmethod
    def to_html(self) -> str:
        """Render content to HTML code.

        Returns:
          HTML code.

        """
        raise NotImplementedError

    def display(self) -> None:
        """Display rendered content in a Jupyter Notebook cell."""
        nb_display(self)

    @property
    def _dependencies(self) -> Set[str]:
        raise NotImplementedError

    @_dependencies.getter
    def _dependencies(self) -> Set[str]:
        if hasattr(self, "_deps"):
            return self._deps
        return set()

    @_dependencies.setter
    def _dependencies(self, deps) -> None:
        self._deps = deps

    def __add__(self, other):
        from esparto._layout import Row  # Deferred for evade circular import

        return Row(self, other)

    def __iter__(self):
        return iter([self])

    def __len__(self):
        return len(list(self.content))

    def _repr_html_(self):
        """ """
        nb_display(self)

    def __str__(self):
        return str(self.__class__.__name__)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if hasattr(self.content, "__iter__") and hasattr(other.content, "__iter__"):
                return all(x == y for x, y in zip(self.content, other.content))
            else:
                return self.content == other.content

        return False

    def __ne__(self, other):
        return not self.__eq__(other)


class Markdown(Content):
    """Markdown text content.

    Args:
      text (str): Markdown text to be added to document.

    """

    @property
    def content(self) -> str:
        """ """
        raise NotImplementedError

    @content.getter
    def content(self) -> str:
        """ """
        return self._content

    @content.setter
    def content(self, content) -> None:
        """ """
        self._content = content

    def __init__(self, text):

        if not isinstance(text, str):
            raise TypeError(r"text must be str")

        self.content = str(text)
        self._dependencies = {"bootstrap"}

    def to_html(self) -> str:
        html = md.markdown(self.content)
        html = f"{html}\n"
        html = f"<div class='px-1'>\n{html}\n</div>"
        return html


class Image(Content):
    """Image content.

    Can be read from a filepath, PIL.Image object, or from bytes.

    Only one of `scale`, `set_width`, or `set_height` should be used.
    If more than one is populated, the values will be prioritised in the order:
         `set_width` -> `set_height` -> `scale`

    Args:
      image (str, PIL.Image, BytesIO): Image data.
      caption (str): Image caption (default = None)
      alt_text (str): Alternative text. (default = None)
      scale (float): Scale image proportionately, must be > 0 and <= 1. (default = None)
      set_width (int): Set width in pixels. (default = None)
      set_height (int): Set height in pixels. (default = None)

    """

    @property
    def content(self) -> Union[str, BytesIO]:
        """ """
        raise NotImplementedError

    @content.getter
    def content(self) -> Union[str, BytesIO]:
        """ """
        return self._content

    @content.setter
    def content(self, content) -> None:
        """ """
        self._content = content

    def __init__(
        self,
        image: Union[str, PILImage, BytesIO],
        alt_text: str = "Image",
        caption: str = "",
        scale: float = None,
        set_width: int = None,
        set_height: int = None,
    ):

        if not isinstance(image, (str, PILImage, BytesIO)):
            raise TypeError(r"image must be one of {str, PIL.Image, BytesIO}")

        self.content = image
        self.alt_text = alt_text
        self.caption = caption
        self._scale = scale
        self._width = set_width
        self._height = set_height
        self._dependencies = {"bootstrap"}

    def set_width(self, width) -> "Image":
        """Set width of image prior to rendering.

        Args:
          width (int): New width in pixels.

        """
        self._width = width
        return self

    def set_height(self, height) -> "Image":
        """Set height of image prior to rendering.

        Args:
          height (int): New height in pixels.

        """
        self._height = height
        return self

    def scale(self, scale) -> "Image":
        """Rescale the image proportionately prior to rendering.

        Note:
          Images can be scaled down only.

        Args:
          scale (float): Scaling ratio.

        """
        self._scale = scale
        return self

    def to_html(self) -> str:
        if isinstance(self.content, PILImage):
            image = self.content
        else:
            image = Img.open(self.content)

        if self._width or self._height or self._scale:
            image = _rescale_image(image, self._width, self._height, self._scale)

        image_encoded = _image_to_base64(image)
        html = (
            "<figure class='text-center my-1'>"
            + "<img class='figure-img rounded' "
            + f"alt='{self.alt_text}' "
            + f"src='data:image/png;base64,{image_encoded}' "
            + ">"
        )

        if self.caption:
            html += f"<figcaption class='figure-caption'>{self.caption}</figcaption>"

        html += "</figure>"

        return html


class DataFramePd(Content):
    """Pandas DataFrame to be rendered as a table.

    Args:
      df (pd.DataFrame): A Pandas DataFrame
      index (bool): If True, render the DataFrame index. (default = False)
      col_space (str, int): Minimum column width in CSS units. Use int for pixels. (default = 10)

    """

    @property
    def content(self) -> "DataFrame":
        """ """
        raise NotImplementedError

    @content.getter
    def content(self) -> "DataFrame":
        """ """
        return self._content

    @content.setter
    def content(self, content) -> None:
        """ """
        self._content = content

    def __init__(
        self, df: "DataFrame", index: bool = False, col_space: Union[int, str] = 10
    ):

        if not isinstance(df, DataFrame):
            raise TypeError(r"df must be Pandas DataFrame")

        self.content = df
        self.index = index
        self.col_space = col_space
        self._dependencies = {"bootstrap"}

    def to_html(self) -> str:
        classes = "table table-sm table-striped table-hover table-bordered my-1"
        html = self.content.to_html(
            index=self.index, border=0, col_space=self.col_space, classes=classes
        )
        return html


class FigureMpl(Image):
    """Matplotlib figure to be rendered as an image.

    Args:
      figure (plt.Figure): A Matplotlib figure.
      caption (str): Image caption (default = None)
      alt_text (str): Alternative text. (default = None)
      scale (float): Scale image proportionately, must be > 0 and <= 1. (default = None)
      set_width (int): Set width in pixels. (default = None)
      set_height (int): Set height in pixels. (default = None)

    """

    def __init__(
        self,
        figure: "MplFigure",
        caption: str = "",
        alt_text: str = "Image",
        scale: float = None,
        set_width: int = None,
        set_height: int = None,
    ):

        if not isinstance(figure, MplFigure):
            raise TypeError(r"figure must be a Matplotlib Figure")

        buffer = BytesIO()
        figure.savefig(buffer, format="png")
        super().__init__(
            buffer,
            caption=caption,
            alt_text=alt_text,
            scale=scale,
            set_width=set_width,
            set_height=set_height,
        )


class FigureBokeh(Content):
    """Bokeh object to be rendered as an interactive plot.

    Args:
      figure (bokeh.layouts.LayoutDOM): A Bokeh object.
      width (int): Width in pixels. (default = from figure or 'auto')
      height (int): Height in pixels. (default = from figure or 'auto')

    """

    @property
    def content(self) -> "BokehObject":
        """ """
        raise NotImplementedError

    @content.getter
    def content(self) -> "BokehObject":
        """ """
        return self._content

    @content.setter
    def content(self, content) -> None:
        """ """
        self._content = content

    @property
    def width(self) -> Union[int, str, None]:
        """ """
        raise NotImplementedError

    @width.getter
    def width(self) -> str:
        """ """
        if isinstance(self._width, str) and self._width == "auto":
            return self._width

        return f"{self._width}px"

    @width.setter
    def width(self, width) -> None:
        """ """
        self._width = width

    @property
    def height(self) -> Union[int, str, None]:
        """ """
        raise NotImplementedError

    @height.getter
    def height(self) -> str:
        """ """
        if isinstance(self._height, str) and self._height == "auto":
            return self._height

        return f"{self._height}px"

    @height.setter
    def height(self, height) -> None:
        """ """
        self._height = height

    def __init__(
        self,
        figure: "BokehObject",
        width: int = None,
        height: int = None,
    ):

        self._dependencies = {"bokeh"}
        self.content = figure

        if not issubclass(type(figure), BokehObject):
            raise TypeError(r"figure must be a Bokeh object")

        fig_width = figure.properties_with_values().get("width")
        fig_height = figure.properties_with_values().get("height")

        self.width = width or fig_width or "auto"
        self.height = height or fig_height or "auto"

    # Required as deep copy is not defined for Bokeh figures
    # Also need to catch some erroneous args that get passed to the function
    def __deepcopy__(self, *args, **kwargs):
        cls = self.__class__
        return cls(self.content)

    def to_html(self) -> str:
        html, js = components(self.content)

        # Remove outer <div> tag so we can give our own attributes
        html = _remove_outer_div(html)

        return f"<div class='mb-3' style='width: {self.width}; height: {self.height};'>{html}\n{js}\n</div>"


class FigurePlotly(Content):
    """Plotly figure to be rendered as an interactive plot.

    Args:
      figure (plotly.graph_objs._figure.Figure): A Plotly figure.
      width (int): Width in pixels. (default = 'auto')
      height (int): Height in pixels. (default = 500)

    """

    @property
    def content(self) -> "PlotlyFigure":
        """ """
        raise NotImplementedError

    @content.getter
    def content(self) -> "PlotlyFigure":
        """ """
        return self._content

    @content.setter
    def content(self, content) -> None:
        """ """
        self._content = content

    @property
    def width(self) -> Union[int, str, None]:
        """ """
        raise NotImplementedError

    @width.getter
    def width(self) -> str:
        """ """
        if self._width == "auto":
            return self._width

        return f"{self._width}px"

    @width.setter
    def width(self, width) -> None:
        """ """
        self._width = width

    @property
    def height(self) -> Union[int, str, None]:
        """ """
        raise NotImplementedError

    @height.getter
    def height(self) -> str:
        """ """
        if self._height == "auto":
            return self._height

        return f"{self._height}px"

    @height.setter
    def height(self, height) -> None:
        """ """
        self._height = height

    def __init__(self, figure: "PlotlyFigure", width: int = None, height: int = None):

        if not isinstance(figure, PlotlyFigure):
            raise TypeError(r"figure must be a Plotly Figure")

        self.width = width or figure.layout["width"] or "auto"
        self.height = height or figure.layout["height"] or 500

        self.content = figure
        self._dependencies = {"plotly"}

    def to_html(self) -> str:
        html = plotly_to_html(self.content, include_plotlyjs=False, full_html=False)

        # Remove outer <div> tag so we can give our own attributes.
        html = _remove_outer_div(html)

        return f"<div class='responsive-plot mb-3' style='width: {self.width}; height: {self.height};'>{html}\n</div>"


def _remove_outer_div(html: str) -> str:
    """Remove outer <div> tags."""
    html = html.replace("<div>", "", 1)
    html = "".join(html.rsplit("</div>", 1))
    return html


def _rescale_image(
    image: PILImage, width: int = None, height: int = None, scale: float = None
) -> PILImage:
    """Rescale image by width in px, height in px, or ratio."""

    if width:
        ratio = width / image.size[0]
    elif height:
        ratio = height / image.size[1]
    elif scale:
        ratio = scale
    else:
        raise ValueError("One of {'width', 'height', scale'} must be supplied")

    if ratio > 1:
        raise ValueError("Target size must be less than original size")

    image = image.copy()
    new_size = (int(image.size[0] * ratio), int(image.size[1] * ratio))
    image.thumbnail(new_size)
    return image
