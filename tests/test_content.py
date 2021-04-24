from itertools import chain

import pytest

import esparto._content as co
import esparto._layout as la
from tests.conftest import _EXTRAS, content_list

if _EXTRAS:

    def test_all_content_classes_covered(content_list_fn):
        test_classes = {type(c) for c in content_list_fn}
        module_classes = {c for c in co.Content.__subclasses__()}
        module_subclasses = [d.__subclasses__() for d in module_classes]
        module_all = set(chain.from_iterable(module_subclasses)) | module_classes
        assert module_all <= test_classes

    def test_all_content_classes_have_deps(content_list_fn):
        deps = [c._dependencies for c in content_list_fn]
        assert all(deps)


@pytest.mark.parametrize("a", content_list)
@pytest.mark.parametrize("b", content_list)
def test_content_add(a, b):
    output = a + b
    expected = la.Row(a, b)
    assert output == expected


def test_content_equality(content_list_fn):
    for i, a in enumerate(content_list_fn):
        for j, b in enumerate(content_list_fn):
            if i == j:
                assert a == b
            else:
                assert a != b


@pytest.mark.parametrize("scale", [0.2, 0.5, 1])
def test_image_resize(scale, image_content):
    content = image_content
    html_input = content.to_html()
    height = int(html_input.split("height")[1].split("'")[1][:-2])
    width = int(html_input.split("width")[1].split("'")[1][:-2])

    resized = content.rescale(scale)
    html_resized = resized.to_html()
    height_new = int(html_resized.split("height")[1].split("'")[1][:-2])
    width_new = int(html_resized.split("width")[1].split("'")[1][:-2])

    assert height_new == int(scale * height)
    assert width_new == int(scale * width)


@pytest.mark.parametrize("a", content_list)
def test_incorrect_content_rejected(a):

    b = type(a)

    class FakeClass:
        def __init__(self):
            self.supported = False

    fake = FakeClass()

    with pytest.raises(TypeError):
        b(fake)
