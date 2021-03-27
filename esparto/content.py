import base64
from abc import ABC, abstractmethod
from io import BytesIO
from typing import Union

import markdown as md
import PIL.Image as pil
from PIL.Image import Image as PILImage


def _image_to_base64(image: PILImage) -> str:
    """ """
    buffer = BytesIO()
    image.save(buffer, format="png")
    image_encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return image_encoded


class Adaptor(ABC):
    """ """

    @abstractmethod
    def to_html(self) -> str:
        """ """
        raise NotImplementedError


class MatplotlibFigure(Adaptor):
    """ """

    def __init__(self, figure):
        self.figure = figure

    def to_html(self):
        """ """
        buffer = BytesIO()
        self.figure.savefig(buffer, format="png")
        img_encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
        html = f"<img src='data:image/png;base64,{img_encoded}' class='img-fluid' width='100%'/>"
        return html


class Markdown(Adaptor):
    """ """

    def __init__(self, text):
        self.text = text

    def to_html(self) -> str:
        """ """
        html = f"\n{md.markdown(self.text)}\n"
        html = html.replace("<blockquote>", "<blockquote class='blockquote'>")
        # html = html.replace("<li>", "<li class='list-group-item'>")
        return html


class Image(Adaptor):
    """ """

    def __init__(
        self,
        image: Union[str, BytesIO],
        size: Union[str, float] = "auto",
        alt_text: str = "Image",
    ):
        self.image = image
        self.size = size
        self.alt_text = alt_text

    def to_html(self):
        """ """
        image = pil.open(self.image)

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
