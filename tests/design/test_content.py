from itertools import chain

import pytest

import esparto.design.content as co
import esparto.design.layout as la
from tests.conftest import _EXTRAS, content_list


@pytest.mark.parametrize("a", content_list)
@pytest.mark.parametrize("b", content_list)
def test_content_add(a, b):
    output = a + b
    expected = la.Row(children=[a, b])
    assert output == expected


def test_content_equality(content_list_fn):
    for i, a in enumerate(content_list_fn):
        for j, b in enumerate(content_list_fn):
            if i == j:
                assert a == b
            else:
                assert a != b


if _EXTRAS:

    def test_all_content_classes_covered(content_list_fn):
        test_classes = {type(c) for c in content_list_fn}
        module_classes = {c for c in co.Content.__subclasses__()}
        module_subclasses = [d.__subclasses__() for d in module_classes]
        module_all = set(chain.from_iterable(module_subclasses)) | module_classes
        missing = module_all.difference(test_classes)
        assert not missing, missing

    def test_all_content_classes_have_deps(content_list_fn):
        # RawHTML has no dependencies
        deps = [
            c._dependencies for c in content_list_fn if not isinstance(c, co.RawHTML)
        ]
        assert all(deps)


@pytest.mark.parametrize("a", content_list)
def test_incorrect_content_rejected(a):

    b = type(a)

    class FakeClass:
        def __init__(self):
            self.supported = False

    fake = FakeClass()

    with pytest.raises(TypeError):
        b(fake)


def test_table_of_contents():
    input_page = la.Page(title="My Page")
    input_page["Section One"]["Item A"] = "some text"
    input_page["Section One"]["Item B"] = "more text"
    input_page["Section Two"]["Item C"]["Item D"] = "and more text"
    input_page["Section Two"]["Item C"]["Item E"] = "even more text"

    output_toc = co.table_of_contents(input_page, numbered=False)
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

    output_toc = co.table_of_contents(input_page, numbered=True)
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
