"""Content classes for rendering objects and markdown to HTML."""

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
from esparto._utils import responsive_svg_mpl

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
    """Template for Content elements.

    Attributes:
        content (Any): Item to be included in the page - should match the encompassing Content class.

    """

    content: Any
    _dependencies: Set[str]

    @abstractmethod
    def to_html(self, **kwargs) -> str:
        """Convert content to HTML code.

        Returns:
            str: HTML code.

        """
        raise NotImplementedError

    def display(self) -> None:
        """Display rendered content in a Jupyter Notebook cell."""
        nb_display(self)

    def __add__(self, other):
        from esparto._layout import Row

        return Row(children=[self, other])

    def __iter__(self):
        return iter([self])

    def __len__(self):
        return len(list(self.content))

    def _repr_html_(self):
        nb_display(self)

    def __str__(self):
        return getattr(self, "title", None) or self.__class__.__name__

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if hasattr(self.content, "__iter__") and hasattr(other.content, "__iter__"):
                return all(x == y for x, y in zip(self.content, other.content))
            return self.content == other.content
        return False

    def __ne__(self, other):
        return not self.__eq__(other)


class RawHTML(Content):
    """Raw HTML content.

    Args:
        html (str): HTML code.

    """

    _dependencies: Set[Any] = set("")

    def __init__(self, html):

        if not isinstance(html, str):
            raise TypeError(r"HTML must be str")

        self.content = html

    def to_html(self, **kwargs) -> str:
        return self.content


class Markdown(Content):
    """Markdown text content.

    Args:
        text (str): Markdown text to be added to document.

    """

    _dependencies = {"bootstrap"}

    def __init__(self, text):

        if not isinstance(text, str):
            raise TypeError(r"text must be str")

        self.content: str = text

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

    _dependencies = {"bootstrap"}

    def __init__(
        self,
        image: Union[str, Path, PILImage, BytesIO],
        caption: str = "",
        alt_text: str = "Image",
        scale: float = None,
        set_width: int = None,
        set_height: int = None,
    ):

        if not isinstance(image, (str, Path, PILImage, BytesIO)):
            raise TypeError(r"image must be one of {str, Path, PIL.Image, BytesIO}")

        self.content = image
        self.alt_text = alt_text
        self.caption = caption
        self._scale = scale
        self._width = set_width
        self._height = set_height

    def set_width(self, width) -> None:
        """Set width of image.

        Args:
            width (int): New width in pixels.

        """
        self._width = width

    def set_height(self, height) -> None:
        """Set height of image.

        Args:
            height (int): New height in pixels.

        """
        self._height = height

    def rescale(self, scale) -> None:
        """Resize the image by a scaling factor prior to rendering.

        Note:
            Images can be scaled down only.

        Args:
            scale (float): Scaling ratio.

        """
        self._scale = scale

    def to_html(self, **kwargs) -> str:
        if isinstance(self.content, PILImage):
            image = self.content
        else:
            image = Img.open(self.content)

        if self._width or self._height or self._scale:
            image = _rescale_image(image, self._width, self._height, self._scale)

        image_encoded = _image_to_base64(image)

        width, height = image.size
        max_scale_up = 1.2
        max_scale_down = 0.5

        html = (
            "<figure class='text-center m-0 p-2 pb-3'>"
            "<img class='img-fluid figure-img rounded' "
            f"style='min-width: {int(width * max_scale_down)}px; "
            f"max-width: min({int(width * max_scale_up)}px, 100%);' "
            f"alt='{self.alt_text}' "
            f"src='data:image/png;base64,{image_encoded}'>"
        )

        if self.caption:
            html += f"<figcaption class='figure-caption'>{self.caption}</figcaption>"

        html += "</figure>"

        return html


