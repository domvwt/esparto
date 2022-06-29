"""Layout classes for defining page appearance and structure."""

import copy
import re
from abc import ABC
from pprint import pformat
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    Iterator,
    List,
    Optional,
    Set,
    Type,
    TypeVar,
    Union,
)

import bs4  # type: ignore

from esparto._options import OutputOptions, options, options_context
from esparto.design.base import AbstractLayout, Child
from esparto.publish.output import nb_display, publish_html, publish_pdf

T = TypeVar("T", bound="Layout")


class Layout(AbstractLayout, ABC):
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

    title: Optional[str]
    children: List[Child] = []

    title_html_tag: str
    title_classes: List[str]
    title_styles: Dict[str, Any]

    body_html_tag: str
    body_classes: List[str]
    body_styles: Dict[str, Any]

    @property
    def _default_id(self) -> str:
        return f"es-{type(self).__name__}".lower()

    @property
    def _parent_class(self) -> Type["Layout"]:
        raise NotImplementedError

    @property
    def _child_class(self) -> Type["Layout"]:
        raise NotImplementedError

    _dependencies = {"bootstrap"}

    @property
    def _child_ids(self) -> Dict[str, str]:
        """Return existing child IDs or a new dict."""
        try:
            super().__getattribute__("__child_ids")
        except AttributeError:
            super().__setattr__("__child_ids", {})
        child_ids: Dict[str, str] = super().__getattribute__("__child_ids")
        return child_ids

    def __init__(
        self,
        title: Optional[str] = None,
        children: Union[List[Child], Child] = None,
        title_classes: Optional[List[str]] = None,
        title_styles: Optional[Dict[str, Any]] = None,
        body_classes: Optional[List[str]] = None,
        body_styles: Optional[Dict[str, Any]] = None,
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

    def __post_init__(self) -> None:
        raise NotImplementedError

    def __iter__(self) -> Iterator["Layout"]:
        return iter([self])

    def __repr__(self) -> str:
        return self._tree()

    def _repr_html_(self) -> None:
        self.display()

    def __str__(self) -> str:
        return self._tree()

    def __add__(self: T, other: Child) -> T:
        new = copy.copy(self)
        new.children = self.children + [*self._smart_wrap(other)]
        return new

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, self.__class__):
            return (
                self.title == other.title
                and len(self.children) == len(other.children)
                and all((x == y for x, y in zip(self.children, other.children)))
            )
        return False

    def __ne__(self, other: Any) -> bool:
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

    def __getitem__(self, key: Union[str, int]) -> Any:
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

    def __setitem__(self, key: Union[str, int], value: Any) -> None:
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

    def __delitem__(self, key: Union[int, str]) -> None:
        if isinstance(key, str):
            indexes = get_matching_titles(key, self.children)
            if len(indexes):
                self._remove_child_id(key)
                del self.children[indexes[0]]
                return None
        elif isinstance(key, int) and key < len(self.children):
            child_title = getattr(self.children[key], "title", None)
            if child_title:
                self._remove_child_id(child_title)
            del self.children[key]
            return None
        raise KeyError(key)

    def __lshift__(self, other: Child) -> Child:
        self.set_children(other)
        return other

    def __rshift__(self, other: Child) -> "Layout":
        self.set_children(other)
        return self

    def __copy__(self) -> "Layout":
        attributes = vars(self)
        new = self.__class__()
        new.__dict__.update(attributes)
        new.children = [*new.children]
        return new

    # ------------------------------------------------------------------------+
    #                              Public Methods                             |
    # ------------------------------------------------------------------------+

    def display(self) -> None:
        """Render content in a Notebook environment."""
        nb_display(self)

    def get_identifier(self) -> str:
        """Get the HTML element ID for the current object."""
        return clean_attr_name(str(self.title)) if self.title else self._default_id

    def get_title_identifier(self) -> str:
        """Get the HTML element ID for the current object title."""
        return f"{self.get_identifier()}-title"

    def set_children(self, other: Union[List[Child], Child]) -> None:
        """Set children as `other`."""
        other = copy.copy(other)
        self.children = [*self._smart_wrap(other)]
        for child in self.children:
            title = getattr(child, "title", None)
            if title:
                self._add_child_id(title)

    def to_html(self, **kwargs: bool) -> str:
        """Render object as HTML string.

        Returns:
            html (str): HTML string.

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
        html = bs4.BeautifulSoup(html, "html.parser").prettify()
        return html

    def tree(self) -> None:
        """Display page tree."""
        print(self._tree())

    # ------------------------------------------------------------------------+
    #                             Private Methods                             |
    # ------------------------------------------------------------------------+

    def _add_child_id(self, key: str) -> None:
        attr_name = clean_attr_name(key)
        if attr_name:
            self._child_ids[attr_name] = key
            super().__setattr__(attr_name, self[key])

    def _remove_child_id(self, key: str) -> None:
        attr_name = clean_attr_name(key)
        if attr_name in self._child_ids:
            del self._child_ids[attr_name]
            super().__delattr__(attr_name)

    def _smart_wrap(self, child_list: Union[List[Child], Child]) -> List[Child]:
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
        return smart_wrap(self, child_list)

    def _recurse_children(self, idx: int) -> Dict[str, Any]:
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

        def dep_finder(parent: Any) -> None:
            nonlocal deps
            for child in parent.children:
                deps = deps | set(getattr(child, "_dependencies", {}))
                if hasattr(child, "children"):
                    dep_finder(child)

        dep_finder(self)
        return deps

    def _tree(self) -> str:
        return pformat(self._recurse_children(idx=0))

    def _ipython_key_completions_(self) -> List[str]:  # pragma: no cover
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
        max_width (int): Maximum page width expressed in pixels.
        output_options (es.OutputOptions): Page specific rendering and output options.
        children (list): Child items defining layout and content.
        title_classes (list): Additional CSS classes to apply to title.
        title_styles (dict): Additional CSS styles to apply to title.
        body_classes (list): Additional CSS classes to apply to body.
        body_styles (dict): Additional CSS styles to apply to body.

    """

    output_options: OutputOptions = options

    def __init__(
        self,
        title: Optional[str] = None,
        navbrand: Optional[str] = "",
        table_of_contents: Union[bool, int] = False,
        max_width: int = 800,
        output_options: Optional[OutputOptions] = None,
        children: Union[List[Child], Child] = None,
        title_classes: Optional[List[str]] = None,
        title_styles: Optional[Dict[str, Any]] = None,
        body_classes: Optional[List[str]] = None,
        body_styles: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            title, children, title_classes, title_styles, body_classes, body_styles
        )
        self.navbrand = navbrand
        self.table_of_contents = table_of_contents
        self.max_width = max_width
        self.output_options = output_options or options

    def save(
        self,
        filepath: str = "./esparto-doc.html",
        return_html: bool = False,
        dependency_source: Optional[str] = None,
    ) -> Optional[str]:
        """
        Save page to HTML file.

        Note:
            Alias for `self.save_html()`.

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

    @options_context(output_options)
    def save_html(
        self,
        filepath: str = "./esparto-doc.html",
        return_html: bool = False,
        dependency_source: Optional[str] = None,
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

    @options_context(output_options)
    def save_pdf(
        self, filepath: str = "./esparto-doc.pdf", return_html: bool = False
    ) -> Optional[str]:
        """
        Save page to PDF file.

        Note:
            Requires `weasyprint` library.

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

    @options_context(output_options)
    def to_html(self, **kwargs: bool) -> str:
        if self.table_of_contents:
            # Create a copy of the page and dynamically generate the TOC.
            # Copy is required so that TOC is not added multiple times and
            # always reflects the current content.
            from esparto.design.content import table_of_contents

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

        self.body_styles.update({"max-width": f"{self.max_width}px"})

        return super().to_html(**kwargs)

    def __post_init__(self) -> None:
        self.title_html_tag = "h1"
        self.title_classes = ["es-page-title"]
        self.title_styles = {}

        self.body_html_tag = "article"
        self.body_classes = ["es-page-body"]
        self.body_styles = {}

    @property
    def _parent_class(self) -> Type["Layout"]:
        return Page

    @property
    def _child_class(self) -> Type["Layout"]:
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
        self.title_classes = ["es-section-title"]
        self.title_styles = {}

        self.body_html_tag = "section"
        self.body_classes = ["es-section-body"]
        self.body_styles = {}

    @property
    def _parent_class(self) -> Type["Layout"]:
        return Page

    @property
    def _child_class(self) -> Type["Layout"]:
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
        children: Union[List[Child], Child, None] = None,
        cards_equal: bool = False,
        title_classes: Optional[List[str]] = None,
        title_styles: Optional[Dict[str, Any]] = None,
        body_classes: Optional[List[str]] = None,
        body_styles: Optional[Dict[str, Any]] = None,
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
    def _child_class(self) -> Type["Layout"]:
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
        self.title_html_tag = "h5"
        self.title_classes = ["col-12", "es-row-title"]
        self.title_styles = {}

        self.body_html_tag = "div"
        self.body_classes = ["row", "es-row-body"]
        self.body_styles = {}

    @property
    def _parent_class(self) -> Type["Layout"]:
        return Section

    @property
    def _child_class(self) -> Type["Layout"]:
        return Column

    def __setitem__(self, key: Union[str, int], value: Any) -> None:
        if isinstance(value, dict):
            title, content = list(value.items())[0]
            value = self._child_class(title=title, children=[content])
        super().__setitem__(key, value)


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
        children: Union[List[Child], Child] = None,
        col_width: Optional[int] = None,
        title_classes: Optional[List[str]] = None,
        title_styles: Optional[Dict[str, Any]] = None,
        body_classes: Optional[List[str]] = None,
        body_styles: Optional[Dict[str, Any]] = None,
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
        self.title_classes = ["es-column-title"]
        self.title_styles = {}

        col_class = f"col-lg-{self.col_width}" if self.col_width else "col-lg"
        self.body_html_tag = "div"
        self.body_classes = [col_class, "es-column-body"]
        self.body_styles = {}

    @property
    def _parent_class(self) -> Type["Layout"]:
        return Row

    @property
    def _child_class(self) -> Type["Layout"]:
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
    def _child_class(self) -> Type["Layout"]:
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
        children: Union[List[Child], Child] = None,
        col_width: int = 6,
        title_classes: Optional[List[str]] = None,
        title_styles: Optional[Dict[str, Any]] = None,
        body_classes: Optional[List[str]] = None,
        body_styles: Optional[Dict[str, Any]] = None,
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
        self.title_styles = {}

        self.body_html_tag = "div"

        col_class = f"col-lg-{self.col_width}" if self.col_width else "col-lg"
        self.body_classes = [col_class, "es-card"]
        self.body_styles = {}

    def to_html(self, **kwargs: bool) -> str:
        """Render content to HTML string.

        Returns:
            html (str): HTML string.

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
        card_body_classes = ["es-card-body"]
        card_body_styles: Dict[str, str] = {}
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
        self.title_styles = {}

        self.body_html_tag = "div"
        self.body_classes = []
        self.body_styles = {}


def smart_wrap(self: Layout, child_list: Union[List[Child], Child]) -> List[Child]:
    from esparto.design.adaptors import content_adaptor

    child_list = ensure_iterable(child_list)

    if isinstance(self, Column):
        if any((isinstance(x, dict) for x in child_list)):
            raise TypeError("Invalid content passed to Column: 'dict'")
        return [content_adaptor(x) for x in child_list]

    is_row = isinstance(self, Row)
    unwrapped_acc: List[Child] = []
    output: List[Child] = []

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


def render_html(
    tag: str,
    classes: List[str],
    styles: Dict[str, str],
    children: str,
    identifier: Optional[str] = None,
) -> str:
    """Render HTML from provided attributes."""
    class_str = " ".join(classes) if classes else ""
    class_str = f"class='{class_str}'" if classes else ""

    style_str = "; ".join((f"{key}: {value}" for key, value in styles.items()))
    style_str = f"style='{style_str}'" if styles else ""

    id_str = f"id='{identifier}'" if identifier else ""

    rendered = " ".join((f"<{tag} {id_str} {class_str} {style_str}>").split())
    rendered += f"\n  {children}\n</{tag}>"

    return rendered


def get_index_where(
    condition: Callable[..., bool], iterable: Iterable[Any]
) -> List[int]:
    """Return index values where `condition` is `True`."""
    return [idx for idx, item in enumerate(iterable) if condition(item)]


def get_matching_titles(title: str, children: List["Child"]) -> List[int]:
    """Return child items with matching title."""
    return get_index_where(lambda x: bool(getattr(x, "title", None) == title), children)


def clean_attr_name(attr_name: str) -> str:
    """Remove invalid characters from the attribute name."""
    if not attr_name:
        return ""

    # Remove leading and trailing spaces
    attr_name = attr_name.strip().replace(" ", "_").lower()

    # Remove invalid characters
    attr_name = re.sub("[^0-9a-zA-Z_]", "", attr_name)

    # Remove leading characters until we find a letter or underscore
    attr_name = re.sub("^[^a-zA-Z_]+", "", attr_name)

    return attr_name


def ensure_iterable(something: Any) -> Iterable[Any]:
    # Convert any non-list iterators to lists
    iterable = (
        list(something) if isinstance(something, (list, tuple, set)) else [something]
    )
    # Un-nest any nested lists of children
    if len(list(iterable)) == 1 and isinstance(list(iterable)[0], (list, tuple, set)):
        iterable = list(iterable)[0]
    return iterable
