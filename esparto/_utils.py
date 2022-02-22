import re
from typing import TYPE_CHECKING, Any, Callable, Dict, Iterable, List, Optional

if TYPE_CHECKING:
    from esparto._typing import Child


def get_index_where(
    condition: Callable[..., bool], iterable: Iterable[Any]
) -> List[int]:
    """Return index values where `condition` is `True`."""
    return [idx for idx, item in enumerate(iterable) if condition(item)]


def get_matching_titles(title: str, children: List["Child"]) -> List[int]:
    """Return child items with matching title."""
    return get_index_where(lambda x: bool(getattr(x, "title", None) == title), children)


def clean_attr_name(attr_name: str) -> str:
    """Remove invalid characters from the attribute name."""
    if not attr_name:
        return ""

    # Remove leading and trailing spaces
    attr_name = attr_name.strip().replace(" ", "_").lower()

    # Remove invalid characters
    attr_name = re.sub("[^0-9a-zA-Z_]", "", attr_name)

    # Remove leading characters until we find a letter or underscore
    attr_name = re.sub("^[^a-zA-Z_]+", "", attr_name)

    return attr_name


def clean_iterator(iterator: Iterable[Any]) -> Iterable[Any]:
    # Convert any non-list iterators to lists
    iterator = (
        list(iterator) if isinstance(iterator, (list, tuple, set)) else [iterator]
    )
    # Un-nest any nested lists of children
    if len(list(iterator)) == 1 and isinstance(list(iterator)[0], (list, tuple, set)):
        iterator = list(iterator)[0]
    return iterator


def public_dict(d: Dict[str, Any]) -> Dict[str, Any]:
    """Remove keys starting with '_' from dict."""
    return {
        k: v for k, v in d.items() if not (isinstance(k, str) and k.startswith("_"))
    }


def render_html(
    tag: str,
    classes: List[str],
    styles: Dict[str, str],
    children: str,
    identifier: Optional[str] = None,
) -> str:
    """Render HTML from provided attributes."""
    class_str = " ".join(classes) if classes else ""
    class_str = f"class='{class_str}'" if classes else ""

    style_str = "; ".join((f"{key}: {value}" for key, value in styles.items()))
    style_str = f"style='{style_str}'" if styles else ""

    id_str = f"id='{identifier}'" if identifier else ""

    rendered = " ".join((f"<{tag} {id_str} {class_str} {style_str}>").split())
    rendered += f"\n  {children}\n</{tag}>"

    return rendered


def responsive_svg_mpl(
    source: str, width: Optional[int] = None, height: Optional[int] = None
) -> str:
    """Make SVG element responsive."""

    regex_w = r"width=\S*"
    regex_h = r"height=\S*"

    width_ = f"width='{width}px'" if width else ""
    height_ = f"height='{height}px'" if height else ""

    source = re.sub(regex_w, width_, source, count=1)
    source = re.sub(regex_h, height_, source, count=1)

    # Preserve aspect ratio of SVG
    old_str = r"<svg"
    new_str = '<svg class="svg-content-mpl" preserveAspectRatio="xMinYMin meet" '
    source = source.replace(old_str, new_str, 1)

    return source
