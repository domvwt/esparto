import copy

from inspect import getmembers
from itertools import compress
from abc import ABC, abstractmethod
from typing import Any, Iterable, Optional, List, Type, Union

from esparto.content import Content
from esparto.publish import publish, nb_display


def _has_method(object: Any, method: str) -> bool:
    """

    Args:
      object: Any:
      method: str:

    Returns:

    """
    fn = getattr(object, method, None)
    return callable(fn)


def _check_content_renderable(items: Iterable) -> List[bool]:
    """

    Args:
      items: Iterable:

    Returns:

    """
    renderable = [_has_method(x, "to_html") for x in items]
    return renderable


class LayoutElement(ABC):
    """ """

    @abstractmethod
    def _render_title(self) -> str:
        """ """
        raise NotImplementedError

    @property
    def title(self) -> Optional[str]:
        """ """
        return self._title

    # Each element should return title with appropriate class
    @title.getter
    def title(self) -> Optional[str]:
        """ """
        return self._render_title()

    @title.setter
    def title(self, title: Optional[str]) -> None:
        """

        Args:
          title: Optional[str]:

        Returns:

        """
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
        """

        Args:
          children:

        Returns:

        """
        content = self._sanitize_content(content)
        self._content = content

    def _sanitize_content(self, content: Iterable[Any]) -> Iterable[Any]:
        content_: Iterable[Any] = (
            list(content) if hasattr(content, "__iter__") else [content]
        )
        renderable = _check_content_renderable(content_)
        unrenderable = list(compress(content_, [not x for x in renderable]))
        assert all(renderable), f"Child has no method '.to_html()':\n{unrenderable}"
        # Ensure children are wrapped in appropriate classes
        if not isinstance(self, Column):
            unwrapped = [x for x in content_ if not isinstance(x, self._child_class)]
            if any(unwrapped):
                wrapped = [x for x in content_ if x not in unwrapped]
                if isinstance(self, Row):
                    # If contents are elements of row, wrap in individual columns
                    newly_wrapped = [self._child_class(x) for x in unwrapped]
                else:
                    newly_wrapped = [self._child_class(*unwrapped)]
                content_ = newly_wrapped + wrapped
        return content_

    @property
    @abstractmethod
    def _child_class(self) -> Type["LayoutElement"]:
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
        *content: Union["LayoutElement", Content, None],
        title: Optional[str] = None,
    ):
        self.content = content
        self.title = title

    def __call__(self, *content: Union["LayoutElement", Content, None]):
        new = copy.deepcopy(self)
        if content:
            new.content = content
        return new

    def __add__(self, other):
        assert (
            hasattr(other, "content") and other.content
        ), "Item has no content to add."
        new = copy.deepcopy(self)
        new.content = [x for x in self.content + other.content if x is not None]
        return new

    def __iter__(self):
        return iter([self])

    def _repr_html_(self):
        nb_display(self)


class Page(LayoutElement):
    """ """

    def _render_title(self) -> str:
        """ """
        return f"<h2 class='display-4'>{self._title}</h2>\n"

    @property
    def _tag_open(self) -> str:
        """ """
        return "<main class='container my-4'>"

    @property
    def _tag_close(self) -> str:
        """ """
        return "</main>"

    @property
    def _child_class(self) -> Type["LayoutElement"]:
        return Section

    def __init__(
        self,
        *content: Union["LayoutElement", Content, None],
        title: Optional[str] = None,
        org_name: Optional[str] = None,
    ):
        super().__init__(*content, title=title)
        self.org_name = org_name if org_name else "Esparto"


class Section(LayoutElement):
    """ """

    def _render_title(self) -> str:
        """ """
        return f"<h2 class='mb-3'>{self._title}</h2>\n"

    @property
    def _tag_open(self) -> str:
        """ """
        return "<div class='container p-4'>"

    @property
    def _tag_close(self) -> str:
        """ """
        return "</div>"

    @property
    def _child_class(self) -> Type["LayoutElement"]:
        return Row


class Row(LayoutElement):
    """ """

    def _render_title(self) -> str:
        """ """
        return f"<h3 class='mb-2'>{self._title}</h3>\n"

    @property
    def _tag_open(self) -> str:
        """ """
        return "<div class='row'>"

    @property
    def _tag_close(self) -> str:
        """ """
        return "</div>"

    @property
    def _child_class(self) -> Type["LayoutElement"]:
        return Column


class Column(LayoutElement):
    """ """

    def _render_title(self) -> str:
        """ """
        return f"<h3 class='mb-2'>{self._title}</h3>\n"

    @property
    def _tag_open(self) -> str:
        """ """
        return "<div class='col'>"

    @property
    def _tag_close(self) -> str:
        """ """
        return "</div>"

    @property
    def _child_class(self) -> Any:
        raise NotImplementedError
