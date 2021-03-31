from itertools import chain

import pytest

import esparto._layout as la
import esparto._content as co
from tests.conftest import layout_list



def test_all_layout_classes_covered(layout_list_fn):
    test_classes = [type(c) for c in layout_list_fn]
    module_classes = [c for c in la.Layout.__subclasses__()]
    module_subclasses = [d.__subclasses__() for d in module_classes]
    module_all = list(chain.from_iterable(module_subclasses)) + module_classes
    assert all([c in test_classes for c in module_all])


def test_layout_smart_wrapping(page_layout):
    strings = ["first", "second", "third"]
    output = page_layout + la.Section(*strings, "fourth", la.Column("fifth"), "sixth")
    expected = page_layout()
    expected += la.Section(
        *[co.Markdown(x) for x in strings],
        la.Row("fourth", la.Column("fifth"), "sixth")
    )
    print(output)
    print()
    print(expected)
    assert output == expected


@pytest.mark.parametrize("a", layout_list)
def test_layout_call(a):
    b = a()
    assert a == b
    assert a is not b


def test_layout_call_many(page_layout, content_list_fn):
    a = la.Page(*content_list_fn, title="jazz")
    assert a == page_layout


def test_layout_call_list(page_layout, content_list_fn):
    a = la.Page(content_list_fn, title="jazz")
    assert a == page_layout


def test_layout_equality(layout_list_fn):
    for i, a in enumerate(layout_list_fn):
        for j, b in enumerate(layout_list_fn):
            if i == j:
                assert a == b
            else:
                assert a != b


layout_add_list = [
    (la.Column(), "miles davis", la.Column(co.Markdown("miles davis"))),
    (
        la.Row(),
        co.Markdown("ornette coleman"),
        la.Row(la.Column(co.Markdown("ornette coleman"))),
    ),
    (
        la.Page("charles mingus"),
        la.Section("thelonious monk"),
        la.Page(["charles mingus", "thelonious monk"]),
    ),
    (
        la.Section(title="jazz"),
        la.Row(la.Column("john coltrane"), la.Column("wayne shorter")),
        la.Section(
            la.Row(la.Column("john coltrane"), la.Column("wayne shorter")), title="jazz"
        ),
    ),
    (
        la.Column("eric dolphy"),
        la.Column("grant green"),
        la.Row(la.Column("eric dolphy"), la.Column("grant green")),
    ),
]


@pytest.mark.parametrize("a,b,expected", layout_add_list)
def test_layout_add(a, b, expected):
    output = a + b
    assert output == expected