from typing import Callable, Iterable, List


def get_index_where(condition: Callable[..., bool], iterable: Iterable) -> List[int]:
    """Return index values where `condition` is `True`."""
    return [idx for idx, item in enumerate(iterable) if condition(item)]


def get_matching_titles(title: str, children: list) -> List[int]:
    """Return child items with matching title."""
    return get_index_where(lambda x: getattr(object, "title", None) == title, children)
