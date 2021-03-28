import base64
from abc import ABC, abstractmethod
from io import BytesIO
from typing import Any, Union

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
    def content(self) -> Any:
        raise NotImplementedError

    @content.getter
    def content(self) -> Any:
        raise NotImplementedError

    @content.setter
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


class Markdown(Content):
    """ """

    @property
    def content(self) -> Any:
        raise NotImplementedError

    @content.getter
    def content(self) -> Any:
        return self._content

    @content.setter
    def content(self, content) -> Any:
        self._content = content

    def __init__(self, text):
        self.content = str(text)

    def to_html(self) -> str:
        """ """
        html = f"{md.markdown(self.content)}\n"
        html = html.replace("<blockquote>", "<blockquote class='blockquote'>")
        # html = html.replace("<li>", "<li class='list-group-item'>")
        return html


class Spacer(Content):
    @property
    def content(self) -> Any:
        raise NotImplementedError

    @content.getter
    def content(self) -> Any:
        raise NotImplementedError

    @content.setter
    def content(self) -> Any:
        raise NotImplementedError

    def to_html(self) -> str:
        html = "<p></p>"
        return html


class Image(Content):
    """ """

    @property
    def content(self) -> Any:
        raise NotImplementedError

    @content.getter
    def content(self) -> Any:
        return self._content

    @content.setter
    def content(self, content) -> Any:
        self._content = content

    def __init__(
        self,
        image: Union[str, BytesIO],
        size: Union[str, float] = "auto",
        alt_text: str = "Image",
    ):
        self.content = image
        self.size = size
        self.alt_text = alt_text

    def resize(self, size) -> "Image":
        self.size = size
        return self

    def to_html(self):
        """ """
        image = pil.open(self.content)

        # Resize image if required
        if self.size == "auto":
            width = "100%"
        else:
            x = int(image.size[0] * self.size)
            y = int(image.size[1] * self.size)
            image.thumbnail((x, y))
            width = f"{x}px"

        image_encoded = _image_to_base64(image)
        html = f"<img src='data:image/png;base64,{image_encoded}' class='img-responsive' width='{width}'>"

        return html


class DataFramePd(Content):
    @property
    def content(self) -> Any:
        raise NotImplementedError

    @content.getter
    def content(self) -> Any:
        return self._content

    @content.setter
    def content(self, content) -> Any:
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


class FigureMpl(Content):
    """ """

    def __init__(self, figure: "Figure"):
        self.content = figure

    def to_html(self):
        """ """
        buffer = BytesIO()
        self.content.savefig(buffer, format="png")
        img_encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
        html = (
            f"<img src='data:image/png;base64,{img_encoded}'"
            + "class='img-fluid; object-fit: scale-down' width='100%'/>"
        )
        return html
