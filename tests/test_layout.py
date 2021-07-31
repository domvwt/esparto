from itertools import chain

import pytest

import esparto._content as co
import esparto._layout as la
from tests.conftest import _irises_path


def test_all_layout_classes_covered(layout_list_fn):
    test_classes = [type(c) for c in layout_list_fn]
    module_classes = [c for c in la.Layout.__subclasses__()]
    module_subclasses = [d.__subclasses__() for d in module_classes]
    module_all = set(list(chain.from_iterable(module_subclasses)) + module_classes)
    missing = module_all.difference(test_classes)
    assert not missing, missing


def test_layout_smart_wrapping(page_layout):
    strings = ["first", "second", "third"]
    output = page_layout + la.Section(
        children=[
            la.Row(children=[*strings, "fourth"]),
            "another bit of content",
            la.Row(children=[la.Column(children=["fifth"]), "sixth"]),
        ]
    )
    expected = page_layout
    expected += la.Section(
        children=[
            la.Row(children=[*[co.Markdown(x) for x in strings], "fourth"]),
            co.Markdown("another bit of content"),
            la.Row(
                children=[
                    la.Column(children=[co.Markdown("fifth")]),
                    la.Column(children=[co.Markdown("sixth")]),
                ]
            ),
        ]
    )
    print(output)
    print()
    print(expected)
    assert output == expected


def test_layout_call_many(page_layout, content_list_fn):
    a = la.Page(title="jazz", children=content_list_fn)
    assert a == page_layout


def test_layout_call_list(page_layout, content_list_fn):
    a = la.Page(title="jazz", children=content_list_fn)
    assert a == page_layout


def test_layout_equality(layout_list_fn):
    for i, a in enumerate(layout_list_fn):
        for j, b in enumerate(layout_list_fn):
            if i == j:
                assert a == b
            else:
                assert a != b


layout_add_list = [
    (
        la.Column(),
        "miles davis",
        la.Column(children=co.Markdown("miles davis")),
    ),
    (
        la.Row(),
        co.Markdown("ornette coleman"),
        la.Row(children=la.Column(children=co.Markdown("ornette coleman"))),
    ),
    (
        la.Page(children=["charles mingus"]),
        la.Section(children=["thelonious monk"]),
        la.Page(
            children=[
                la.Section(children=["charles mingus"]),
                la.Section(children=["thelonious monk"]),
            ]
        ),
    ),
    (
        la.Section(title="jazz"),
        la.Row(
            children=[
                la.Column(children=["john coltrane"]),
                la.Column(children=["wayne shorter"]),
            ]
        ),
        la.Section(
            title="jazz",
            children=[
                la.Row(
                    children=[
                        la.Column(children=["john coltrane"]),
                        la.Column(children=["wayne shorter"]),
                    ]
                )
            ],
        ),
    ),
    (
        la.Column(children=["eric dolphy"]),
        la.Column(children=["grant green"]),
        la.Row(
            children=[
                la.Column(children=["eric dolphy"]),
                la.Column(children=["grant green"]),
            ]
        ),
    ),
    (
        la.Page(title="piano"),
        "bill evans",
        la.Page(title="piano", children=[co.Markdown("bill evans")]),
    ),
    (
        la.Page(),
        _irises_path,
        la.Page(
            children=la.Section(
                children=la.Row(children=la.Column(children=co.Image(_irises_path)))
            )
        ),
    ),
]


@pytest.mark.parametrize("a,b,expected", layout_add_list)
def test_layout_add(a, b, expected):
    output = a + b
    assert output == expected


def test_get_item(page_basic_layout):
    page = la.Page(title="Test Page")
    page["Section One"]["Row One"] = "markdown content"
    assert page.section_one.row_one[0] == page_basic_layout[0][0][0]


def test_get_item_key_str_error(page_basic_layout):
    page = la.Page(title="Test Page")
    page["Section One"]["Row One"] = "markdown content"
    with pytest.raises(KeyError):
        page["Section One"][2]


def test_set_item_key_int_error(page_basic_layout):
    page = la.Page(title="Test Page")
    page["Section One"]["Row One"] = "markdown content"
    with pytest.raises(KeyError):
        page["Section One"][2] = "different content"


def test_set_item_new(page_basic_layout):
    page = la.Page(title="Test Page")
    page["Section One"]["Row One"] = "markdown content"
    assert page == page_basic_layout


