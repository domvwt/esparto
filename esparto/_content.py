import base64
from abc import ABC, abstractmethod
from io import BytesIO
from typing import Any, BinaryIO, List, Union

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

    Args:
      image: PILImage:

    Returns:

    """
    buffer = BytesIO()
    image.save(buffer, format="png")
    image_encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return image_encoded


class Content(ABC):
    """ """

    @property
    @abstractmethod
    def content(self) -> Any:
        """ """
        raise NotImplementedError

    @abstractmethod
    def to_html(self) -> str:
        """ """
        raise NotImplementedError

    def display(self) -> None:
        """ """
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
    """ """

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
        """

        Args:
          content:

        Returns:

        """
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
    """ """

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
        """

        Args:
          other:

        Returns:

        """
        # Spacer has no content
        if other:
            raise AttributeError("Spacer cannot hold content.")
        return None

    def to_html(self) -> str:
        """ """
        html = "<p></p>"
        return html


class Image(Content):
    """ """

    @property
    def rescale(self) -> float:
        """ """
        raise NotImplementedError

    @rescale.getter
    def rescale(self) -> float:
        """ """
        return self._rescale

    @rescale.setter
    def rescale(self, rescale: float) -> None:
        """

        Args:
          rescale: float:

        Returns:

        """
        assert rescale <= 1, "Image can not be scaled over 100%"
        self._rescale = rescale

    @property
    def content(self) -> Union[str, BinaryIO]:
        """ """
        raise NotImplementedError

    @content.getter
    def content(self) -> Union[str, BinaryIO]:
        """ """
        return self._content

    @content.setter
    def content(self, content) -> None:
        """

        Args:
          content:

        Returns:

        """
        self._content = content

    def __init__(
        self,
        image: Union[str, BinaryIO, pil.Image],
        rescale: float = 1,
        alt_text: str = "Image",
    ):
        self.content = image
        self.rescale = rescale
        self.alt_text = alt_text

    def resize(self, size) -> "Image":
        """

        Args:
          size:

        Returns:

        """
        self.rescale = size
        return self

    def to_html(self) -> str:
        """ """
        if isinstance(self.content, pil.Image):
            image = self.content
        else:
            image = pil.open(self.content)

        # Resize image if required
        if self.rescale != 1:
            x = int(image.size[0] * self.rescale)
            y = int(image.size[1] * self.rescale)
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
    """ """

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
        """

        Args:
          content:

        Returns:

        """
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
    """ """

    def __init__(
        self,
        figure: "Figure",
        alt_text: str = "Image",
    ):
        buffer = BytesIO()
        figure.savefig(buffer, format="png")
        super().__init__(buffer, rescale=1, alt_text=alt_text)
