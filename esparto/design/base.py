"""Abstract design classes to help decoupling of domain from implementation."""

from abc import ABC
from typing import Any, List, Set, TypeVar, Union

T = TypeVar("T", bound="AbstractLayout")

Child = Union["AbstractLayout", "AbstractContent", Any]


class AbstractLayout(ABC):
    """Class Template for Layout elements.

    Layout class hierarchy:
        `Page -> Section -> Row -> Column -> Content`

    Attributes:
        title (str): Object title. Used as a title within the page and as a key value.
        children (list): Child items defining the page layout and content.
        title_classes (list): Additional CSS classes to apply to title.
        title_styles (dict): Additional CSS styles to apply to title.
        body_classes (list): Additional CSS classes to apply to body.
        body_styles (dict): Additional CSS styles to apply to body.

    """

    # ------------------------------------------------------------------------+
    #                              Public Methods                             |
    # ------------------------------------------------------------------------+

    def display(self) -> None:
        """Render content in a Notebook environment."""
        raise NotImplementedError

    def get_identifier(self) -> str:
        """Get the HTML element ID for the current object."""
        raise NotImplementedError

    def get_title_identifier(self) -> str:
        """Get the HTML element ID for the current object title."""
        raise NotImplementedError

    def set_children(self, other: Union[List[Child], Child]) -> None:
        """Set children as `other`."""
        raise NotImplementedError

    def to_html(self, **kwargs: bool) -> str:
        """Render object as HTML string.

        Returns:
            html (str): HTML string.

        """
        raise NotImplementedError

    def tree(self) -> None:
        """Display page tree."""
        raise NotImplementedError


class AbstractContent(ABC):
    """Template for Content elements.

    Attributes:
        content (Any): Item to be included in the page - should match the encompassing Content class.

    """

    content: Any
    _dependencies: Set[str]

    def to_html(self, **kwargs: bool) -> str:
        """Convert content to HTML string.

        Returns:
            str: HTML string.

        """
        raise NotImplementedError

    def display(self) -> None:
        """Display rendered content in a Jupyter Notebook cell."""
        raise NotImplementedError
