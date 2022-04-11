"""Content classes for rendering objects and markdown to HTML."""

import base64
import re
from abc import ABC, abstractmethod
from collections import namedtuple
from io import BytesIO, StringIO
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Set, Tuple, TypeVar, Union
from uuid import uuid4

import markdown as md

from esparto import _INSTALLED_MODULES
from esparto._options import options
from esparto.design.base import AbstractContent, AbstractLayout, Child
from esparto.design.layout import Row
from esparto.publish.output import nb_display

if "PIL" in _INSTALLED_MODULES:
    from PIL.Image import Image as PILImage  # type: ignore

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


T = TypeVar("T", bound="Content")


class Content(AbstractContent, ABC):
    """Template for Content elements.

    Attributes:
        content (Any): Item to be included in the page - should match the encompassing Content class.

    """

    content: Any
    _dependencies: Set[str]

    @abstractmethod
    def to_html(self, **kwargs: bool) -> str:
        """Convert content to HTML string.

        Returns:
            str: HTML string.

        """
        raise NotImplementedError

    def display(self) -> None:
        """Display rendered content in a Jupyter Notebook cell."""
        nb_display(self)

    def __add__(self, other: Child) -> "Row":
        from esparto.design.layout import Row

        return Row(children=[self, other])

    def __iter__(self) -> Iterator["Content"]:
        return iter([self])

    def __len__(self) -> int:
        return len(list(self.content))

    def _repr_html_(self) -> None:
        nb_display(self)

    def __str__(self) -> str:
        return getattr(self, "title", None) or self.__class__.__name__

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, self.__class__):
            if hasattr(self.content, "__iter__") and hasattr(other.content, "__iter__"):
                return all(x == y for x, y in zip(self.content, other.content))
            return bool(self.content == other.content)
        return False

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)


class RawHTML(Content):
    """Raw HTML content.

    Args:
        html (str): HTML string.

    """

    _dependencies: Set[Any] = set("")
    content: str

    def __init__(self, html: str) -> None:

        if not isinstance(html, str):
            raise TypeError(r"HTML must be str")

        self.content = html

    def to_html(self, **kwargs: bool) -> str:
        return self.content


class Markdown(Content):
    """Markdown text content.

    Args:
        text (str): Markdown text to be added to document.

    """

    _dependencies = {"bootstrap"}

    def __init__(self, text: str) -> None:

        if not isinstance(text, str):
            raise TypeError(r"text must be str")

        self.content: str = text

    def to_html(self, **kwargs: bool) -> str:
        html = md.markdown(self.content, extensions=["extra", "smarty"])
        html = f"{html}\n"
        html = f"<div class='es-markdown'>\n{html}\n</div>"
        return html


class Image(Content):
    """Image content.

    Can be read from a filepath, PIL.Image object, or from bytes..

    Args:
        image (str, Path, PIL.Image, BytesIO): Image data.
        caption (str): Image caption (default = None)
        alt_text (str): Alternative text. (default = None)
        scale (float): Scale image by proportion. (default = None)
        set_width (int): Set width in pixels. (default = None)
        set_height (int): Set height in pixels. (default = None)

    """

    _dependencies = {"bootstrap"}

    def __init__(
        self,
        image: Union[str, Path, "PILImage", BytesIO],
        caption: Optional[str] = "",
        alt_text: Optional[str] = "Image",
        scale: Optional[float] = None,
        set_width: Optional[int] = None,
        set_height: Optional[int] = None,
    ):

        valid_types: Tuple[Any, ...]

        if "PIL" in _INSTALLED_MODULES:
            valid_types = (str, Path, PILImage, BytesIO)
        else:
            valid_types = (str, Path, BytesIO)

        if not isinstance(image, (valid_types)):
            raise TypeError(r"`image` must be one of {}".format(valid_types))

        self.content = image
        self.alt_text = alt_text
        self.caption = caption
        self._scale = scale
        self._width = set_width
        self._height = set_height

    def set_width(self, width: int) -> None:
        """Set width of image.

        Args:
            width (int): New width in pixels.

        """
        self._width = width

    def set_height(self, height: int) -> None:
        """Set height of image.

        Args:
            height (int): New height in pixels.

        """
        self._height = height

    def rescale(self, scale: float) -> None:
        """Resize the image by a scaling factor.

        Args:
            scale (float): Scaling ratio.

        """
        self._scale = scale

    def to_html(self, **kwargs: bool) -> str:
        image_bytes = image_to_bytes(self.content)
        image_encoded = bytes_to_base64(image_bytes)

        width = f"min({self._width}, 100%)" if self._width else "auto"
        height = f"min({self._height}, 100%)" if self._height else "auto"
        scale = f"transform: scale({self._scale});" if self._scale else ""

        html = (
            "<figure class='es-figure'>"
            "<img class='img-fluid figure-img rounded es-image' "
            f"style='width: {width}; height: {height}; {scale}' "
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
            "table-hover",
        ]

    def to_html(self, **kwargs: bool) -> str:
        html: str = self.content.to_html(
            index=self.index,
            border=0,
            col_space=self.col_space,
            classes=self.css_classes,
        )
        html = f"<div class='table-responsive es-table'>{html}</div>"
        return html


