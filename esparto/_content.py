"""
Content classes for rendering common objects and markdown text to HTML.
"""
import base64
from abc import ABC, abstractmethod
from io import BytesIO
from typing import Any, List, Union

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
        self.content = str(text)

    def to_html(self) -> str:
        """ """
        html = f"{md.markdown(self.content)}\n"
        html = html.replace("<blockquote>", "<blockquote class='blockquote'>")
        html = f"<div class='container-fluid p-1'>\n{html}\n</div>"
        return html


class Spacer(Content):
    """Spacer for adding empty space to a Row."""

    @property
    def content(self) -> None:
        """ """
        raise NotImplementedError

    @content.getter
    def content(self) -> List[None]:
        """ """
        # Spacer has no content
        return []

    @content.setter
    def content(self, other) -> None:
        """ """
        # Spacer has no content
        if other:
            raise AttributeError("Spacer cannot hold content.")
        return None

    def to_html(self) -> str:
        """ """
        html = "<p></p>"
        return html


class Image(Content):
    """Image content.

    Can be read from a filepath, PIL.Image object, or from bytes.

    Args:
      image (str, PIL.Image, BytesIO): Image data.
      alt_text (str): Alternative text for rendered document.

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
        scale: float = 1,
        alt_text: str = "Image",
    ):
        self.content = image
        self.scale = scale
        self.alt_text = alt_text

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
            f"<img width='{width}' height='{height}' src='data:image/png;base64,{image_encoded}' "
            + "style='margin: auto; display: block'>"
        )

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
      alt_text (str): Alternative text for rendered document.

    """

    def __init__(
        self,
        figure: "Figure",
        alt_text: str = "Image",
    ):
        buffer = BytesIO()
        figure.savefig(buffer, format="png")
        super().__init__(buffer, scale=1, alt_text=alt_text)
