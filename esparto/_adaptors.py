from functools import singledispatch
from mimetypes import guess_type
from typing import Union, BinaryIO
from io import BytesIO

from PIL.Image import Image as PILImage  # type: ignore

from esparto import _installed_modules

from esparto._content import Content, DataFramePd, FigureMpl, Image, Markdown


@singledispatch
def content_adaptor(content: str) -> Content:
    guess = guess_type(content)
    if guess and "image" in str(guess[0]):
        return Image(content)
    else:
        return Markdown(content)


@content_adaptor.register
def ca_cb(content: Content) -> Content:
    return content


if "pandas" in _installed_modules:
    from pandas import DataFrame  # type: ignore

    @content_adaptor.register
    def ca_df(content: DataFrame) -> DataFramePd:
        return DataFramePd(content)


if "matplotlib" in _installed_modules:
    from matplotlib.figure import Figure  # type: ignore

    @content_adaptor.register
    def ca_fig(content: Figure) -> FigureMpl:
        return FigureMpl(content)
