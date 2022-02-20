import copy

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
