esparto
=======

[![image](https://img.shields.io/pypi/v/esparto.svg)](https://pypi.python.org/pypi/esparto)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/esparto.svg)](https://pypi.python.org/pypi/esparto/)
[![Build Status](https://travis-ci.com/domvwt/esparto.svg?branch=main)](https://travis-ci.com/domvwt/esparto)
[![codecov](https://codecov.io/gh/domvwt/esparto/branch/main/graph/badge.svg?token=35J8NZCUYC)](https://codecov.io/gh/domvwt/esparto)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=domvwt_esparto&metric=alert_status)](https://sonarcloud.io/dashboard?id=domvwt_esparto)

## Introduction

`esparto` is a simple HTML and PDF document generator for Python. The API design emphasises
productivity and reliability over flexibility or complexity - although you should find that it serves many
use cases more than adequately. `esparto` is suitable for tasks such as:

* Designing simple web pages
* Automated MI reporting
* Collating and sharing data graphics
* ML model performance and evaluation documents


## Main Features
* Lightweight API
* Jupyter Notebook support
* Output self-contained HTML and PDF files
* Responsive layout from [Bootstrap](https://getbootstrap.com/)
* No CSS or HTML required
* Automatic conversion for:
    * Markdown
    * Images
    * Pandas DataFrames
    * Matplotlib
    * Bokeh
    * Plotly


## Installation
`esparto` is available from PyPI:
```bash
pip install esparto
```

If PDF output is required, `weasyprint` must also be installed:
```bash
pip install weasyprint
```


## Dependencies

*   [python](https://python.org/) >= 3.6
*   [jinja2](https://palletsprojects.com/p/jinja/)
*   [markdown](https://python-markdown.github.io/)
*   [Pillow](https://python-pillow.org/)
*   [weasyprint](https://weasyprint.org/) _(optional - for PDF output)_


## License
[MIT](https://opensource.org/licenses/MIT)


## Documentation
Full documentation and examples are available at [domvwt.github.io/esparto/](https://domvwt.github.io/esparto/).


## Basic Usage
```python
import esparto as es

# Instantiating a Page
page = es.Page(title="Research")

# Page layout hierarchy:
# Page -> Section -> Row -> Column -> Content

# Add or update content
# Keys are used as titles
page["Introduction"]["Part One"]["Item A"] = "lorem ipsum"
page["Introduction"]["Part One"]["Item B"] = "./pictures/image1.jpg"

# Add content without a title
page["Introduction"]["Part One"][""] = "Hello, Wolrd!"

# Replace child at index - useful if no title given
page["Introduction"]["Part One"][-1] = "Hello, World!"

# Set content and return input object
# Useful in Jupyter Notebook as it will be displayed in cell output
page["Methodology"]["Part One"]["Item A"] << "dolor sit amet"
# >>> "dolor sit amet"

# Set content and return new layout
page["Methodology"]["Part Two"]["Item B"] >> "foobar"
# >>> {'Item B': ['Markdown']}

# Show document structure
page.tree()
# >>> {'Research': [{'Introduction': [{'Part One': [{'Item A': ['Markdown']},
#                                                   {'Item B': ['Image']}]}]},
#                   {'Methodology': [{'Part One': [{'Item A': ['Markdown']}]},
#                                    {'Part Two': [{'Item A': ['Markdown']}]}]}]}

# Remove content
del page["Methodology"]["Part One"]["Item A"]
del page.methodology.part_two.item_b

# Access existing content as an attribute
page.introduction.part_one.item_a = "./pictures/image2.jpg"
page.introduction.part_one.tree()
# >>> {'Part One': [{'Item A': ['Image']},
#                   {'Item B': ['Image']},
#                   {'Column 2': ['Markdown']}]}

# Save the document
page.save_html("my-page.html")
page.save_pdf("my-page.pdf")
```


## Example Output

Iris Report - [HTML](https://domvwt.github.io/esparto/examples/iris-report.html) |
[PDF](https://domvwt.github.io/esparto/examples/iris-report.pdf)

Bokeh and Plotly - [HTML](https://domvwt.github.io/esparto/examples/interactive-plots.html) |
[PDF](https://domvwt.github.io/esparto/examples/interactive-plots.pdf)

<br>

<img width=600  src="https://github.com/domvwt/esparto/blob/fdc0e787c0bc013d16667773e82e21c647b71d91/docs/images/iris-report-compressed.png?raw=true"
alt="example page" style="border-radius:0.5%;">
