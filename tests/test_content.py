from io import StringIO
from itertools import chain
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import pytest
from lxml import etree

import esparto._content as co
import esparto._layout as la

irises_jpg = str(Path("tests/resources/irises.jpg").absolute())


@pytest.fixture
def markdown_content():
    return co.Markdown("A")


@pytest.fixture
def image_content():
    return co.Image(irises_jpg)


# Add new content classes here
test_content_list = [
    (co.Markdown("A")),
    (co.Image(irises_jpg)),
    (co.Spacer()),
    (co.DataFramePd(pd.DataFrame({"a": range(1, 11), "b": range(11, 21)}))),
    (co.FigureMpl(plt.figure())),
]


@pytest.fixture
def test_content():
    return test_content_list


def test_all_content_classes_covered():
    test_classes = [type(c) for c in test_content_list]
    module_classes = [c for c in co.Content.__subclasses__()]
    module_subclasses = [d.__subclasses__() for d in module_classes]
    module_all = list(chain.from_iterable(module_subclasses)) + module_classes
    assert all([c in test_classes for c in module_all])


# Hack to allow use of pytest.fixture in parametrize decorator
@pytest.mark.parametrize("a", test_content_list)
@pytest.mark.parametrize("b", test_content_list)
def test_content_add(a, b):
    output = a + b
    expected = la.Row(a, b)
    assert output == expected


def test_content_eq():
    for i, a in enumerate(test_content_list):
        for j, b in enumerate(test_content_list):
            if i == j:
                assert a == b
            else:
                assert a != b


@pytest.mark.parametrize("content", test_content_list)
def test_content_html_valid(content):
    parser = etree.HTMLParser(recover=False)
    try:
        etree.parse(StringIO(content.to_html()), parser)
        output = True
    except Exception as e:
        print(e)
        output = False
    assert output
