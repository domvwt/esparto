from typing import TYPE_CHECKING, Any, Union

if TYPE_CHECKING:
    from esparto._content import Content
    from esparto._layout import Layout

Child = Union["Layout", "Content", Any]
