from itertools import chain

import pytest

import esparto._content as co
import esparto._layout as la
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
