import copy

import pytest

import esparto._options as opt


def test_options_context():
    default_options = copy.deepcopy(opt.options)
    updated_options = opt.PageOptions(
        dependency_source="XXX",
        matplotlib=opt.MatplotlibOptions(
            html_output_format="svg", notebook_format="XXX", pdf_figsize=0.7
        ),
    )
    new_options = opt.PageOptions(
        dependency_source="XXX", matplotlib=opt.MatplotlibOptions(notebook_format="XXX")
    )
    with opt.OptionsContext(new_options):
        context_options = copy.deepcopy(opt.options)

    assert opt.options == default_options
    assert context_options == updated_options


update_recursive_cases = [
    ({"a": 1, "b": 2}, {"b": 3}, {"a": 1, "b": 3}),
    (
        {"a": 1, "b": 2, "c": {"d": 4, "e": 5}},
        {"b": 3, "c": {"e": 6}},
        {"a": 1, "b": 3, "c": {"d": 4, "e": 6}},
    ),
]


@pytest.mark.parametrize("input1,input2,expected", update_recursive_cases)
def test_update_recursive(input1, input2, expected):
    assert opt.update_recursive(input1, input2) == expected
