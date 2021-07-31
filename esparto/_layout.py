"""Layout classes define the structure and appearance of the document."""

import copy
from abc import ABC
from collections import namedtuple
from pprint import pformat
from typing import TYPE_CHECKING, Any, Dict, Iterable, List, Optional, Set, Type, Union

from esparto._publish import nb_display, publish_html, publish_pdf
from esparto._utils import (
    clean_attr_name,
    clean_iterator,
    get_matching_titles,
    render_html,
)

if TYPE_CHECKING:
    from esparto._content import Content, Markdown


class Layout(ABC):
    """Template for Layout elements. All Layout classes come with these methods and attributes.

    Layout class hierarchy:
        `Page -> Section -> Row -> Column -> Content`

    Attributes:
      title (str): Object title. Used as a title within the document and as a key value.
      children (list): Child items defining the document layout and content.
      title_classes (list): CSS classes to apply to title HTML.
      title_styles (dict): CSS styles to apply to title HTML.
      body_classes (list): CSS classes to apply to body HTML.
      body_styles (dict): CSS styles to apply to body HTML.

    """

    # ------------------------------------------------------------------------+
    #                              Magic Methods                              |
    # ------------------------------------------------------------------------+

    def __init__(
        self,
        title: Optional[str] = None,
        children: Union[
            List[Union["Layout", "Content", Any]], "Layout", "Content"
        ] = None,
        title_classes: List[str] = None,
        title_styles: Dict[str, Any] = None,
        body_classes: List[str] = None,
        body_styles: Dict[str, Any] = None,
    ):
        children = children or []
        self.set_children(children)
        self.title = title

        self.__post_init__()

        title_classes = title_classes or []
        title_styles = title_styles or {}
        body_classes = body_classes or []
        body_styles = body_styles or {}

        self.title_classes += title_classes
        self.title_styles.update(title_styles)

        self.body_classes += body_classes
        self.body_styles.update(body_styles)

    def __post_init__(self):
        raise NotImplementedError

    def __iter__(self):
        return iter([self])

    def __repr__(self):
        return self._tree()

    def _repr_html_(self):
        self.display()

    def __str__(self):
        return self._tree()

    def __add__(self, other: Union["Layout", "Content", Any]):

        if isinstance(other, (type(self), Spacer)):
            return self._parent_class(children=[self, other])

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
            if len(indexes) and key:
                return self.children[indexes[0]]
            value = self._child_class(title=key)
            self.children.append(value)
            if key:
                self._add_child_id(key)
            return self.children[-1]

        elif isinstance(key, int) and key < len(self.children):
            return self.children[key]

        raise KeyError(key)

    def __setitem__(self, key: Union[str, int], value: Any):
        value = copy.copy(value)
        if not isinstance(value, self._child_class):
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

    def __copy__(self):
        attributes = vars(self)
        new = self.__class__()
        new.__dict__.update(attributes)
        new.children = [*new.children]
        return new

    title: Optional[str]
    children: List[Any] = []

    title_html_tag: str
    title_classes: List[str]
    title_styles: Dict[str, Any]

    body_html_tag: str
    body_classes: List[str]
    body_styles: Dict[str, Any]

    @property
    def _default_id(self):
        return f"es-{type(self).__name__}".lower()

    _parent_class: Type["Layout"]
    _child_class: Type["Layout"]
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

    def get_identifier(self):
        return clean_attr_name(str(self.title)) if self.title else self._default_id

    def get_title_identifier(self):
        return f"{self.get_identifier()}-title"

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
        title_rendered = (
            render_html(
                self.title_html_tag,
                self.title_classes,
                self.title_styles,
                self.title,
                self.get_title_identifier(),
            )
            if self.title
            else ""
        )
        html = render_html(
            self.body_html_tag,
            self.body_classes,
            self.body_styles,
            f"{title_rendered}\n{children_rendered}\n",
            self.get_identifier(),
        )
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

        def dep_finder(parent):
            nonlocal deps
            for child in parent.children:
                deps = deps | set(getattr(child, "_dependencies", {}))
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
        table_of_contents (bool, int): Add a Table of Contents to the top of page/
            Int will be interpreted as maximum depth.
        children (list): Child items defining layout and content.
        title_classes (list): Additional CSS classes to apply to title HTML.
        title_styles (dict): Additional CSS styles to apply to title HTML.
        body_classes (list): Additional CSS classes to apply to body HTML.
        body_styles (dict): Additional CSS styles to apply to body HTML.

    """

    def __init__(
        self,
        title: Optional[str] = None,
        navbrand: Optional[str] = "",
        table_of_contents: Union[bool, int] = False,
        children: Union[
            List[Union["Layout", "Content", Any]], "Layout", "Content"
        ] = None,
        title_classes: List[str] = None,
        title_styles: Dict[str, Any] = None,
        body_classes: List[str] = None,
        body_styles: Dict[str, Any] = None,
    ):
        super().__init__(
            title, children, title_classes, title_styles, body_classes, body_styles
        )
        self.navbrand = navbrand
        self.table_of_contents = table_of_contents

    def save(
        self,
        filepath: str = "./esparto-doc.html",
        return_html: bool = False,
        dependency_source: str = None,
    ) -> Optional[str]:
        """
        Save document to HTML file.

        Note: Alias for `self.save_html()`.

        Args:
          filepath (str): Destination filepath.
          return_html (bool): If True, return HTML as a string.
          dependency_source (str): 'cdn' or 'inline'.

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
        dependency_source: str = None,
    ) -> Optional[str]:
        """
        Save document to HTML file.

        Args:
          filepath (str): Destination filepath.
          return_html (bool): If True, return HTML as a string.
          dependency_source (str): 'cdn' or 'inline'.

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

    def to_html(self, **kwargs):
        if self.table_of_contents:
            # Create a copy of the page and dynamically generate the TOC.
            # Copy is required so that TOC is not added multiple times and
            # always reflects the current content.
            max_depth = (
                None if self.table_of_contents is True else self.table_of_contents
            )
            page_copy = copy.copy(self)
            toc = table_of_contents(page_copy, max_depth=max_depth)
            page_copy.children.insert(
                0,
                page_copy._child_class(
                    title="Contents", children=[toc], title_classes=["h4"]
                ),
            )
            page_copy.table_of_contents = False
            return page_copy.to_html(**kwargs)
        return super().to_html(**kwargs)

    def __post_init__(self) -> None:
        self.title_html_tag = "h1"
        self.title_classes = ["es-page-title", "display-4", "mb-4"]
        self.title_styles = dict()

        self.body_html_tag = "main"
        self.body_classes = ["es-page-body", "container", "px-2"]
        self.body_styles = dict()

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
        title_classes (list): Additional CSS classes to apply to title HTML.
        title_styles (dict): Additional CSS styles to apply to title HTML.
        body_classes (list): Additional CSS classes to apply to body HTML.
        body_styles (dict): Additional CSS styles to apply to body HTML.

    """

    def __post_init__(self) -> None:
        self.title_html_tag = "h3"
        self.title_classes = ["mb-3", "es-section-title"]
        self.title_styles = dict()

        self.body_html_tag = "div"
        self.body_classes = ["px-1", "mb-3", "es-section-body"]
        self.body_styles = {"align-items": "flex-start"}

    _parent_class = Page

    @property
    def _child_class(self):
        return Row


