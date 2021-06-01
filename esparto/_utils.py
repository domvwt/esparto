import re
from typing import Callable, Iterable, List


def get_index_where(condition: Callable[..., bool], iterable: Iterable) -> List[int]:
    """Return index values where `condition` is `True`."""
    return [idx for idx, item in enumerate(iterable) if condition(item)]


def get_matching_titles(title: str, children: list) -> List[int]:
    """Return child items with matching title."""
    return get_index_where(lambda x: getattr(x, "title", None) == title, children)


def clean_attr_name(attr_name: str):
    # Remove leading and trailing spaces
    attr_name = attr_name.strip().replace(" ", "_").lower()

    # Remove invalid characters
    attr_name = re.sub("[^0-9a-zA-Z_]", "", attr_name)

    # Remove leading characters until we find a letter or underscore
    attr_name = re.sub("^[^a-zA-Z_]+", "", attr_name)

    return attr_name


def clean_iterator(iterator: Iterable) -> Iterable:
    # Convert any non-list iterators to lists
    iterator = (
        list(iterator) if isinstance(iterator, (list, tuple, set)) else [iterator]
    )
    # Unnest any nested lists of children
    if len(list(iterator)) == 1 and isinstance(list(iterator)[0], (list, tuple, set)):
        iterator = list(iterator)[0]
    return iterator


def responsive_svg_mpl(source: str, width: int = None, height: int = None) -> str:
    """Make SVG element responsive."""

    regex_w = r"width=\S*"
    regex_h = r"height=\S*"

    width_ = f"width='{width}px'" if width else ""
    height_ = f"height='{height}px'" if height else ""

    source = re.sub(regex_w, width_, source, count=1)
    source = re.sub(regex_h, height_, source, count=1)

    # Preserve aspect ratio of SVG
    regexp = r"<svg"
    repl = '<svg class="svg-content-mpl" preserveAspectRatio="xMinYMin meet" '
    source = re.sub(regexp, repl, source, count=1)

    return source
