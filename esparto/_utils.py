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


def clean_iterator(iter: Iterable) -> Iterable:
    # Convert any non-list iterators to lists
    iter = (
        list(iter)
        if hasattr(iter, "__iter__") and not isinstance(iter, str)
        else [iter]
    )
    # Unnest any nested lists of children
    if len(list(iter)) == 1 and isinstance(list(iter)[0], (list, tuple)):
        iter = list(iter)[0]

    return iter