class Row(Layout):
    """Rows are used in combination with Columns to define the grid layout within a section.

    Args:
        title (str): Used as a title within the document and as a key value.
        children (list): Child items defining layout and content.
        title_classes (list): Additional CSS classes to apply to title HTML.
        title_styles (dict): Additional CSS styles to apply to title HTML.
        body_classes (list): Additional CSS classes to apply to body HTML.
        body_styles (dict): Additional CSS styles to apply to body HTML.

    """

    def __post_init__(self) -> None:
        self.title_html_tag = "div"
        self.title_classes = ["col-12", "mt-2", "mb-3", "px-3", "h5", "es-row-title"]
        self.title_styles = dict()

        self.body_html_tag = "div"
        self.body_classes = ["row", "px-1", "es-row-body"]
        self.body_styles = {"align-items": "flex-start"}

    _parent_class = Section

    @property
    def _child_class(self):
        return Column


class Column(Layout):
    """Columns sit within Rows and act as content holders.

    Args:
        title (str): Used as a title within the document and as a key value.
        children (list): Child items defining layout and content.
        title_classes (list): Additional CSS classes to apply to title HTML.
        title_styles (dict): Additional CSS styles to apply to title HTML.
        body_classes (list): Additional CSS classes to apply to body HTML.
        body_styles (dict): Additional CSS styles to apply to body HTML.

    """

    def __post_init__(self) -> None:
        self.title_html_tag = "h5"
        self.title_classes = ["mt-2", "mb-3", "px-1", "es-column-title"]
        self.title_styles = dict()

        self.body_html_tag = "div"
        self.body_classes = ["col-lg", "mx-2", "mb-3", "es-column-body"]
        self.body_styles = dict()

    _parent_class = Row

    @property
    def _child_class(self):
        raise NotImplementedError


