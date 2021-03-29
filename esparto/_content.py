import base64
from abc import ABC, abstractmethod
from io import BytesIO
from typing import Any, BinaryIO, List, Union

import markdown as md
import PIL.Image as pil  # type: ignore
from PIL.Image import Image as PILImage

from esparto import _installed_optional_dependencies
from esparto._layout import Row
from esparto._publish import nb_display

if "pandas" in _installed_optional_dependencies:
    from pandas import DataFrame  # type: ignore

if "matplotlib" in _installed_optional_dependencies:
    from matplotlib.figure import Figure  # type: ignore


def _image_to_base64(image: PILImage) -> str:
    """ """
    buffer = BytesIO()
    image.save(buffer, format="png")
    image_encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return image_encoded


class Content(ABC):
    """ """

    @property
    @abstractmethod
    def content(self) -> Any:
        raise NotImplementedError

    @abstractmethod
    def to_html(self) -> str:
        """ """
        raise NotImplementedError

    def display(self) -> None:
        nb_display(self)

    def __add__(self, other):
        return Row(self, other)

    def __iter__(self):
        return iter([self])

    def __len__(self):
        return len(self.content)

    def _repr_html_(self):
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
        raise NotImplementedError

    @content.getter
    def content(self) -> str:
        return self._content

    @content.setter
    def content(self, content) -> None:
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
        raise NotImplementedError

    @content.getter
    def content(self) -> List[None]:
        return []

    @content.setter
    def content(self) -> None:
        pass

    def to_html(self) -> str:
        html = "<p></p>"
        return html


class Image(Content):
    """ """

    @property
    def content(self) -> Union[str, BinaryIO]:
        raise NotImplementedError

    @content.getter
    def content(self) -> Union[str, BinaryIO]:
        return self._content

    @content.setter
    def content(self, content) -> None:
        self._content = content

    def __init__(
        self,
        image: Union[str, BytesIO, pil.Image],
        size: Union[str, float] = "auto",
        alt_text: str = "Image",
    ):
        self.content = image
        self.size = size
        self.alt_text = alt_text

    def resize(self, size) -> "Image":
        self.size = size
        return self

    def to_html(self) -> str:
        """ """
        if isinstance(self.content, pil.Image):
            image = self.content
        else:
            image = pil.open(self.content)

        # Resize image if required
        if self.size == "auto":
            width = "100%"
        else:
            x = int(image.size[0] * self.size)
            y = int(image.size[1] * self.size)
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
        raise NotImplementedError

    @content.getter
    def content(self) -> "DataFrame":
        return self._content

    @content.setter
    def content(self, content) -> None:
        self._content = content

    def __init__(
        self, df: "DataFrame", index: bool = False, col_space: Union[int, str] = 10
    ):
        self.content = df
        self.index = index
        self.col_space = col_space

    def to_html(self) -> str:
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
        super().__init__(buffer, size="auto", alt_text=alt_text)
