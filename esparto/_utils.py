import re
from typing import Callable, Iterable, List


def get_index_where(condition: Callable[..., bool], iterable: Iterable) -> List[int]:
    """Return index values where `condition` is `True`."""
    return [idx for idx, item in enumerate(iterable) if condition(item)]


def get_matching_titles(title: str, children: list) -> List[int]:
    """Return child items with matching title."""
    return get_index_where(lambda x: getattr(x, "title", None) == title, children)


def clean_identifier(s: str):
    # Remove leading and trailing spaces
    s = s.strip().replace(" ", "_").lower()

    # Remove invalid characters
    s = re.sub("[^0-9a-zA-Z_]", "", s)

    # Remove leading characters until we find a letter or underscore
    s = re.sub("^[^a-zA-Z_]+", "", s)

    return s


def clean_iterator(iterator: Iterable) -> Iterable:
    # Convert any non-list iterators to lists
    iterator = (
        list(iterator)
        if hasattr(iterator, "__iter__") and not isinstance(iterator, str)
        else [iterator]
    )
    # Unnest any nested lists of children
    if len(list(iterator)) == 1 and isinstance(list(iterator)[0], (list, tuple)):
        iterator = list(iterator)[0]

    return iterator


# TODO: Set width and height of SVG
def responsive_svg_mpl(source: str, width: int = None, height: int = None) -> str:
    """Make SVG element responsive."""

    width_ = width or "auto"
    height_ = height or "auto"

    regex_w = r"width=\S*"
    regex_h = r"height=\S*"

    source = re.sub(regex_w, f"length='{width_}'", source, count=1)
    source = re.sub(regex_h, f"height='{height_}'", source, count=1)

    # Preserve aspect ratio of SVG
    regexp = r"<svg"
    repl = '<svg class="svg-content-mpl" preserveAspectRatio="xMinYMin meet" '
    source = re.sub(regexp, repl, source, count=1)

    return source
