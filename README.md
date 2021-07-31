<h1 style="color: #036666; font-size: 5rem; font-style: italic;
 text-shadow: 2px 2px #248277"> esparto</h1>

[![image](https://img.shields.io/pypi/v/esparto.svg)](https://pypi.python.org/pypi/esparto)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/esparto.svg)](https://pypi.python.org/pypi/esparto/)
[![Build Status](https://travis-ci.com/domvwt/esparto.svg?branch=main)](https://travis-ci.com/domvwt/esparto)
[![codecov](https://codecov.io/gh/domvwt/esparto/branch/main/graph/badge.svg?token=35J8NZCUYC)](https://codecov.io/gh/domvwt/esparto)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=domvwt_esparto&metric=alert_status)](https://sonarcloud.io/dashboard?id=domvwt_esparto)
![PyPI - Downloads](https://img.shields.io/pypi/dm/esparto)


## Introduction
`esparto` is a Python library for building shareable
reports with markdown, images, and objects from popular data analysis libraries.

Reports produced by `esparto` support interactivity by incorporating
dependencies inline, or linking to a CDN as needed.
No backend server is required - files can be shared by email, served
on a webserver, or hosted as a static site on cloud storage as-is.

We rely on [Bootstrap 4][Bootstrap] for defining the page structure,
ensuring that pages are responsive and readable on any device.
A wide array of themes and extensions are available for Boostrap
courtesy of the open source community. It's easy to customise the look and feel of your reports by supplying a CSS file, Jinja template, or using the options available in the `esparto` API.


## Main Features
* Lightweight API
* Jupyter Notebook compatible
* Output to HTML or PDF
* Responsive Bootstrap layout
* Built in adaptors for:
  * Markdown
  * Images
  * [Pandas DataFrames][Pandas]
  * [Matplotlib][Matplotlib]
  * [Bokeh][Bokeh]
  * [Plotly][Plotly]


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
