from inspect import getmembers, isfunction, signature

import pytest

import esparto._adaptors as ad
from esparto._content import Content
from tests.conftest import _EXTRAS, adaptor_list


def get_dispatch_type(fn):
    sig = signature(fn)
    if "content" in sig.parameters:
        return sig.parameters["content"].annotation


def test_all_adaptors_covered(adaptor_list_fn):
    test_classes = {type(item[0]) for item in adaptor_list_fn}
    module_functions = [x[1] for x in getmembers(ad, isfunction)]
    adaptor_types = {get_dispatch_type(fn) for fn in module_functions}
    adaptor_types.remove(Content)  # Can't use abstract base class in a test
    if _EXTRAS:
        adaptor_types.remove(ad.BokehObject)  # Can't use abstract base class in a test
    adaptor_types.remove(None)
    missing = adaptor_types.difference(test_classes)
    assert not missing, missing


@pytest.mark.parametrize("input_,expected", adaptor_list)
def test_adaptor_text(input_, expected):
    output = ad.content_adaptor(input_)
    assert isinstance(output, expected)


def test_incorrect_content_rejected():
    class FakeClass:
        def __call__(self):
            return "I'm not supported"

    fake = FakeClass()

    with pytest.raises(TypeError):
        ad.content_adaptor(fake)
