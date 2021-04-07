import pytest

import esparto._adaptors as ad
from tests.conftest import adaptor_list


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
