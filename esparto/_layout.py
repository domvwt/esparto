"""
Layout classes for defining a document.
"""
import copy
from abc import ABC, abstractmethod
from inspect import getmembers
from pprint import pformat
from typing import TYPE_CHECKING, Any, Iterable, Optional, Type, Union

from esparto._publish import nb_display, publish


if TYPE_CHECKING:  # pragma: no cover
    from esparto._content import Content


class Layout(ABC):
    """Template for Layout elements. All Layout classes come with these methods and attributes.

    Attributes:
      title (str): Title for object reference and HTML rendering.
      children (list): Child elements representing the document tree.
    """

    # Each element should return title with appropriate HTML tags
    @abstractmethod
    def _render_title(self) -> str:
        """Each element should return its title with appropriate HTML tags."""
        raise NotImplementedError

    @property
    def title(self) -> Optional[str]:
        """Title for use in document layout and as object reference."""
        raise NotImplementedError

    @title.getter
    def title(self) -> Optional[str]:
        """ """
        return self._title

    @title.setter
    def title(self, title: Optional[str]) -> None:
        """ """
        self._title = title

    @property
    def children(self) -> list:
        """List of child elements representing the document tree.

        Layout and Content elements can be added to any existing Layout object.

        When an item is added to a Layout element it is automatically nested in a suitable child class
        and matched to an appropriate Content class as required.

        """
        raise NotImplementedError

    @children.getter
    def children(self) -> Iterable:
        """ """
        if hasattr(self, "_children"):
            children = self._children
        else:
            children = []
        return children

    @children.setter
    def children(self, children) -> None:
        """ """
        children = self._sanitize_child_iter(children)
        children = self._smart_wrap(children)
        self._children = children

    def _sanitize_child_iter(self, children: Iterable[Any]) -> Iterable[Any]:
        """Ensure new Content and Layout elements are in the correct format for further processing.

        Args:
          children: Iterable[Any]: Sequence of Layout and / or Content items.

        Returns:
          Iterable[Any]: Clean sequence of Layout and / or Content items.

        """
        # Convert any non-list iterators to lists
        children_: Iterable[Any] = (
            list(children)
            if hasattr(children, "__iter__") and not isinstance(children, str)
            else [children]
        )
        # Unnest any nested lists of children
        if len([x for x in children_]) == 1 and isinstance(
            list(children_)[0], (list, tuple)
        ):
            children_ = list(children_)[0]
        return children_

    def _smart_wrap(self, children: Iterable[Any]) -> Iterable[Any]:
        """Wrap children in a coherent class hierarchy.

        Args:
          children: Sequence of Content and / or Layout items.

        Returns:
          List of Layout and Content items wrapped in a coherent class hierarchy.


        If the parent object is a Column and the item is a Content Class:
            - return child with no modification
        If the parent object is a Column and the item is not a Content Class:
            - cast the child to an appropriate Content Class if possible
            - return the child
        If the current item is wrapped and unwrapped items have been accumulated:
            - wrap the unwrapped children
            - append newly wrapped to output
            - append current child to output
        If the current child is wrapped and we have no accumulated unwrapped items:
            - append the wrapped child to output
        If the current child is unwrapped and the parent is a Row:
            - wrap and append the current child to output
        If the current item is unwrapped and the parent is not a Row:
            - add the current child to unwrapped item accumulator
        Finally:
            - wrap any accumulated unwrapped items
            - append the final wrapped segment to output

        """
        from esparto._adaptors import content_adaptor

        if isinstance(self, Column):
            return [content_adaptor(x) for x in children]

        is_row = isinstance(self, Row)
        unwrapped_acc: list = []
        output = []

        for item in children:
            is_wrapped = isinstance(item, self._child_class)

            if is_wrapped:
                if unwrapped_acc:
                    wrapped_segment = self._child_class(*unwrapped_acc)
                    output.append(wrapped_segment)
                    output.append(item)
                    unwrapped_acc = []
                else:
                    output.append(item)
            else:  # if not is_wrapped
                if is_row:
                    assert (
                        not unwrapped_acc
                    ), "Elements should not be accumulated for row"
                    output.append(self._child_class(item))
                else:
                    unwrapped_acc.append(item)

        if unwrapped_acc:
            wrapped_segment = self._child_class(*unwrapped_acc)
            output.append(wrapped_segment)

        return output

    @property
    @abstractmethod
    def _parent_class(self) -> Type["Layout"]:
        """Parent class - used by _smart_wrap."""
        raise NotImplementedError

    @property
    @abstractmethod
    def _child_class(self) -> Type["Layout"]:
        """Child class - used by _smart_wrap."""
        raise NotImplementedError

    @property
    @abstractmethod
    def _tag_open(self) -> str:
        """Opening HTML tag and arguments."""
        raise NotImplementedError

    @property
    @abstractmethod
    def _tag_close(self) -> str:
        """Closing HTML tag."""
        raise NotImplementedError

    def to_html(self) -> str:
        """Render document to HTML code.

        Returns:
          str: HTML code.

        """
        children_rendered = " ".join([c.to_html() for c in self.children])
        title_rendered = f"{self._render_title()}\n" if self._title else None
        if title_rendered:
            html = f"{self._tag_open}\n{title_rendered}{children_rendered}\n{self._tag_close}\n"
        else:
            html = f"{self._tag_open}\n{children_rendered}\n{self._tag_close}\n"
        return html

    @property
    def _rendered(self) -> str:
        """Alias for method to_html. Used by Jinja."""
        return self.to_html()

    def display(self):
        """Display rendered document in a Jupyter Notebook cell."""
        nb_display(self)

    def save(
        self, filepath: str = "./esparto-doc.html", return_html: bool = False
    ) -> Optional[str]:
        """
        Render document to HTML and save to disk.

        Args:
          filepath: Destination filepath. (default = './esparto-doc.html')
          return_html: If True, return HTML as a string.

        Returns:
          Document rendered as HTML. (If 'return_html' is True)

        """
        html = publish(self, filepath=filepath, return_html=return_html)

        if return_html:
            return html
        else:
            return None

    def to_dict(self) -> dict:
        """Return object as a dictionary."""
        return dict(getmembers(self))

    def __init__(
        self,
        *children: Union["Layout", "Content", Any],
        title: Optional[str] = None,
    ):
        self.children = list(children)
        self.title = title

    def __call__(self, *children: Union["Layout", "Content", None]):
        new = copy.deepcopy(self)
        if children:
            new.children = list(children)
        return new

    def __add__(self, other: Union["Layout", "Content", Any]):
        from esparto._content import Content

        if isinstance(other, type(self)):
            return self._parent_class(
                *(*self.children, *other.children), title=self.title
            )

        new = copy.deepcopy(self)
        new.children = self.children

        if isinstance(other, (Layout, Content, list, tuple)):
            new.children += list(other)
        else:
            from esparto._adaptors import content_adaptor

            new.children += [content_adaptor(other)]

        return new

    def __iter__(self):
        return iter([self])

    def _repr_html_(self):
        """ """
        nb_display(self)

    def __repr__(self):
        title = self._title if self._title else "Untitled"
        return f"{type(self)}: {title}"

    def _recurse_children(self) -> dict:
        """ """
        key = self._title if self._title else type(self).__name__
        tree = {
            f"{key}": [
                x._recurse_children()
                if hasattr(x, "_recurse_children")
                else type(x).__name__
                for x in self.children
            ]
        }
        return tree

    def __str__(self):
        return pformat(self._recurse_children())

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._title == other._title and all(
                [x == y for x, y in zip(self.children, other.children)]
            )
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)