class FigureMpl(Content):
    """Matplotlib figure.

    Args:
        figure (plt.Figure): A Matplotlib figure.
        output_format (str): 'svg' or 'png'. (default = None)
        pdf_figsize (tuple, float): Set figure size for PDF output. (default = None)
            Accepts a tuple of (height, width) or a float to use as scale factor.

    """

    _dependencies = {"bootstrap"}

    def __init__(
        self,
        figure: "MplFigure",
        output_format: Optional[str] = None,
        pdf_figsize: Optional[Union[Tuple[int, int], float]] = None,
    ) -> None:

        if not isinstance(figure, MplFigure):
            raise TypeError(r"figure must be a Matplotlib Figure")

        self.content: MplFigure = figure
        self.output_format = output_format or options.matplotlib.html_output_format
        self.pdf_figsize = pdf_figsize or options.matplotlib.pdf_figsize

        self._original_figsize = figure.get_size_inches()

    def to_html(self, **kwargs: bool) -> str:

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

        if output_format == "svg":

            string_buffer = StringIO()
            self.content.savefig(string_buffer, format="svg")
            string_buffer.seek(0)
            xml = string_buffer.read()

            dpi = 96
            fig_width, fig_height = (
                int(val * dpi) for val in self.content.get_size_inches()
            )

            if kwargs.get("pdf_mode"):
                xml = responsive_svg_mpl(
                    xml, width=int(fig_width), height=int(fig_height)
                )
                temp_file = Path(options._pdf_temp_dir) / f"{uuid4()}.svg"
                temp_file.write_text(xml)
                inner = (
                    "<object type='image/svg+xml' width='100%' height='100%' "
                    f"data='{temp_file.name}'></object>\n"
                )
            else:
                xml = responsive_svg_mpl(xml)
                inner = xml

            html = (
                f"<div class='es-matplotlib-figure' style='width: min({fig_width}px, 100%);'>"
                f"{inner}\n</div>\n"
            )

            # Reset figsize in case it was changed
            self.content.set_size_inches(*self._original_figsize)

            return html

        # If not svg:
        bytes_buffer = BytesIO()
        self.content.savefig(bytes_buffer, format="png")
        bytes_buffer.seek(0)
        return Image(bytes_buffer).to_html()


class FigureBokeh(Content):
    """Bokeh object to be rendered as an interactive plot.

    Args:
        figure (bokeh.layouts.LayoutDOM): A Bokeh object.
        layout_attributes (dict): Attributes set on `figure`. (default = None)

    """

    _dependencies = {"bokeh"}

    def __init__(
        self,
        figure: "BokehObject",
        layout_attributes: Optional[Dict[Any, Any]] = None,
    ):
        if not issubclass(type(figure), BokehObject):
            raise TypeError(r"figure must be a Bokeh object")

        self.content: BokehObject = figure
        self.layout_attributes = layout_attributes or options.bokeh.layout_attributes

    def to_html(self, **kwargs: bool) -> str:

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
        html = remove_outer_div(html)

        fig_width = self.content.properties_with_values().get("width", 1000)

        return (
            "<div class='es-bokeh-figure' "
            f"style='width: min({fig_width}px, 100%);'>"
            f"\n{html}\n{js}\n</div>"
        )


