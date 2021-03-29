import copy
from abc import ABC, abstractmethod
from inspect import getmembers
from itertools import compress
from typing import TYPE_CHECKING, Any, Iterable, List, Optional, Type, Union

from esparto._publish import nb_display, publish

if TYPE_CHECKING:
    from esparto._content import Content


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
        content = self._smart_wrap(content)
        self._content = content

    def _sanitize_content(self, content: Iterable[Any]) -> Iterable[Any]:
        content_: Iterable[Any] = (
            list(content) if hasattr(content, "__iter__") else [content]
        )
        renderable = _check_content_renderable(content_)
        unrenderable = list(compress(content_, [not x for x in renderable]))
        assert all(renderable), f"Child has no method '.to_html()':\n{unrenderable}"

        return content_

    def _smart_wrap(self, content: Iterable[Any]) -> Iterable[Any]:
        """
        Wrap unwrapped content intelligently and preserve the order of content items.
        If the parent object is a Column:
            - Return the content with no modification
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

        if isinstance(self, Column):
            return content

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
        *content: Union["LayoutElement", "Content", None],
        title: Optional[str] = None,
    ):
        self.content = content
        self.title = title

    def __call__(self, *content: Union["LayoutElement", "Content", None]):
        new = copy.deepcopy(self)
        if content:
            new.content = content
        return new

    def __add__(self, other: object):
        # Hack to avoid circular import of Content class for instance checking
        if "Content" in [x.__name__ for x in other.__class__.__bases__]:
            other_content = [other]
        elif isinstance(other, LayoutElement):
            other_content = list(other.content)
        else:
            raise NotImplementedError

        new = copy.deepcopy(self)
        new.content = [x for x in list(self.content) + other_content]
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
        *content: Union["LayoutElement", "Content", None],
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
