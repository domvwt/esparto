esparto
=======

[![image](https://img.shields.io/pypi/v/esparto.svg)](https://pypi.python.org/pypi/esparto)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/esparto.svg)](https://pypi.python.org/pypi/esparto/)
[![Build Status](https://travis-ci.com/domvwt/esparto.svg?branch=main)](https://travis-ci.com/domvwt/esparto)
[![codecov](https://codecov.io/gh/domvwt/esparto/branch/main/graph/badge.svg?token=35J8NZCUYC)](https://codecov.io/gh/domvwt/esparto)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=domvwt_esparto&metric=alert_status)](https://sonarcloud.io/dashboard?id=domvwt_esparto)
![PyPI - Downloads](https://img.shields.io/pypi/dm/esparto)


## Introduction
**esparto** is a Python package for building shareable reports with content
from popular data analysis libraries.
With just a few lines of code, **esparto** turns DataFrames, plots, and
markdown into an interactive HTML document or PDF.

Documents produced by **esparto** are completely portable - no backend server
is required - and entirely customisable using CSS and Jinja templating.
All content dependencies are declared inline or loaded via a CDN, meaning your
reports can be shared by email, hosted on a standard http server, or made
available as static pages on cloud storage as-is.


## Basic Usage
```python
import esparto as es
page = es.Page(title="My Report")
page["Data Analysis"] = (pandas_dataframe, plotly_figure)
page.save_html("my-report.html")
```


## Main Features
* Simple API
* Jupyter Notebook compatible
* Output to HTML or PDF
* Customise with CSS or Jinja
* Built in adaptors for:
  * Markdown
  * Images
  * [Pandas DataFrames][Pandas]
  * [Matplotlib][Matplotlib]
  * [Bokeh][Bokeh]
  * [Plotly][Plotly]


## Installation
**esparto** is available from PyPI:
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
*   [PyYAML](https://pyyaml.org/)
*   [weasyprint](https://weasyprint.org/) _(optional - for PDF output)_


## License
[MIT](https://opensource.org/licenses/MIT)


## Documentation
Full documentation and examples are available at [domvwt.github.io/esparto/](https://domvwt.github.io/esparto/).


## Examples
Iris Report - [HTML](https://domvwt.github.io/esparto/examples/iris-report.html) |
[PDF](https://domvwt.github.io/esparto/examples/iris-report.pdf)

Bokeh and Plotly - [HTML](https://domvwt.github.io/esparto/examples/interactive-plots.html) |
[PDF](https://domvwt.github.io/esparto/examples/interactive-plots.pdf)

<br>

<img width=600  src="https://github.com/domvwt/esparto/blob/fdc0e787c0bc013d16667773e82e21c647b71d91/docs/images/iris-report-compressed.png?raw=true"
alt="example page" style="border-radius:0.5%;">

<!-- Links -->
[Bootstrap]: https://getbootstrap.com/docs/4.6/getting-started/introduction/
[Pandas]: https://pandas.pydata.org/
[Matplotlib]: https://matplotlib.org/
[Bokeh]: https://docs.bokeh.org/en/latest/index.html
[Plotly]: https://plotly.com/
