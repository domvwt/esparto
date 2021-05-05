"""Content classes for rendering common objects and markdown text to HTML."""

import base64
from abc import ABC, abstractmethod
from io import BytesIO, StringIO
from pathlib import Path
from typing import Any, Set, Tuple, Union
from uuid import uuid4

import markdown as md
import PIL.Image as Img  # type: ignore
from PIL.Image import Image as PILImage

from esparto import _INSTALLED_MODULES
from esparto._options import options
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
    def to_html(self, **kwargs) -> str:
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
        from esparto._layout import Row

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

    def to_html(self, **kwargs) -> str:
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

    def rescale(self, scale) -> "Image":
        """Rescale the image proportionately prior to rendering.

        Note:
          Images can be scaled down only.

        Args:
          scale (float): Scaling ratio.

        """
        self._scale = scale
        return self

    def to_html(self, **kwargs) -> str:
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

    def to_html(self, **kwargs) -> str:
        classes = "table table-sm table-striped table-hover table-bordered my-1"
        html = self.content.to_html(
            index=self.index, border=0, col_space=self.col_space, classes=classes
        )
        return html


class FigureMpl(Content):
    """Matplotlib figure.

    Args:
      figure (plt.Figure): A Matplotlib figure.
      caption (str): Image caption (default = None)
      alt_text (str): Alternative text. (default = None)
      output_format (str): One of 'svg', 'png', or 'esparto.options'. (default = 'esparto.options')

    """

    @property
    def content(self) -> "MplFigure":
        """ """
        raise NotImplementedError

    @content.getter
    def content(self) -> "MplFigure":
        """ """
        return self._content

    @content.setter
    def content(self, content) -> None:
        """ """
        self._content = content

    def __init__(
        self,
        figure: "MplFigure",
        caption: str = "",
        alt_text: str = "Image",
        output_format="esparto.options",
    ):

        if not isinstance(figure, MplFigure):
            raise TypeError(r"figure must be a Matplotlib Figure")

        self.content = figure
        self.caption = caption
        self.alt_text = alt_text
        self.output_format = output_format
        self._dependencies = {"bootstrap"}

    def __deepcopy__(self, *args, **kwargs):
        cls = self.__class__
        return cls(self.content)

    def to_html(self, **kwargs):

        if self.output_format == "esparto.options":
            output_format = options.matplotlib_output_format
        else:
            output_format = self.output_format

        if output_format == "svg":
            if kwargs.get("pdf_mode"):
                temp_file = Path(options.pdf_temp_dir) / f"{uuid4()}.svg"
                self.content.savefig(temp_file, format="svg")
                source = f"<img src='{temp_file.name}'>\n"

            else:
                buffer = StringIO()
                self.content.savefig(buffer, format="svg")
                buffer.seek(0)
                source = buffer.read()

            html = f"<figure class='text-center my-1'>\n{source}\n"

            if self.caption:
                html += (
                    f"<figcaption class='figure-caption'>{self.caption}</figcaption>\n"
                )

            html += "</figure>\n"

            return html

        # If not svg:
        buffer = BytesIO()
        self.content.savefig(buffer, format="png")
        buffer.seek(0)
        return Image(buffer, caption=self.caption, alt_text=self.alt_text).to_html()


class FigureBokeh(Content):
    """Bokeh object to be rendered as an interactive plot.

    Args:
      figure (bokeh.layouts.LayoutDOM): A Bokeh object.
      width (int): Width in pixels. (default = figure.width or 'auto')
      height (int): Height in pixels. (default = figure.height or 'auto')

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

    def to_html(self, **kwargs) -> str:

        if kwargs.get("pdf_mode"):
            from bokeh.io import export_svg  # type: ignore

            temp_file = Path(options.pdf_temp_dir) / f"{uuid4()}.svg"
            export_svg(self.content, filename=str(temp_file))
            html = f"<img src='{temp_file.name}'>\n"
            return html

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

    def to_html(self, **kwargs) -> str:

        if kwargs.get("pdf_mode"):
            temp_file = Path(options.pdf_temp_dir) / f"{uuid4()}.svg"
            self.content.write_image(str(temp_file))
            html = f"<img src='{temp_file.name}'>\n"

        else:
            html = plotly_to_html(self.content, include_plotlyjs=False, full_html=False)

            # Remove outer <div> tag so we can give our own attributes.
            html = _remove_outer_div(html)
            html = (
                "<div class='responsive-plot mb-3' "
                + f"style='width: {self.width}; height: {self.height};'>{html}\n</div>"
            )

        return html


def _remove_outer_div(html: str) -> str:
    """Remove outer <div> tags."""
    html = html.replace("<div>", "", 1)
    html = "".join(html.rsplit("</div>", 1))
    return html


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


def _rescale_image(
    image: PILImage, width: int = None, height: int = None, scale: float = None
) -> PILImage:
    """Rescale image by width in px, height in px, or ratio."""
    image = image.copy()
    new_size = _rescale_dims(image.size, width, height, scale)
    image.thumbnail(new_size)
    return image


def _rescale_dims(
    size: Tuple[int, int], width: int = None, height: int = None, scale: float = None
) -> Tuple[int, int]:
    """Rescale dimensions by width in px, height in px, or ratio."""
    if width:
        ratio = width / size[0]
    elif height:
        ratio = height / size[1]
    elif scale:
        ratio = scale
    else:
        raise ValueError("One of {'width', 'height', scale'} must be supplied")

    if ratio > 1:
        raise ValueError("Target size must be less than original size")

    new_size = (int(size[0] * ratio), int(size[1] * ratio))
    return new_size