class FigurePlotly(Content):
    """Plotly figure to be rendered as an interactive plot.

    Args:
        figure (plotly.graph_objs._figure.Figure): A Plotly figure.
        layout_args (dict): Args passed to `figure.update_layout()`. (default = None)

    """

    _dependencies = {"plotly"}

    def __init__(
        self,
        figure: "PlotlyFigure",
        layout_args: Optional[Dict[Any, Any]] = None,
    ):

        if not isinstance(figure, PlotlyFigure):
            raise TypeError(r"figure must be a Plotly Figure")

        self.layout_args = layout_args or options.plotly.layout_args

        self.content: PlotlyFigure = figure
        self._original_layout = figure.layout

    def to_html(self, **kwargs: bool) -> str:

        if self.layout_args:
            self.content.update_layout(**self.layout_args)

        # Default width is 700, default height is 450
        fig_width: int = getattr(self.content, "width", 700)

        if kwargs.get("pdf_mode"):
            temp_file = Path(options._pdf_temp_dir) / f"{uuid4()}.svg"
            self.content.write_image(str(temp_file))
            inner = f"<img src='{temp_file.name}' width='100%' height='auto'>"

        else:
            inner = plotly_to_html(
                self.content, include_plotlyjs=False, full_html=False
            )
            # Remove outer <div> tag so we can give our own attributes.
            inner = remove_outer_div(inner)

        html = f"<div class='es-plotly-figure' style='width: min({fig_width}px, 100%);'>{inner}\n</div>"

        # Reset layout in case it was changed
        self.content.update_layout(self._original_layout)

        return html


def remove_outer_div(html: str) -> str:
    """Remove outer <div> tags."""
    html = html.replace("<div>", "", 1)
    html = "".join(html.rsplit("</div>", 1))
    return html


def image_to_bytes(image: Union[str, Path, BytesIO, "PILImage"]) -> BytesIO:
    """Convert `image` to bytes.

    Args:
        image (Union[str, Path, BytesIO, PIL.Image]): image object.

    Raises:
        TypeError: image type not recognised.

    Returns:
        BytesIO: image as bytes object.

    """
    if isinstance(image, BytesIO):
        return image
    elif "PIL" in _INSTALLED_MODULES and isinstance(image, PILImage):
        return BytesIO(image.tobytes())
    elif isinstance(image, (str, Path)):
        return BytesIO(Path(image).read_bytes())
    else:
        raise TypeError(type(image))


def bytes_to_base64(bytes: BytesIO) -> str:
    """
    Convert an image from bytes to base64 representation.

    Args:
        image (BytesIO): image bytes object.

    Returns:
        str: image encoded as a base64 utf-8 string.

    """
    return base64.b64encode(bytes.getvalue()).decode("utf-8")


def table_of_contents(
    object: AbstractLayout, max_depth: Optional[int] = None, numbered: bool = True
) -> "Markdown":
    """Produce table of contents for a Layout object.

    Args:
        object (Layout): Target object for TOC.
        max_depth (int): Maximum depth of returned TOC.
        numbered (bool): If True TOC items are numbered.
            If False, bulletpoints are used.

    """
    from esparto.design.content import Markdown

    max_depth = max_depth or 99

    TOCItem = namedtuple("TOCItem", "title, level, id")

    def get_toc_items(parent: AbstractLayout) -> List[TOCItem]:
        def find_ids(parent: Any, level: int, acc: List[TOCItem]) -> List[TOCItem]:
            if hasattr(parent, "get_title_identifier") and parent.title:
                acc.append(TOCItem(parent.title, level, parent.get_title_identifier()))
                level += 1
            if hasattr(parent, "children"):
                for child in parent.children:
                    find_ids(child, level, acc)
            else:
                return acc
            return acc

        acc_new = find_ids(parent, 0, [])
        return acc_new

    toc_items = get_toc_items(object)

    tab = "\t"
    marker = "1." if numbered else "*"
    markdown_list = [
        f"{(item.level - 1) * tab} {marker} [{item.title}](#{item.id})"
        for item in toc_items
        if item.level > 0 and item.level <= max_depth
    ]
    markdown_str = "\n".join(markdown_list)

    return Markdown(markdown_str)


def responsive_svg_mpl(
    source: str, width: Optional[int] = None, height: Optional[int] = None
) -> str:
    """Make SVG element responsive."""

    regex_w = r"width=\S*"
    regex_h = r"height=\S*"

    width_ = f"width='{width}px'" if width else ""
    height_ = f"height='{height}px'" if height else ""

    source = re.sub(regex_w, width_, source, count=1)
    source = re.sub(regex_h, height_, source, count=1)

    # Preserve aspect ratio of SVG
    old_str = r"<svg"
    new_str = '<svg class="svg-content-mpl" preserveAspectRatio="xMinYMin meet" '
    source = source.replace(old_str, new_str, 1)

    return source
