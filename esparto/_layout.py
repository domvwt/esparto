"""Layout classes for defining and interacting with a document."""

import copy
from abc import ABC
from pprint import pformat
from typing import TYPE_CHECKING, Any, Dict, Iterable, List, Optional, Set, Type, Union

from esparto._publish import nb_display, publish_html, publish_pdf
from esparto._utils import clean_attr_name, clean_iterator, get_matching_titles

if TYPE_CHECKING:
    from esparto._content import Content


class Layout(ABC):
    """Template for Layout elements. All Layout classes come with these methods and attributes.

    Layout class hierarchy:
        `Page -> Section -> Row -> Column -> Content`

    Attributes:
      title (str): Object title. Used as a title within the document and as a key value.
      children (list): Child items defining the document layout and content.

    """

    # ------------------------------------------------------------------------+
    #                              Magic Methods                              |
    # ------------------------------------------------------------------------+

    def __init__(
        self,
        title: Optional[str] = None,
        children: Union[
            List[Union["Layout", "Content", Any]], "Layout", "Content"
        ] = list(),
    ):
        self.set_children(children)
        self.title = title

    def __iter__(self):
        return iter([self])

    def __repr__(self):
        return self._tree()

    def _repr_html_(self):
        self.display()

    def __str__(self):
        return self._tree()

    def __add__(self, other: Union["Layout", "Content", Any]):

        if isinstance(other, type(self)):
            return self._parent_class(
                title=self.title, children=[*(*self.children, *other.children)]
            )

        new = copy.copy(self)
        new.children = self.children + [*self._smart_wrap(other)]

        return new

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (
                self.title == other.title
                and len(self.children) == len(other.children)
                and all((x == y for x, y in zip(self.children, other.children)))
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

    def __delattr__(self, key: str) -> None:
        child_id = super().__getattribute__("_child_ids").get(key)
        if child_id:
            self.__delitem__(child_id)
        else:
            super().__delattr__(key)

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
        value = copy.copy(value)
        value = self._smart_wrap(value)
        value = value[0]
        if isinstance(key, str):
            if key:
                value.title = key
                indexes = get_matching_titles(key, self.children)
                if indexes:
                    self.children[indexes[0]] = value
                else:
                    self.children.append(value)
                self._add_child_id(key)
            else:
                self.children.append(value)
            return None
        elif isinstance(key, int) and key < len(self.children):
            value.title = getattr(self.children[key], "title", None)
            self.children[key] = value
            return None
        raise KeyError(key)

    def __delitem__(self, key) -> None:
        if isinstance(key, str):
            indexes = get_matching_titles(key, self.children)
            if len(indexes):
                self._remove_child_id(key)
                del self.children[indexes[0]]
                return None
        elif isinstance(key, int) and key < len(self.children):
            child_title = getattr(self.children[key], "title", None)
            self._remove_child_id(child_title)
            del self.children[key]
            return None
        raise KeyError(key)

    def __lshift__(self, other: Union["Layout", "Content", Any]):
        self.set_children(other)
        return other

    def __rshift__(self, other: Union["Layout", "Content", Any]):
        self.set_children(other)
        return self

    title: Optional[str]
    children: List[Any] = []
    _parent_class: Type["Layout"]
    _child_class: Type["Layout"]
    _title_tags: str
    _body_tags: str
    _dependencies = {"bootstrap"}

    @property
    def _child_ids(self) -> Dict[str, str]:
        """Return existing child IDs or a new dict."""
        try:
            super().__getattribute__("__child_ids")
        except AttributeError:
            super().__setattr__("__child_ids", dict())
        return super().__getattribute__("__child_ids")

    # ------------------------------------------------------------------------+
    #                              Public Methods                             |
    # ------------------------------------------------------------------------+

    def display(self) -> None:
        """Display rendered document in a Notebook environment."""
        nb_display(self)

    def set_children(self, other: Union["Layout", "Content", Any]):
        """Set children as other."""
        other = copy.copy(other)
        self.children = [*self._smart_wrap(other)]

    def to_html(self, **kwargs) -> str:
        """Convert document to HTML code.

        Returns:
          str: HTML code.

        """
        children_rendered = " ".join([c.to_html(**kwargs) for c in self.children])
        title_rendered = self._title_tags.format(self.title) if self.title else ""

        html = self._body_tags.format(f"{title_rendered}\n{children_rendered}\n")
        return html

    def tree(self) -> None:
        """Display document tree."""
        print(self._tree())

    # ------------------------------------------------------------------------+
    #                             Private Methods                             |
    # ------------------------------------------------------------------------+

    def _add_child_id(self, key):
        attr_name = clean_attr_name(key)
        if attr_name:
            self._child_ids[attr_name] = key
            super().__setattr__(attr_name, self[key])

    def _remove_child_id(self, key):
        attr_name = clean_attr_name(key)
        if attr_name in self._child_ids:
            del self._child_ids[attr_name]
            super().__delattr__(attr_name)

    def _smart_wrap(
        self, child_list: Iterable[Any]
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

        child_list = clean_iterator(child_list)

        if isinstance(self, Column):
            return [content_adaptor(x) for x in child_list]

        is_row = isinstance(self, Row)
        unwrapped_acc: list = []
        output = []

        for child in child_list:
            is_wrapped = isinstance(child, self._child_class)

            if is_wrapped:
                if unwrapped_acc:
                    wrapped_segment = self._child_class(children=unwrapped_acc)
                    output.append(wrapped_segment)
                    output.append(child)
                    unwrapped_acc = []
                else:
                    output.append(child)
            else:  # if not is_wrapped
                if is_row:
                    output.append(self._child_class(children=[child]))
                else:
                    unwrapped_acc.append(child)

        if unwrapped_acc:
            wrapped_segment = self._child_class(children=unwrapped_acc)
            output.append(wrapped_segment)

        return output

    def _recurse_children(self, idx) -> dict:
        key = self.title or f"{type(self).__name__} {idx}"
        tree = {
            f"{key}": [
                child._recurse_children(idx)  # type: ignore
                if hasattr(child, "_recurse_children")
                else str(child)
                for idx, child in enumerate(self.children)
            ]
        }
        return tree

    def _required_dependencies(self) -> Set[str]:
        deps: Set[str] = self._dependencies

        def dep_finder(item):
            nonlocal deps
            for child in item.children:
                deps = deps | set(getattr(child, "_dependencies", None))
                if hasattr(child, "children"):
                    dep_finder(child)

        dep_finder(self)
        return deps

    def _tree(self) -> str:
        return pformat(self._recurse_children(idx=0))

    def _ipython_key_completions_(self):  # pragma: no cover
        return [
            getattr(child, "title")
            for child in self.children
            if hasattr(child, "title")
        ]


class Page(Layout):
    """Defines the top level of a document.

    Args:
        title (str): Used as a title within the document and as a key value.
        navbrand (str): Brand name. Displayed in the page navbar if provided.
        children (list): Child items defining layout and content.

    """

    def __init__(
        self,
        title: Optional[str] = None,
        navbrand: Optional[str] = "",
        children: Union[
            List[Union["Layout", "Content", Any]], "Layout", "Content"
        ] = list(),
    ):
        super().__init__(title, children)
        self.org_name = navbrand

    def save(
        self,
        filepath: str = "./esparto-doc.html",
        return_html: bool = False,
        dependency_source="esparto.options",
    ) -> Optional[str]:
        """
        Save document to HTML file.

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

    def save_html(
        self,
        filepath: str = "./esparto-doc.html",
        return_html: bool = False,
        dependency_source="esparto.options",
    ) -> Optional[str]:
        """
        Save document to HTML file.

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

    def save_pdf(
        self, filepath: str = "./esparto-doc.pdf", return_html: bool = False
    ) -> Optional[str]:
        """
        Save document to PDF file.

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

    _title_tags = "<h1 class='display-4 my-3'>{}</h1>"
    _body_tags = "<main class='container px-2'>{}</main>"

    @property
    def _parent_class(self):
        return Page

    @property
    def _child_class(self):
        return Section


class Section(Layout):
    """Sections define thematically distinct groups of content within a Page.

    Args:
        title (str): Used as a title within the document and as a key value.
        children (list): Child items defining layout and content.

    """

    _title_tags = "<h3 class='mb-3'>{}</h3>"
    _body_tags = "<div class='px-1 mb-5'>{}</div>"
    _parent_class = Page

    @property
    def _child_class(self):
        return Row


class Row(Layout):
    """Rows are used in combination with Columns to define the grid layout within a section.

    Args:
        title (str): Used as a title within the document and as a key value.
        children (list): Child items defining layout and content.

    """

    _title_tags = "<div class='col-12'><h5 class='px-1 mb-3'>{}</h5></div>"
    _body_tags = "<div class='row'>{}</div>"
    _parent_class = Section

    @property
    def _child_class(self):
        return Column


class Column(Layout):
    """Columns sit within Rows and act as content holders.

    Args:
        title (str): Used as a title within the document and as a key value.
        children (list): Child items defining layout and content.

    """

    _title_tags = "<h5 class='px-1 mb-3'>{}</h5>"
    _body_tags = "<div class='col-lg mb-3'>{}</div>"
    _parent_class = Row

    @property
    def _child_class(self):
        raise NotImplementedError
