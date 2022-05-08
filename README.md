<div align="center">

<br><img src="logo/esparto-logo.png/"><br>

[![PyPI pyversions](https://img.shields.io/pypi/pyversions/esparto.svg)](https://pypi.python.org/pypi/esparto/)
[![image](https://img.shields.io/pypi/v/esparto.svg)](https://pypi.python.org/pypi/esparto)
[![Anaconda-Server Badge](https://anaconda.org/conda-forge/esparto/badges/version.svg)](https://anaconda.org/conda-forge/esparto)
![Build Status](https://github.com/domvwt/esparto/actions/workflows/lint-and-test.yml/badge.svg)
[![codecov](https://codecov.io/gh/domvwt/esparto/branch/main/graph/badge.svg?token=35J8NZCUYC)](https://codecov.io/gh/domvwt/esparto)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=domvwt_esparto&metric=alert_status)](https://sonarcloud.io/dashboard?id=domvwt_esparto)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Anaconda-Server Badge](https://anaconda.org/conda-forge/esparto/badges/license.svg)](https://anaconda.org/conda-forge/esparto)
![PyPI - Downloads](https://img.shields.io/pypi/dm/esparto)

</div>

**esparto** is a Python library for building data driven reports with content
from popular analytics packages.

Basic Usage
-----------

```python
import esparto as es

# Do some analysis
pandas_dataframe = ...
plot_figure = ...
markdown_str = ...

# Create a Page object
page = es.Page(title="My Report")

# Add content
page["Data Analysis"]["Plot"] = plot_figure
page["Data Analysis"]["Data"] = pandas_dataframe
page["Data Analysis"]["Commentary"] = markdown_str

# Save to HTML or PDF
page.save_html("my-report.html")
page.save_pdf("my-report.pdf")

```

Main Features
-------------

- Interactive document design with Jupyter Notebooks
- Share as self-contained webpage or PDF
- Customise with CSS and Jinja
- Responsive [Bootstrap][Bootstrap] grid layout
- Content adaptors for:
    - [Markdown][Markdown]
    - [Pandas DataFrames][Pandas]
    - [Matplotlib][Matplotlib]
    - [Bokeh][Bokeh]
    - [Plotly][Plotly]

Installation
------------

**esparto** is available from [PyPI][PyPI] and [Conda][Conda]:

```bash
pip install esparto
```

```bash
conda install esparto -c conda-forge
```

Dependencies
------------

- [python](https://python.org/) >= 3.6
- [jinja2](https://palletsprojects.com/p/jinja/)
- [markdown](https://python-markdown.github.io/)
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)
- [PyYAML](https://pyyaml.org/)

#### Optional

- [weasyprint](https://weasyprint.org/) *(for PDF output)*

License
-------

[MIT](https://opensource.org/licenses/MIT)

Documentation
-------------

Documentation and examples are available at
[domvwt.github.io/esparto/](https://domvwt.github.io/esparto/).

Contributions, Issues, and Requests
-----------------------------------

Feedback and contributions are welcome - please raise an issue or pull request
on [GitHub][GitHub].

Examples
--------

Iris Report - [Webpage](https://domvwt.github.io/esparto/examples/iris-report.html) |
[PDF](https://domvwt.github.io/esparto/examples/iris-report.pdf) | [Notebook](https://github.com/domvwt/esparto/blob/main/docs/examples/iris-report.ipynb)

<br>

<p width=100%>
<img width=100%  src="https://github.com/domvwt/esparto/blob/1857f1d7411f12c37c96f8f5d60ff7012071851f/docs/images/iris-report-compressed.png?raw=true" alt="example page" style="border-radius:0.5%;">
</p>

<!-- * Links -->
[PyPI]: https://pypi.org/project/esparto/
[Conda]: https://anaconda.org/conda-forge/esparto
[Bootstrap]: https://getbootstrap.com/
[Jinja]: https://jinja.palletsprojects.com/
[Markdown]: https://www.markdownguide.org/
[Pandas]: https://pandas.pydata.org/
[Matplotlib]: https://matplotlib.org/
[Bokeh]: https://bokeh.org/
[Plotly]: https://plotly.com/
[GitHub]: https://github.com/domvwt/esparto
