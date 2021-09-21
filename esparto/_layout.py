"""Layout classes for defining page apperance and structure."""

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
        self.title = title
        children = children or []
        self.set_children(children)

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

        elif isinstance(key, int):
            if key < len(self.children):
                return self.children[key]
            value = self._child_class()
            self.children.append(value)
            return self.children[-1]

        raise KeyError(key)

    def __setitem__(self, key: Union[str, int], value: Any):
        value = copy.copy(value)
        title = (
            getattr(value, "title", None) if issubclass(type(value), Layout) else None
        )
        if not isinstance(value, self._child_class):
            if issubclass(self._child_class, Column):
                value = self._child_class(title=title, children=[value])
            else:
                value = self._smart_wrap(value)
                value = value[0]
        if isinstance(key, str):
            if key:
                value.title = title or key
                indexes = get_matching_titles(key, self.children)
                if indexes:
                    self.children[indexes[0]] = value
                else:
                    self.children.append(value)
                self._add_child_id(value.title)
            else:
                self.children.append(value)
            return
        elif isinstance(key, int):
            if key < len(self.children):
                value.title = title or getattr(self.children[key], "title", None)
                self.children[key] = value
                return
            self.children.append(value)
            return

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
        """Render content in a Notebook environment."""
        nb_display(self)

    def get_identifier(self):
        """Get the HTML element ID for the current object."""
        return clean_attr_name(str(self.title)) if self.title else self._default_id

    def get_title_identifier(self):
        """Get the HTML element ID for the current object title."""
        return f"{self.get_identifier()}-title"

    def set_children(self, other: Union["Layout", "Content", Any]):
        """Set children as `other`."""
        other = copy.copy(other)
        self.children = [*self._smart_wrap(other)]
        for child in self.children:
            title = getattr(child, "title", None)
            if title:
                self._add_child_id(title)

    def to_html(self, **kwargs) -> str:
        """Render object as HTML code.

        Returns:
            html (str): HTML code.

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
        """Display page tree."""
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
    ) -> Iterable[Union["Layout", "Content", dict]]:
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
        If the current child is a dict and the parent is a Row:
            - use the dictionary key as a title and value as content
            - wrap and append the current child to output
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
            if any([isinstance(x, dict) for x in child_list]):
                raise TypeError("Invalid content passed to Column: 'dict'")
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
                    if isinstance(child, dict):
                        title, child = list(child.items())[0]
                    else:
                        title = None
                    output.append(self._child_class(title=title, children=[child]))
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
    """Layout class that defines a Page.

    Args:
        title (str): Used as a title within the page and as a key value.
        navbrand (str): Brand name. Displayed in the page navbar if provided.
        table_of_contents (bool, int): Add a Table of Contents to the top of page.
            Passing an `int` will define the maximum depth.
        children (list): Child items defining layout and content.
        title_classes (list): Additional CSS classes to apply to title.
        title_styles (dict): Additional CSS styles to apply to title.
        body_classes (list): Additional CSS classes to apply to body.
        body_styles (dict): Additional CSS styles to apply to body.

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
        Save page to HTML file.

        Note: Alias for `self.save_html()`.

        Args:
            filepath (str): Destination filepath.
            return_html (bool): If True, return HTML as a string.
            dependency_source (str): 'cdn' or 'inline'.

        Returns:
            html (str): Document rendered as HTML. (If `return_html` is True)

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
        Save page to HTML file.

        Args:
            filepath (str): Destination filepath.
            return_html (bool): If True, return HTML as a string.
            dependency_source (str): 'cdn' or 'inline'.

        Returns:
            html (str): Document rendered as HTML. (If `return_html` is True)

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
        Save page to PDF file.

        Note: Requires optional module `weasyprint`.

        Args:
            filepath (str): Destination filepath.
            return_html (bool): If True, return intermediate HTML representation as a string.

        Returns:
            html (str): Document rendered as HTML. (If `return_html` is True)

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
    """Layout class that defines a Section.

    Args:
        title (str): Used as a title within the page and as a key value.
        children (list): Child items defining layout and content.
        title_classes (list): Additional CSS classes to apply to title.
        title_styles (dict): Additional CSS styles to apply to title.
        body_classes (list): Additional CSS classes to apply to body.
        body_styles (dict): Additional CSS styles to apply to body.

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


class CardSection(Section):
    """Layout class that defines a CardSection. CardSections wrap content in Cards by default.

    Args:
        title (str): Used as a title within the page and as a key value.
        children (list): Child items defining layout and content.
        cards_equal (bool): Cards in the same Row are stretched vertically if True.
        title_classes (list): Additional CSS classes to apply to title.
        title_styles (dict): Additional CSS styles to apply to title.
        body_classes (list): Additional CSS classes to apply to body.
        body_styles (dict): Additional CSS styles to apply to body.

    """

    def __init__(
        self,
        title: Optional[str] = None,
        children: Union[
            List[Union["Layout", "Content", Any]], "Layout", "Content"
        ] = None,
        cards_equal: bool = False,
        title_classes: List[str] = None,
        title_styles: Dict[str, Any] = None,
        body_classes: List[str] = None,
        body_styles: Dict[str, Any] = None,
    ):
        super().__init__(
            title=title,
            children=children,
            title_classes=title_classes,
            title_styles=title_styles,
            body_classes=body_classes,
            body_styles=body_styles,
        )

        self.cards_equal = cards_equal

    @property
    def _child_class(self):
        # Attribute missing if class is not instantiated
        if hasattr(self, "cards_equal") and self.cards_equal:
            return CardRowEqual
        return CardRow


class Row(Layout):
    """Layout class that defines a Row.

    Args:
        title (str): Used as a title within the page and as a key value.
        children (list): Child items defining layout and content.
        title_classes (list): Additional CSS classes to apply to title.
        title_styles (dict): Additional CSS styles to apply to title.
        body_classes (list): Additional CSS classes to apply to body.
        body_styles (dict): Additional CSS styles to apply to body.

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
    """Layout class that defines a Column.

    Args:
        title (str): Used as a title within the page and as a key value.
        children (list): Child items defining layout and content.
        col_width (int): Fix column width - must be between 1 and 12.
        title_classes (list): Additional CSS classes to apply to title.
        title_styles (dict): Additional CSS styles to apply to title.
        body_classes (list): Additional CSS classes to apply to body.
        body_styles (dict): Additional CSS styles to apply to body.

    """

    def __init__(
        self,
        title: Optional[str] = None,
        children: Union[
            List[Union["Layout", "Content", Any]], "Layout", "Content"
        ] = None,
        col_width: int = None,
        title_classes: List[str] = None,
        title_styles: Dict[str, Any] = None,
        body_classes: List[str] = None,
        body_styles: Dict[str, Any] = None,
    ):
        self.title = title
        children = children or []
        self.set_children(children)
        self.col_width = col_width

        self.__post_init__()

        title_classes = title_classes or []
        title_styles = title_styles or {}
        body_classes = body_classes or []
        body_styles = body_styles or {}

        self.title_classes += title_classes
        self.title_styles.update(title_styles)

        self.body_classes += body_classes
        self.body_styles.update(body_styles)

    def __post_init__(self) -> None:
        self.title_html_tag = "h5"
        self.title_classes = ["mt-2", "mb-3", "px-1", "es-column-title"]
        self.title_styles = dict()

        col_class = f"col-lg-{self.col_width}" if self.col_width else "col-lg"
        self.body_html_tag = "div"
        self.body_classes = [col_class, "mx-2", "mb-3", "es-column-body"]
        self.body_styles = dict()

    _parent_class = Row

    @property
    def _child_class(self):
        raise NotImplementedError


