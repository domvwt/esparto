from itertools import chain

import pytest

import esparto._content as co
import esparto._layout as la
from tests.conftest import content_list


def test_all_content_classes_covered(content_list_fn):
    test_classes = [type(c) for c in content_list_fn]
    module_classes = [c for c in co.Content.__subclasses__()]
    module_subclasses = [d.__subclasses__() for d in module_classes]
    module_all = list(chain.from_iterable(module_subclasses)) + module_classes
    assert all([c in test_classes for c in module_all])


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
    height, width = [
        int(content.to_html().replace("px", "").split("'")[x]) for x in [1, 3]
    ]
    resized = content.resize(scale)
    height_new, width_new = [
        int(resized.to_html().replace("px", "").split("'")[x]) for x in [1, 3]
    ]
    assert height_new == int(scale * height)
    assert width_new == int(scale * width)
