"""
Layout classes for defining an HTML document.
"""
import copy
from abc import ABC, abstractmethod
from inspect import getmembers
from pprint import pformat
from typing import TYPE_CHECKING, Any, Iterable, Optional, Type, Union
from warnings import warn

from esparto._publish import nb_display, publish


if TYPE_CHECKING:  # pragma: no cover
    from esparto._content import Content


class Layout(ABC):
    """Common methods for Layout elements.

    Attributes:
      title: Title for object reference and HTML rendering.
      content: Nested list of child elements representing the document tree.
    """

    # Each element should return title with appropriate HTML tags
    @abstractmethod
    def _render_title(self) -> str:
        """Each element should return its title with appropriate HTML tags."""
        raise NotImplementedError

    @property
    def title(self) -> Optional[str]:
        """Title for object reference and HTML rendering."""
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
    def content(self) -> Iterable:
        """Nested list of child elements representing the document tree.

        Layout and Content elements can be added to any existing Layout object.

        When an item is added to a Layout element it is automatically nested in a suitable child class
        and matched to an appropriate Content class as required.

        """
        raise NotImplementedError

    @content.getter
    def content(self) -> Iterable:
        """ """
        if hasattr(self, "_content"):
            content = self._content
        else:
            content = []
        return content

    @content.setter
    def content(self, content) -> None:
        """ """
        content = self._sanitize_content(content)
        content = self._smart_wrap(content)
        self._content = content

    def _sanitize_content(self, content: Iterable[Any]) -> Iterable[Any]:
        """Ensure new Content and Layout elements are in the correct format for further processing.

        Args:
          content: Iterable[Any]: Sequence of Layout and / or Content items.

        Returns:
          Iterable[Any]: Clean sequence of Layout and / or Content items.

        """
        # Convert any non-list iterators to lists
        content_: Iterable[Any] = (
            list(content)
            if hasattr(content, "__iter__") and not isinstance(content, str)
            else [content]
        )
        # Unnest any nested lists of content
        if len([x for x in content_]) == 1 and isinstance(
            list(content_)[0], (list, tuple)
        ):
            content_ = list(content_)[0]
        return content_

    def _smart_wrap(self, content: Iterable[Any]) -> Iterable[Any]:
        """Wrap new content in a coherent class hierarchy.

        If the parent object is a Column and the item is a Content Class:
            - return the content with no modification
        If the parent object is a Column and the item is not a Content Class:
            - cast the item to an appropriate Content Class if possible
            - return the item
        If the current item is wrapped and unwrapped items have been accumulated:
            - wrap the unwrapped items
            - append newly wrapped to output
            - append current item to output
        If the current item is wrapped and we have no accumulated unwrapped items:
            - append the current wrapped item to output
        If the current item is unwrapped and the parent is a Row:
            - wrap and append the current item to output
        If the current item is unwrapped and the parent is not a Row:
            - add the current item to unwrapped item accumulator
        Finally:
            - wrap any accumulated unwrapped items
            - append the final wrapped segment to output

        Args:
          content: Sequence of Content and / or Layout items.

        Returns:
          List of Layout and Content items wrapped in a coherent class hierarchy.

        """
        from esparto._adaptors import content_adaptor

        if isinstance(self, Column):
            return [content_adaptor(x) for x in content]

        is_row = isinstance(self, Row)
        unwrapped_acc: list = []
        output = []

        for item in content:
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
          HTML code.

        """
        content_rendered = " ".join([c.to_html() for c in self.content])
        title_rendered = f"{self._render_title()}\n" if self._title else None
        if title_rendered:
            html = f"{self._tag_open}\n{title_rendered}{content_rendered}\n{self._tag_close}\n"
        else:
            html = f"{self._tag_open}\n{content_rendered}\n{self._tag_close}\n"
        return html

    @property
    def _rendered(self) -> str:
        """Alias for method to_html. Used by Jinja."""
        return self.to_html()

    def display(self):
        """Display rendered document in a Jupyter Notebook cell."""
        nb_display(self)

    def save(
        self, filepath: Optional[str] = None, return_html: bool = False
    ) -> Optional[str]:
        """
        Render document to HTML and save to disk.

        Args:
          filepath: Destination filepath. (Optional)
          return_html: If True, return HTML as a string. (Default value = False)

        Returns:
          Document rendered as HTML. (If return_html is True)

        """
        html = publish(self, filepath, return_html)

        if return_html:
            return html
        else:
            return None

    def to_dict(self) -> dict:
        """Return object as a dictionary."""
        return dict(getmembers(self))

    def __init__(
        self,
        *content: Union["Layout", "Content", Any],
        title: Optional[str] = None,
    ):
        self.content = content
        self.title = title

    def __call__(self, *content: Union["Layout", "Content", None]):
        new = copy.deepcopy(self)
        if content:
            new.content = content
        return new

    def __add__(self, other: Union["Layout", "Content", Any]):
        if isinstance(other, type(self)):
            return self._parent_class(
                *(*self.content, *other.content), title=self.title
            )
        else:
            new = copy.deepcopy(self)
            new.content = (x for x in (*self.content, *other))
            return new

    def __iter__(self):
        return iter([self])

    def _repr_html_(self):
        """ """
        nb_display(self)

    def __repr__(self):
        title = self._title if self._title else "Untitled"
        return f"{type(self)}: {title}"

    def _recurse_content(self) -> dict:
        """ """
        key = self._title if self._title else type(self).__name__
        tree = {
            f"{key}": [
                x._recurse_content()
                if hasattr(x, "_recurse_content")
                else type(x).__name__
                for x in self.content
            ]
        }
        return tree

    def __str__(self):
        return pformat(self._recurse_content())

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._title == other._title and all(
                [x == y for x, y in zip(self.content, other.content)]
            )
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)


class Page(Layout):
    """Page - top level element for defining an HTML document.

    Args:
        *content:  Layout items to include in the Page.
        title: Page title.
        org_name: Organisation name.

    """

    def _render_title(self) -> str:
        """ """
        return f"<h2 class='display-4'>{self._title}</h2>\n"

    @property
    def _tag_open(self) -> str:
        """ """
        return "<main class='container p-4'>"

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
        *content: Union["Layout", "Content", Any],
        title: Optional[str] = None,
        org_name: Optional[str] = None,
    ):
        super().__init__(*content, title=title)
        self.org_name = org_name if org_name else "esparto"


class Section(Layout):
    """Section - defines a Section within a Page.

    Args:
        *content: Row items to include in the Section.
        title: Section title.

    """

    def _render_title(self) -> str:
        """ """
        return f"<h1 class='mb-6rem'>{self._title}</h1>\n"

    @property
    def _tag_open(self) -> str:
        """ """
        return "<div class='container p-3'>"

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
        *content: Column items to include in the Row.
        title: Row title. (for reference only, not rendered)

    """

    @property
    def title(self) -> Optional[str]:
        """ """
        raise NotImplementedError

    @title.getter
    def title(self) -> Optional[str]:
        """ """
        return self._title

    @title.setter
    def title(self, title: Optional[str]) -> None:
        """ """
        if title:
            warn("Row titles are not rendered - for reference use only")
        self._title = title

    def _render_title(self) -> str:
        """ """
        # Row should not return title
        return ""

    @property
    def _tag_open(self) -> str:
        """ """
        return "<div class='row container-sm'>"

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
        *content: Content to include in the Column.
        title: Column title.

    """

    def _render_title(self) -> str:
        """ """
        return f"<h3 class='mb-1rem'>{self._title}</h3>\n"

    @property
    def _tag_open(self) -> str:
        """ """
        return "<div class='col p-4'>"

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
