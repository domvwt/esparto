from functools import singledispatch
from mimetypes import guess_type


from esparto import _installed_modules

from esparto._content import Content, DataFramePd, FigureMpl, Image, Markdown


@singledispatch
def content_adaptor(content: str) -> Content:
    guess = guess_type(content)
    if guess and "image" in str(guess[0]):
        return Image(content)
    else:
        return Markdown(content)


@content_adaptor.register(Content)
def ca_cb(content: Content) -> Content:
    return content


if "pandas" in _installed_modules:
    from pandas.core.frame import DataFrame  # type: ignore

    @content_adaptor.register(DataFrame)
    def ca_df(content: DataFrame) -> DataFramePd:
        return DataFramePd(content)


if "matplotlib" in _installed_modules:
    from matplotlib.figure import Figure  # type: ignore

    @content_adaptor.register(Figure)
    def ca_fig(content: Figure) -> FigureMpl:
        return FigureMpl(content)