class CardRow(Row):
    """Layout class that defines a CardRow. CardRows wrap content in Cards by default.

    Args:
        title (str): Used as a title within the page and as a key value.
        children (list): Child items defining layout and content.
        title_classes (list): Additional CSS classes to apply to title.
        title_styles (dict): Additional CSS styles to apply to title.
        body_classes (list): Additional CSS classes to apply to body.
        body_styles (dict): Additional CSS styles to apply to body.

    """

    @property
    def _child_class(self):
        return Card


class CardRowEqual(CardRow):
    """Layout class that defines a CardRow with Cards of equal height.

    Args:
        title (str): Used as a title within the page and as a key value.
        children (list): Child items defining layout and content.
        title_classes (list): Additional CSS classes to apply to title.
        title_styles (dict): Additional CSS styles to apply to title.
        body_classes (list): Additional CSS classes to apply to body.
        body_styles (dict): Additional CSS styles to apply to body.

    """

    def __post_init__(self) -> None:
        super().__post_init__()
        self.body_styles = {"align-items": "stretch"}


class Card(Column):
    """Layout class that defines a Card.

    Child items will be vertically stacked by default.
    Horizontal arrangement is achieved by nesting content inside a Row.

    Args:
        title (str): Used as a title within the page and as a key value.
        children (list): Child items defining layout and content.
        col_width (int): Fix column width - must be between 1 and 12.
        title_classes (list): Additional CSS classes to apply to title.
        title_styles (dict): Additional CSS styles to apply to title.
        body_classes (list): Additional CSS classes to apply to body.
        body_styles (dict): Additional CSS styles to apply to body.

    """

    def __init__(
        self,
        title: Optional[str] = None,
        children: Union[
            List[Union["Layout", "Content", Any]], "Layout", "Content"
        ] = None,
        col_width: int = 6,
        title_classes: List[str] = None,
        title_styles: Dict[str, Any] = None,
        body_classes: List[str] = None,
        body_styles: Dict[str, Any] = None,
    ):
        super().__init__(
            title=title,
            children=children,
            col_width=col_width,
            title_classes=title_classes,
            title_styles=title_styles,
            body_classes=body_classes,
            body_styles=body_styles,
        )

    def __post_init__(self) -> None:
        self.title_html_tag = "h5"
        self.title_classes = ["card-title", "es-card-title"]
        self.title_styles = dict()

        self.body_html_tag = "div"

        col_class = f"col-lg-{self.col_width}" if self.col_width else "col-lg"
        self.body_classes = [
            col_class,
            "mb-3",
            "p-0",
            "es-card",
        ]
        self.body_styles = {}

    def to_html(self, **kwargs) -> str:
        """Render content to HTML code.

        Returns:
            html (str): HTML code.

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
        card_body_classes = ["mx-2", "border", "rounded", "card-body", "es-card-body"]
        card_body_styles = {"min-height": "100%"}
        html_body = render_html(
            "div",
            card_body_classes,
            card_body_styles,
            f"\n{title_rendered}\n{children_rendered}\n",
            f"{self.get_identifier()}-body",
        )
        html_full = render_html(
            self.body_html_tag,
            self.body_classes,
            self.body_styles,
            f"\n{html_body}\n",
            f"{self.get_identifier()}",
        )

        return html_full


class Spacer(Column):
    """Empty Column for making space within a Row."""


class PageBreak(Section):
    """Defines a page break when printing or saving to PDF."""

    body_id = "es-page-break"

    def __post_init__(self) -> None:
        self.title_html_tag = ""
        self.title_classes = []
        self.title_styles = dict()

        self.body_html_tag = "div"
        self.body_classes = []
        self.body_styles = {"page-break-after": "always"}


def table_of_contents(
    object: Layout, max_depth: int = None, numbered=True
) -> "Markdown":
    """Produce table of contents for a Layout object.

    Args:
        object (Layout): Target object for TOC.
        max_depth (int): Maximum depth of returned TOC.
        numbered (bool): If True TOC items are numbered.
            If False, bulletpoints are used.

    """
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
