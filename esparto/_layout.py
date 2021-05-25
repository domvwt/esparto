"""Layout classes for defining a document."""

import copy
from abc import ABC, abstractmethod
from pprint import pformat
from typing import TYPE_CHECKING, Any, Dict, Iterable, Optional, Set, Type, Union

from esparto._publish import nb_display, publish_html, publish_pdf
from esparto._utils import clean_identifier, clean_iterator, get_matching_titles

if TYPE_CHECKING:
    from esparto._content import Content


# TODO: Update documentation for get / set item
# TODO: Order class methods properly
# TODO: Warning about printing from HTML opened via Jupyter
# TODO: Print option in new footer style
# TODO: New page style in jinja template
# TODO: Fix wonky tables
class Layout(ABC):
    """Template for Layout elements. All Layout classes come with these methods and attributes.

    Attributes:
      title (str): Title for object reference and HTML rendering.
      children (list): Child elements representing the document tree.

    """

    title: Optional[str]
    _parent_class: Type["Layout"]
    _child_class: Type["Layout"]
    _tag_open: str
    _tag_close: str
    _dependencies = {"bootstrap"}
    _child_ids: Dict[str, str] = dict()

    @abstractmethod
    def _render_title(self) -> str:
        """Each element should return its title with appropriate HTML tags."""
        raise NotImplementedError

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
        return getattr(self, "_children", [])

    @children.setter
    def children(self, children) -> None:
        """ """
        children = self._smart_wrap(children)
        self._children = children

    def _smart_wrap(
        self, children: Iterable[Any]
    ) -> Iterable[Union["Layout", "Content"]]:
        """Wrap children in a coherent class hierarchy.

        Args:
          children: Sequence of Content and / or Child items.

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

        children = clean_iterator(children)

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

    def to_html(self, **kwargs) -> str:
        """Render document to HTML code.

        Returns:
          str: HTML code.

        """
        children_rendered = " ".join([c.to_html(**kwargs) for c in self.children])
        title_rendered = f"{self._render_title()}\n" if self.title else None
        if title_rendered:
            html = f"{self._tag_open}\n{title_rendered}{children_rendered}\n{self._tag_close}\n"
        else:
            html = f"{self._tag_open}\n{children_rendered}\n{self._tag_close}\n"
        return html

    def tree(self) -> str:
        """String representation of the document tree.

        Returns:
            str: Formatted string.

        """
        return pformat(self._recurse_children(idx=0))

    def display(self) -> None:
        """Display rendered document in a Notebook environment."""
        nb_display(self)

    def _recurse_children(self, idx) -> dict:
        """ """
        key = self.title or f"{type(self).__name__} {idx}"
        tree = {
            f"{key}": [
                child._recurse_children(idx)
                if hasattr(child, "_recurse_children")
                else str(child)
                for idx, child in enumerate(self.children)
            ]
        }
        return tree

    def _required_dependencies(self) -> Set[str]:
        """ """
        deps: Set[str] = self._dependencies

        def dep_finder(item):
            nonlocal deps
            for child in item.children:
                deps = deps | set(getattr(child, "_dependencies", None))
                if hasattr(child, "children"):
                    dep_finder(child)

        dep_finder(self)
        return deps

    def __init__(
        self,
        *children: Union["Layout", "Content", Any],
        title: Optional[str] = None,
    ):
        self.children = list(children)
        self.title = title

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

    def __repr__(self):
        return self.tree()

    def __str__(self):
        return self.tree()

    # TODO: Add this to docs
    def __lshift__(self, other: Union["Layout", "Content", Any]):
        from esparto._content import Content

        if isinstance(other, (Layout, Content, list, tuple)):
            self.children = list(other)
        else:
            from esparto._adaptors import content_adaptor

            self.children = [content_adaptor(other)]
        return other

    def __iter__(self):
        return iter([self])

    def _repr_html_(self):
        """ """
        self.display()

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.title == other.title and all(
                (x == y for x, y in zip(self.children, other.children))
            )
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __getattribute__(self, key: str) -> Any:
        child_id = super().__getattribute__("_child_ids").get(key)
        if child_id:
            return self.__getitem__(child_id)
        return super().__getattribute__(key)

    def __setattr__(self, key: str, value: Any) -> None:
        child_id = super().__getattribute__("_child_ids").get(key)
        if child_id:
            self.__setitem__(child_id, value)
        else:
            super().__setattr__(key, value)

    def __getitem__(self, key: Union[str, int]):
        if isinstance(key, str):
            indexes = get_matching_titles(key, self.children)
            if len(indexes):
                return self.children[indexes[0]]
            value = self._child_class(title=key)
            self.children.append(value)
            if key:
                self._add_child_id(key)
            return self[key]

        elif isinstance(key, int) and key < len(self.children):
            return self.children[key]

        raise KeyError(key)

    def __setitem__(self, key: Union[str, int], value: Any):
        value = self._smart_wrap(value)
        value = value[0]
        if isinstance(key, str):
            if key:
                value.title = key
                indexes = get_matching_titles(key, self.children)
                if len(indexes):
                    self.children[indexes[0]] = value
                else:
                    self.children.append(value)
            if key:
                self._add_child_id(key)
        else:
            if key < len(self.children):
                value.title = self.children[key].title
                self.children[key] = value
            else:
                raise KeyError(key)

    def __delitem__(self, key) -> None:
        if isinstance(key, str):
            indexes = get_matching_titles(key, self.children)
            if len(indexes):
                del self.children[indexes[0]]
                return None
        elif isinstance(key, int) and key < len(self.children):
            del self.children[key]
            return None
        raise KeyError(key)

    def _add_child_id(self, key):
        attr_name = clean_identifier(key)
        self._child_ids[attr_name] = key
        super().__setattr__(attr_name, self[key])

    def _ipython_key_completions_(self):  # pragma: no cover
        return [child.title for child in self.children if getattr(child, "title", None)]


class Page(Layout):
    """Page - top level element for defining a document.

    Args:
        *children (Layout, Any):  Child items to include within the element.
        title (str): Element title.
        org_name (str): Organisation name.

    """

    _tag_open = "<main class='container px-2'>"
    _tag_close = "</main>"

    @property
    def _parent_class(self):
        """ """
        return Page

    @property
    def _child_class(self):
        """ """
        return Section

    def _render_title(self) -> str:
        """ """
        return f"<h1 class='display-4 my-3'>{self.title}</h1>\n"

    def save_html(
        self,
        filepath: str = "./esparto-doc.html",
        return_html: bool = False,
        dependency_source="esparto.options",
    ) -> Optional[str]:
        """
        Save document as an HTML file.

        Args:
          filepath (str): Destination filepath.
          return_html (bool): If True, return HTML as a string.
          dependency_source (str): One of 'cdn', 'inline', or 'esparto.options'.

        Returns:
          Document rendered as HTML. (If `return_html` is True)

        """
        html = publish_html(
            self,
            filepath=filepath,
            return_html=return_html,
            dependency_source=dependency_source,
        )

        if return_html:
            return html
        return None

    def save(
        self,
        filepath: str = "./esparto-doc.html",
        return_html: bool = False,
        dependency_source="esparto.options",
    ) -> Optional[str]:
        """
        Save document as an HTML file.

        Note: Alias for `self.save_html()`.

        Args:
          filepath (str): Destination filepath.
          return_html (bool): If True, return HTML as a string.
          dependency_source (str): One of 'cdn', 'inline', or 'esparto.options'.

        Returns:
          Document rendered as HTML. (If `return_html` is True)

        """
        html = self.save_html(
            filepath=filepath,
            return_html=return_html,
            dependency_source=dependency_source,
        )

        if return_html:
            return html
        return None

    def save_pdf(
        self, filepath: str = "./esparto-doc.pdf", return_html: bool = False
    ) -> Optional[str]:
        """
        Save document as a PDF file.

        Note: Requires optional module `weasyprint`.

        Args:
          filepath (str): Destination filepath.
          return_html (bool): If True, return intermediate HTML representation as a string.

        Returns:
          Document rendered as HTML. (If `return_html` is True)

        """
        html = publish_pdf(self, filepath, return_html=return_html)

        if return_html:
            return html
        return None

    def __init__(
        self,
        *children: Union["Layout", "Content", Any],
        title: Optional[str] = None,
        org_name: Optional[str] = "esparto",
    ):
        super().__init__(*children, title=title)
        self.org_name = org_name


class Section(Layout):
    """Section - defines a Section within a Page.

    Args:
        *children (Layout, Any):  Child items to include within the element.
        title (str): Element title.

    """

    _tag_open = "<div class='px-1 mb-5'>"
    _tag_close = "</div>"
    _parent_class = Page

    @property
    def _child_class(self):
        """ """
        return Row

    def _render_title(self) -> str:
        """ """
        return f"<h3 class='mb-3'>{self.title}</h3>\n"


class Row(Layout):
    """Row -  defines a Row within a Section.

    Args:
        *children (Layout, Any):  Child items to include within the element.
        title (str): Element title.

    """

    _tag_open = "<div class='row'>"
    _tag_close = "</div>"
    _parent_class = Section

    @property
    def _child_class(self):
        """ """
        return Column

    def _render_title(self) -> str:
        """ """
        return f"<div class='col-12'><h5 class='px-1 mb-3'>{self.title}</h5></div>\n"


class Column(Layout):
    """Column -  defines a Column within a Row.

    Args:
        *children (Layout, Any):  Child items to include within the element.
        title (str): Element title.

    """

    _tag_open = "<div class='col-lg mb-3'>"
    _tag_close = "</div>"
    _parent_class = Row

    @property
    def _child_class(self):
        """ """
        raise NotImplementedError

    def _render_title(self) -> str:
        """ """
        return f"<h5 class='px-1 mb-3'>{self.title}</h5>\n"
