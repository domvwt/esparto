"""
Content classes for rendering common objects and markdown text to HTML.
"""
import base64
from abc import ABC, abstractmethod
from io import BytesIO
from typing import Any, Union

import markdown as md
import PIL.Image as pil  # type: ignore
from PIL.Image import Image as PILImage

from esparto import _installed_modules
from esparto._publish import nb_display

if "pandas" in _installed_modules:  # pragma: no cover
    from pandas import DataFrame  # type: ignore

if "matplotlib" in _installed_modules:  # pragma: no cover
    from matplotlib.figure import Figure  # type: ignore


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

    def __add__(self, other):
        from esparto._layout import Row  # Deferred for evade circular import

        return Row(self, other)

    def __iter__(self):
        return iter([self])

    def __len__(self):
        return len(self.content)

    def _repr_html_(self):
        """ """
        nb_display(self)

    def __str__(self):
        return str(self.__class__.__name__)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return all([x == y for x, y in zip(self.content, other.content)])
        else:
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

    def to_html(self) -> str:
        """ """
        html = md.markdown(self.content)
        html = f"{html}\n"
        html = f"<div class='container-fluid px-1'>\n{html}\n</div>"
        return html


class Image(Content):
    """Image content.

    Can be read from a filepath, PIL.Image object, or from bytes.

    Args:
      image (str, PIL.Image, BytesIO): Image data.
      caption (str): Image caption (default = None)
      alt_text (str): Alternative text. (default = None)
      scale (float): Value by which to scale image, must be > 0 and <= 1. (default = 1)

    """

    @property
    def scale(self) -> float:
        """ """
        raise NotImplementedError

    @scale.getter
    def scale(self) -> float:
        """ """
        return self._scale

    @scale.setter
    def scale(self, scale: float) -> None:
        """ """
        assert scale <= 1, "Image can not be scaled over 100%"
        self._scale = scale

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
        image: Union[str, pil.Image, BytesIO],
        alt_text: str = "Image",
        caption: str = "",
        scale: float = 1,
    ):

        if not isinstance(image, (str, pil.Image, BytesIO)):
            raise TypeError(r"image must be one of {str, pil.Image, BytesIO}")

        self.content = image
        self.alt_text = alt_text
        self.caption = caption
        self.scale = scale

    def rescale(self, scale) -> "Image":
        """
        Rescale the image prior to rendering.

        Note:
            Images can be scaled down only.

        Args:
          scale (float): Scaling ratio.

        """
        self.scale = scale
        return self

    def to_html(self) -> str:
        """ """
        if isinstance(self.content, pil.Image):
            image = self.content
        else:
            image = pil.open(self.content)

        # Resize image if required
        if self.scale != 1:
            x = int(image.size[0] * self.scale)
            y = int(image.size[1] * self.scale)
            image.thumbnail((x, y))

        width = f"{image.size[0]}px"
        height = f"{image.size[1]}px"

        image_encoded = _image_to_base64(image)
        html = (
            "<figure class='text-center'>"
            + "<img class='figure-img img-fluid rounded' "
            + f"alt='{self.alt_text}' "
            + f"height='{height}' width='{width}' "
            + f"src='data:image/png;base64,{image_encoded}'>"
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

    def to_html(self) -> str:
        """ """
        classes = "table table-sm table-striped table-hover table-bordered"
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
      scale (float): Value by which to scale image, must be > 0 and <= 1. (default = 1)

    """

    def __init__(
        self,
        figure: "Figure",
        caption: str = "",
        alt_text: str = "Image",
    ):

        if not isinstance(figure, Figure):
            raise TypeError(r"figure must be a Matplotlib Figure")

        buffer = BytesIO()
        figure.savefig(buffer, format="png")
        super().__init__(buffer, scale=1, caption=caption, alt_text=alt_text)
