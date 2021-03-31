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
    """ """

    # Each element should return title with appropriate HTML tags
    @abstractmethod
    def _render_title(self) -> str:
        """ """
        raise NotImplementedError

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
        self._title = title

    @property
    def content(self) -> Iterable:
        """ """
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
        # Convert any not list iterators to lists
        content_: Iterable[Any] = (
            list(content)
            if hasattr(content, "__iter__") and not isinstance(content, str)
            else [content]
        )
        # Unnest any content passed inside a nested list
        if len([x for x in content_]) == 1 and isinstance(
            list(content_)[0], (list, tuple)
        ):
            content_ = list(content_)[0]
        return content_

    def _smart_wrap(self, content: Iterable[Any]) -> Iterable[Any]:
        """
        Wrap unwrapped content intelligently and preserve the order of content items.
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
        """
        from esparto._adaptors import content_adaptor
        from esparto._content import Content

        if isinstance(self, Column):
            return [
                x if isinstance(x, Content) else content_adaptor(x) for x in content
            ]

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
        else:
            if unwrapped_acc:
                wrapped_segment = self._child_class(*unwrapped_acc)
                output.append(wrapped_segment)

        return output

    @property
    @abstractmethod
    def _parent_class(self) -> Type["Layout"]:
        """ """
        raise NotImplementedError

    @property
    @abstractmethod
    def _child_class(self) -> Type["Layout"]:
        """ """
        raise NotImplementedError

    @property
    @abstractmethod
    def _tag_open(self) -> str:
        """ """
        raise NotImplementedError

    @property
    @abstractmethod
    def _tag_close(self) -> str:
        """ """
        raise NotImplementedError

    def to_html(self) -> str:
        """Render current object and children to HTML string.

        Args:

        Returns:
            str:

        """
        content_rendered = " ".join([c.to_html() for c in self.content])
        title_rendered = f"{self._render_title()}\n" if self._title else None
        if title_rendered:
            html = f"{self._tag_open}\n{title_rendered}{content_rendered}\n{self._tag_close}\n"
        else:
            html = f"{self._tag_open}\n{content_rendered}\n{self._tag_close}\n"
        return html

    @property
    def rendered(self) -> str:
        return self.to_html()

    def display(self):
        nb_display(self)

    def save(self, filepath: Optional[str] = None) -> None:
        publish(self, filepath)

    def to_dict(self) -> dict:
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
        nb_display(self)

    def __repr__(self):
        title = self._title if self._title else "Untitled"
        return f"{type(self)}: {title}"

    def _recurse_content(self) -> dict:
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
    """ """

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
    """ """

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
        return Row


class Row(Layout):
    """ """

    @property
    def title(self) -> Optional[str]:
        """ """
        raise NotImplementedError

    # Each element should return title with appropriate HTML tags
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
        return Column


class Column(Layout):
    """ """

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
        raise NotImplementedError
