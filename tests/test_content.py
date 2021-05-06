from itertools import chain

import pytest
from PIL import Image  # type: ignore

import esparto._content as co
import esparto._layout as la
from tests.conftest import _EXTRAS, content_list

if _EXTRAS:

    def test_all_content_classes_covered(content_list_fn):
        test_classes = {type(c) for c in content_list_fn}
        module_classes = {c for c in co.Content.__subclasses__()}
        module_subclasses = [d.__subclasses__() for d in module_classes]
        module_all = set(chain.from_iterable(module_subclasses)) | module_classes
        missing = module_all.difference(test_classes)
        assert not missing, missing

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
def test_image_rescale(scale, image_content):
    img = Image.open(image_content.content)
    width, height = img.size

    resized = co._rescale_image(img, scale=scale)
    width_new, height_new = resized.size

    assert height_new == int(scale * height)
    assert width_new == int(scale * width)


@pytest.mark.parametrize("target", [100, 400, 550])
def test_image_scale_width(target, image_content):
    img = Image.open(image_content.content)
    width, height = img.size

    scale = target / width

    if target > width:
        with pytest.raises(ValueError):
            resized = co._rescale_image(img, width=target)
    else:
        resized = co._rescale_image(img, width=target)
        width_new, height_new = resized.size
        assert height_new == int(scale * height)
        assert width_new == target


@pytest.mark.parametrize("target", [100, 400, 1000])
def test_image_scale_height(target, image_content):
    img = Image.open(image_content.content)
    width, height = img.size

    scale = target / height

    if target > height:
        with pytest.raises(ValueError):
            resized = co._rescale_image(img, height=target)
    else:
        resized = co._rescale_image(img, height=target)
        width_new, height_new = resized.size
        assert height_new == target
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