def test_set_item_existing_str(page_basic_layout):
    page = la.Page(title="Test Page")
    page["Section One"]["Row One"] = "different content"
    page["Section One"]["Row One"] = "markdown content"
    assert page == page_basic_layout


def test_set_item_existing_int(page_basic_layout):
    page = la.Page(title="Test Page")
    page["Section One"]["Row One"] = "different content"
    page[0][0] = "markdown content"
    assert page == page_basic_layout


def test_set_item_existing_attr(page_basic_layout):
    page = la.Page(title="Test Page")
    page["Section One"]["Row One"] = "different content"
    page.section_one.row_one = "markdown content"
    assert page == page_basic_layout


def test_delitem_str(page_basic_layout):
    page = la.Page(title="Test Page")
    page["Section One"]["Row One"] = "markdown content"
    page["Section One"]["Row Two"] = "different content"
    del page["Section One"]["Row Two"]
    assert page == page_basic_layout


def test_delitem_int(page_basic_layout):
    page = la.Page(title="Test Page")
    page["Section One"]["Row One"] = "markdown content"
    page["Section One"]["Row Two"] = "different content"
    del page["Section One"][1]
    assert page == page_basic_layout


def test_delattr(page_basic_layout):
    page = la.Page(title="Test Page")
    page["Section One"]["Row One"] = "markdown content"
    page["Section One"]["Row Two"]["Markdown"] = "different content"
    del page.section_one.row_two
    assert page == page_basic_layout


def test_delitem_key_int_error():
    page = la.Page(title="Test Page")
    page["Section One"]["Row One"] = "markdown content"
    page["Section One"]["Row Two"] = "different content"
    with pytest.raises(KeyError):
        del page["Section One"][3]


def test_delitem_key_str_error():
    page = la.Page(title="Test Page")
    page["Section One"]["Row One"] = "markdown content"
    page["Section One"]["Row Two"] = "different content"
    with pytest.raises(KeyError):
        del page["Section One"]["Row Three"]


def test_child_id_maps_to_child():
    page = la.Page()
    page["Section One"]["Row One"] = "markdown content"
    assert page.section_one is page.children[0]


def test_lshift(page_basic_layout):
    page = la.Page(title="Test Page")
    content = "markdown content"
    passthrough = page["Section One"]["Row One"] << content
    assert passthrough == content
    assert page.children == page_basic_layout.children
    assert page == page_basic_layout


def test_rshift(page_basic_layout):
    page = la.Page(title="Test Page")
    content = "markdown content"
    passthrough = page["Section One"]["Row One"] >> content
    assert passthrough == page_basic_layout["Section One"]["Row One"]
    assert page == page_basic_layout


def test_table_of_contents():
    input_page = la.Page(title="My Page")
    input_page["Section One"]["Item A"] = "some text"
    input_page["Section One"]["Item B"] = "more text"
    input_page["Section Two"]["Item C"]["Item D"] = "and more text"
    input_page["Section Two"]["Item C"]["Item E"] = "even more text"

    output_toc = la.table_of_contents(input_page, numbered=False)
    expected_toc = co.Markdown(
        " * [Section One](#section_one-title)\n\t"
        " * [Item A](#item_a-title)\n\t"
        " * [Item B](#item_b-title)\n"
        " * [Section Two](#section_two-title)\n\t"
        " * [Item C](#item_c-title)\n\t\t"
        " * [Item D](#item_d-title)\n\t\t"
        " * [Item E](#item_e-title)"
    )
    assert output_toc == expected_toc


def test_table_of_contents_numbered():
    input_page = la.Page(title="My Page")
    input_page["Section One"]["Item A"] = "some text"
    input_page["Section One"]["Item B"] = "more text"
    input_page["Section Two"]["Item C"]["Item D"] = "and more text"
    input_page["Section Two"]["Item C"]["Item E"] = "even more text"

    output_toc = la.table_of_contents(input_page, numbered=True)
    expected_toc = co.Markdown(
        " 1. [Section One](#section_one-title)\n\t"
        " 1. [Item A](#item_a-title)\n\t"
        " 1. [Item B](#item_b-title)\n"
        " 1. [Section Two](#section_two-title)\n\t"
        " 1. [Item C](#item_c-title)\n\t\t"
        " 1. [Item D](#item_d-title)\n\t\t"
        " 1. [Item E](#item_e-title)"
    )
    assert output_toc == expected_toc


def test_cardgrid():
    page = la.Page()
    content = ["a" for _ in range(12)]
    page["Section One"] = la.CardGrid(children=content)
    assert False