class DataFramePd(Content):
    """Pandas DataFrame to be converted to table.

    Args:
        df (pd.DataFrame): A Pandas DataFrame
        index (bool): If True, render the DataFrame index. (default = True)
        col_space (str, int): Minimum column width in CSS units. Use int for pixels. (default = 0)

    Attributes:
        css_classes (List[str]): CSS classes applied to the HTML output.

    """

    _dependencies = {"bootstrap"}

    def __init__(
        self, df: "DataFrame", index: bool = True, col_space: Union[int, str] = 0
    ):

        if not isinstance(df, DataFrame):
            raise TypeError(r"df must be Pandas DataFrame")

        self.content: "DataFrame" = df
        self.index = index
        self.col_space = col_space
        self.css_classes = [
            "table",
            "table-xs",
            "table-striped",
            "table-hover",
            "table-bordered",
            "my-1",
        ]

    def to_html(self, **kwargs) -> str:
        html = self.content.to_html(
            index=self.index,
            border=0,
            col_space=self.col_space,
            classes=self.css_classes,
        )
        html = f"<div class='table-responsive'>{html}</div>"
        return html


class FigureMpl(Content):
    """Matplotlib figure.

    Args:
        figure (plt.Figure): A Matplotlib figure.
        width (int, str): Image width. (default = '100%')
        height (int, str): Image height. (default = 'auto')
        output_format (str): 'svg' or 'png'. (default = None)
        pdf_figsize (tuple, float): Set figure size for PDF output. (default = None)
            Accepts a tuple of (height, width) or a float to use as scale factor.

    """

    _dependencies = {"bootstrap"}

    def __init__(
        self,
        figure: "MplFigure",
        width: Union[str, int] = "100%",
        height: Union[str, int] = "auto",
        output_format: str = None,
        pdf_figsize: Union[Tuple[int, int], float] = None,
    ):

        if not isinstance(figure, MplFigure):
            raise TypeError(r"figure must be a Matplotlib Figure")

        self.content: MplFigure = figure
        self.width = _html_dim(width)
        self.height = _html_dim(height)
        self.output_format = output_format or options.matplotlib.html_output_format
        self.pdf_figsize = pdf_figsize or options.matplotlib.pdf_figsize

        self._original_figsize = figure.get_size_inches()

    def to_html(self, **kwargs):

        if kwargs.get("notebook_mode"):
            output_format = options.matplotlib.notebook_format
        else:
            output_format = self.output_format

        if kwargs.get("pdf_mode") and self.pdf_figsize:
            if isinstance(self.pdf_figsize, float):
                figsize = self.pdf_figsize * self._original_figsize
            else:
                figsize = self.pdf_figsize
            self.content.set_size_inches(*figsize)
            self.content.tight_layout()

        if output_format == "svg":

            buffer = StringIO()
            self.content.savefig(buffer, format="svg")
            buffer.seek(0)
            xml = buffer.read()

            dpi = 96
            width, height = self.content.get_size_inches() * dpi

            if kwargs.get("pdf_mode"):
                xml = responsive_svg_mpl(xml, width=int(width), height=int(height))
                temp_file = Path(options._pdf_temp_dir) / f"{uuid4()}.svg"
                temp_file.write_text(xml)
                inner = (
                    "<object type='image/svg+xml' width='100%' height='100%' "
                    f"data='{temp_file.name}'></object>\n"
                )
            else:
                xml = responsive_svg_mpl(xml)
                inner = xml

            max_scale_up = 1
            max_scale_down = 0.5
            html = (
                "<div class='row justify-content-center p-0 m-0' "
                "style='width: 100%; height: auto;'>\n"
                f"<div class='col p-0 m-0' style='max-width: min({int(width * max_scale_up)}px, 100%); "
                f"min-width: {int(width * max_scale_down)}px; height: auto;'>"
                f"{inner}\n</div>\n</div>\n"
            )

            # Reset figsize in case it was changed
            self.content.set_size_inches(*self._original_figsize)

            return html

        # If not svg:
        buffer = BytesIO()
        self.content.savefig(buffer, format="png")
        buffer.seek(0)
        return Image(buffer).to_html()


