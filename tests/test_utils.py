import esparto._utils as utils


def test_render_html():
    tag = "div"
    classes = ["row", "row-es"]
    styles = {"color": "red", "border": "blue"}
    children = "some text"
    identifier = "row-one"
    expected = "<div id='row-one' class='row row-es' style='color: red; border: blue'>\n  some text\n</div>"
    output = utils.render_html(tag, classes, styles, children, identifier)
    print(output)
    assert output == expected
