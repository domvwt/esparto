#

<br>
<div align="center">
<a href="https://domvwt.github.io/esparto/"><img src="https://github.com/domvwt/esparto/blob/main/logo/logo.svg?raw=true"></a>
<br>
<br>

<a href="https://pypi.python.org/pypi/esparto/"><img src="https://img.shields.io/pypi/pyversions/esparto.svg"></img></a>
<img src="https://github.com/domvwt/esparto/actions/workflows/lint-and-test.yml/badge.svg"></img>
<a href="https://codecov.io/gh/domvwt/esparto"><img src="https://codecov.io/gh/domvwt/esparto/branch/main/graph/badge.svg?token=35J8NZCUYC"></img></a>
<a href="https://sonarcloud.io/dashboard?id=domvwt_esparto"><img src="https://sonarcloud.io/api/project_badges/measure?project=domvwt_esparto&metric=alert_status"></img></a>
</div>
<br>

**esparto** is a Python library for building data driven reports with content
from popular analytics packages.

- [Documentation][ProjectHome]
- [Source Code][GitHub]
- [Contributing](#contributions-issues-and-requests)
- [Bug Reports][Issues]

Main Features
-------------

- Create beautiful analytical reports using idiomatic Python
- Generate content from:
    - [Markdown][Markdown]
    - [Pandas DataFrames][Pandas]
    - [Matplotlib][Matplotlib]
    - [Bokeh][Bokeh]
    - [Plotly][Plotly]
- Develop interactively with [Jupyter Notebooks][Jupyter]
- Share documents as a self-contained webpage or PDF
- Customise with [CSS][CSS] and [Jinja][Jinja]
- Responsive [Bootstrap][Bootstrap] layout

Basic Usage
-----------

```python
import esparto as es

# Do some analysis
pandas_df = ...
plot_fig = ...
markdown_str = ...

# Create a page
page = es.Page(title="My Report")

# Add content
page["Data Analysis"]["Plot"] = plot_fig
page["Data Analysis"]["Data"] = pandas_df
page["Data Analysis"]["Notes"] = markdown_str

# Save to HTML or PDF
page.save_html("my-report.html")
page.save_pdf("my-report.pdf")

```

Installation
------------

**esparto** is available from [PyPI][PyPI] and [Conda][Conda]:

```bash
pip install esparto
```

```bash
conda install esparto -c conda-forge
```

```bash
poetry add esparto
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

User guides, documentation, and examples are available on the [project home page][ProjectHome].

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
[ProjectHome]: https://domvwt.github.io/esparto/
[PyPI]: https://pypi.org/project/esparto/
[Conda]: https://anaconda.org/conda-forge/esparto
[Bootstrap]: https://getbootstrap.com/
[Jinja]: https://jinja.palletsprojects.com/
[CSS]: https://developer.mozilla.org/en-US/docs/Web/CSS
[Markdown]: https://www.markdownguide.org/
[Pandas]: https://pandas.pydata.org/
[Matplotlib]: https://matplotlib.org/
[Bokeh]: https://bokeh.org/
[Plotly]: https://plotly.com/
[Jupyter]: https://jupyter.org/
[GitHub]: https://github.com/domvwt/esparto
[Issues]: https://github.com/domvwt/esparto/issues