class Page(Layout):
    """Page - top level element for defining a document.

    Args:
        *children (Layout, optional):  Layout items to include in the Page.
        title (str, optional): Page title.
        org_name (str, optional): Organisation name.

    """

    def _render_title(self) -> str:
        """ """
        return f"<h1 class='display-4 my-3'>{self._title}</h1>\n"

    @property
    def _tag_open(self) -> str:
        """ """
        return "<main class='container px-2'>"

    @property
    def _tag_close(self) -> str:
        """ """
        return "</main>"

    @property
    def _parent_class(self) -> Type["Layout"]:
        """ """
        return Page

    @property
    def _child_class(self) -> Type["Layout"]:
        """ """
        return Section

    def __init__(
        self,
        *children: Union["Layout", "Content", Any],
        title: Optional[str] = None,
        org_name: Optional[str] = None,
    ):
        super().__init__(*children, title=title)
        self.org_name = org_name if org_name else "esparto"


class Section(Layout):
    """Section - defines a Section within a Page.

    Args:
        *children: Row items to include in the Section.
        title: Section title.

    """

    def _render_title(self) -> str:
        """ """
        return f"<h2 class='mb-3'>{self._title}</h2>\n"

    @property
    def _tag_open(self) -> str:
        """ """
        return "<div class='px-1 mb-5'>"

    @property
    def _tag_close(self) -> str:
        """ """
        return "</div>"

    @property
    def _parent_class(self) -> Type["Layout"]:
        """ """
        return Page

    @property
    def _child_class(self) -> Type["Layout"]:
        """ """
        return Row


class Row(Layout):
    """Row -  defines a Row within a Section.

    Args:
        *children: Column items to include in the Row.
        title: Row title.

    """

    def _render_title(self) -> str:
        """ """
        return f"<div class='col-12'><h5 class='px-1 mb-3'>{self._title}</h5></div>\n"

    @property
    def _tag_open(self) -> str:
        """ """
        return "<div class='row'>"

    @property
    def _tag_close(self) -> str:
        """ """
        return "</div>"

    @property
    def _parent_class(self) -> Type["Layout"]:
        """ """
        return Section

    @property
    def _child_class(self) -> Type["Layout"]:
        """ """
        return Column


class Column(Layout):
    """Column -  defines a Column within a Row.

    Args:
        *children: Content to include in the Column.
        title: Column title.

    """

    def _render_title(self) -> str:
        """ """
        return f"<h5 class='px-1 mb-3'>{self._title}</h5>\n"

    @property
    def _tag_open(self) -> str:
        """ """
        return "<div class='col-lg mb-3'>"

    @property
    def _tag_close(self) -> str:
        """ """
        return "</div>"

    @property
    def _parent_class(self) -> Type["Layout"]:
        """ """
        return Row

    @property
    def _child_class(self) -> Any:
        """ """
        raise NotImplementedError