class Card(Column):
    """A Card can be used in place of a Column for grouping related items.
    Child items will be vertically stacked by defualt. Horizontal distribution
    can be achieved by nesting content inside a Row.

    Args:
        title (str): Used as a title within the document and as a key value.
        children (list): Child items defining layout and content.
        title_classes (list): Additional CSS classes to apply to title HTML.
        title_styles (dict): Additional CSS styles to apply to title HTML.
        body_classes (list): Additional CSS classes to apply to body HTML.
        body_styles (dict): Additional CSS styles to apply to body HTML.

    """

    def __post_init__(self) -> None:
        self.title_html_tag = "h5"
        self.title_classes = ["card-title", "es-card-title"]
        self.title_styles = dict()

        self.body_html_tag = "div"
        self.body_classes = [
            "col-lg",
            "mx-2",
            "mb-3",
            "border",
            "rounded",
            "es-card-body",
        ]
        self.body_styles = {"padding": "1rem"}


class Spacer(Column):
    """Empty Column for making space within a Row."""


class PageBreak(Section):
    """Add a page break when printing or saving to PDF."""

    body_id = "es-page-break"

    def __post_init__(self) -> None:
        self.title_html_tag = ""
        self.title_classes = []
        self.title_styles = dict()

        self.body_html_tag = "div"
        self.body_classes = []
        self.body_styles = {"page-break-after": "always"}


class ColumnGrid(Section):
    def __init__(
        self,
        title: Optional[str] = None,
        n_cols: int = None,
        heights_equal=True,
        children: Union[List[Union["Layout", "Content", Any]]] = None,
        spacer: Any = Spacer(),
        title_classes: List[str] = None,
        title_styles: Dict[str, Any] = None,
        body_classes: List[str] = None,
        body_styles: Dict[str, Any] = None,
    ):
        self.n_cols = n_cols
        self.spacer = spacer
        self.heights_equal = heights_equal

        super().__init__(
            title=title,
            children=[],
            title_classes=title_classes,
            title_styles=title_styles,
            body_classes=body_classes,
            body_styles=body_styles,
        )

        children = children or []
        self.set_grid(children)

    def set_grid(self, other: List[Any]) -> None:
        if other:
            child_grid = grid_formation(
                content=other,
                n_cols=self.n_cols,
                row_type=self._child_class,
                spacer=self.spacer,
                heights_equal=self.heights_equal,
            )  # type: ignore
            self.children = child_grid


class CardRow(Row):
    @property
    def _child_class(self):
        return Card


class CardGrid(ColumnGrid):
    @property
    def _child_class(self):
        return CardRow


def table_of_contents(
    object: Layout, max_depth: int = None, numbered=True
) -> "Markdown":
    """Produce table of contents for a `Layout` object."""
    from esparto._content import Markdown

    max_depth = max_depth or 99

    def get_toc_items(parent):
        result_tup = namedtuple("TOCItem", "title, level, id")

        def find_ids(parent, level, acc):
            if hasattr(parent, "get_title_identifier") and parent.title:
                acc.append(
                    result_tup(parent.title, level, parent.get_title_identifier())
                )
                level += 1
            if hasattr(parent, "children"):
                for child in parent.children:
                    find_ids(child, level, acc)
            else:
                return acc
            return acc

        acc_new = find_ids(parent, 0, [])
        return acc_new

    toc_items = get_toc_items(object)

    tab = "\t"
    marker = "1." if numbered else "*"
    markdown_list = [
        f"{(item.level - 1) * tab} {marker} [{item.title}](#{item.id})"
        for item in toc_items
        if item.level > 0 and item.level <= max_depth
    ]
    markdown_str = "\n".join(markdown_list)

    return Markdown(markdown_str)


def grid_formation(
    content: List[Any],
    n_cols: int = None,
    row_type=Row,
    spacer=Spacer(),
    heights_equal=True,
) -> List[Any]:
    """Arrange `content` into grid formation."""
    n_cols = n_cols or 2
    row_styles = {"align-items": "stretch"} if heights_equal else {}
    content = [
        row_type(children=content[i : i + n_cols], body_styles=row_styles)
        for i in range(0, len(content), n_cols)
    ]
    n_spacers = n_cols - (len(content[-1].children) % n_cols)
    n_spacers = n_spacers if n_spacers < n_cols else 0
    content[-1].children += [spacer for _ in range(n_spacers)]

    return content