class FigureBokeh(Content):
    """Bokeh object to be rendered as an interactive plot.

    Args:
        figure (bokeh.layouts.LayoutDOM): A Bokeh object.
        width (int, str): Figure width. (default = figure.width or '100%')
        height (int, str): Figure height. (default = figure.height or 'auto')
        layout_attributes (dict): Attributes set on `figure`. (default = None)

    """

    _dependencies = {"bokeh"}

    def __init__(
        self,
        figure: "BokehObject",
        width: Union[int, str] = None,
        height: Union[int, str] = None,
        layout_attributes: dict = None,
    ):
        if not issubclass(type(figure), BokehObject):
            raise TypeError(r"figure must be a Bokeh object")

        self.content: BokehObject = figure

        fig_width = figure.properties_with_values().get("width")
        fig_height = figure.properties_with_values().get("height")

        self.width = _html_dim(width or fig_width or "100%")
        self.height = _html_dim(height or fig_height or "auto")

        self.layout_attributes = layout_attributes or options.bokeh.layout_attributes

    def to_html(self, **kwargs) -> str:

        if self.layout_attributes:
            for key, value in self.layout_attributes.items():
                setattr(self.content, key, value)

        # Bokeh to PDF is experimental and untested
        if kwargs.get("pdf_mode"):  # pragma: no cover
            from bokeh.io import export_svg  # type: ignore

            temp_file = Path(options._pdf_temp_dir) / f"{uuid4()}.svg"
            export_svg(self.content, filename=str(temp_file))
            html = f"<img src='{temp_file.name}' width='100%' height='auto'>\n"
            return html

        html, js = components(self.content)

        # Remove outer <div> tag so we can give our own attributes
        html = _remove_outer_div(html)

        return (
            "<div class='mb-3 es-bokeh-figure' "
            f"style='max-width: {self.width}; max-height: {self.height}; margin: auto;'>"
            f"\n{html}\n{js}\n</div>"
        )


class FigurePlotly(Content):
    """Plotly figure to be rendered as an interactive plot.

    Args:
        figure (plotly.graph_objs._figure.Figure): A Plotly figure.
        width (int): Figure width. (default = '100%')
        height (int): Figure height. (default = 500)
        layout_args (dict): Args passed to `figure.update_layout()`. (default = None)

    """

    _dependencies = {"plotly"}

    def __init__(
        self,
        figure: "PlotlyFigure",
        width: int = None,
        height: int = None,
        layout_args: dict = None,
    ):

        if not isinstance(figure, PlotlyFigure):
            raise TypeError(r"figure must be a Plotly Figure")

        self.width = _html_dim(width or int(figure.layout["width"] or 0) or "100%")  # type: ignore
        self.height = _html_dim(height or int(figure.layout["height"] or 0) or 500)  # type: ignore
        self.layout_args = layout_args or options.plotly.layout_args

        self.content: PlotlyFigure = figure
        self._original_layout = figure.layout

    def to_html(self, **kwargs) -> str:

        if self.layout_args:
            self.content.update_layout(**self.layout_args)

        if kwargs.get("pdf_mode"):
            temp_file = Path(options._pdf_temp_dir) / f"{uuid4()}.svg"
            self.content.write_image(str(temp_file))
            html = f"<img src='{temp_file.name}' width='100%' height='auto'>\n"

        else:
            html = plotly_to_html(self.content, include_plotlyjs=False, full_html=False)

            # Remove outer <div> tag so we can give our own attributes.
            html = _remove_outer_div(html)
            html = (
                "<div class='responsive-plot mb-3' "
                f"style='max-width: {self.width}; height: {self.height}; margin: auto;'>{html}\n</div>"
            )

        # Reset layout in case it was changed
        self.content.update_layout(self._original_layout)

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


def _html_dim(size: Union[int, str]) -> str:
    if isinstance(size, int):
        return f"{size}px"
    elif isinstance(size, str):
        return size
    else:
        raise TypeError(type(size))
