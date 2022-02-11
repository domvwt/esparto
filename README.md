esparto
=======

- [ ] TODO: Create develop branch
- [ ] TODO: Move CSS styles to esparto.css
- [ ] TODO: Retire bootstrap CSS apart from grid layout - cleaner table style
- [ ] TODO: Minify esparto html - no, this is non-trivial
- [ ] TODO: Update README documentation to explain project
- [ ] TODO: Do NOT remove optional css styles from layout elements
- [ ] TODO: Custom page icon emoji
- [ ] TODO: Replace iris report example image in README
- [ ] TODO: Update examples in docs
- [ ] TODO: Update docs
- [ ] TODO: Refactor options - pass to page object
- [ ] TODO: Allow linked stylesheets via 'url' option

<!--
<http://codesqueeze.com/the-7-software-ilities-you-need-to-know/>

This project prioritises:

* usability
  * producing attractive reports by default
  * abstracting away most layout and formatting decisions
  * object oriented Python API
  * intentionally limited configuration
* portability
  * as an application
    * minimal install requires few python dependencies - useful when no internet connectivity
    * tested on versions of python from 3.6 onwards
  * in terms of output
    * always standalone html pages, optionally pdf files with weasyprint
    * bootstrap layout adjusts content for according to device screen size
    * plots converted to SVG where possible for scaling and size reduction
* extensibility
  * html template and css can be replaced - no js
  * widely used bootstrap, many themes available, easy to customise
  * straightforward process for adding new content adaptors

Originally designed to solve enterprise reporting problems where comprehensive dashboard solution is not available or feasible, limited connectivity / packages available in private repo, work is conducted on remote servers, production jobs where limited reports are needed for quality assurance and debugging, developers and analysts with limited front-end knowledge need a quick and dirty solution.

Because of enterprise requirements:

* code is scanned by sonarcloud for security
* maintains high degree of test coverage
* aiming for strict type coverage with mypy
-->

[![image](https://img.shields.io/pypi/v/esparto.svg)](https://pypi.python.org/pypi/esparto)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/esparto.svg)](https://pypi.python.org/pypi/esparto/)
[![Build Status](https://travis-ci.com/domvwt/esparto.svg?branch=main)](https://travis-ci.com/domvwt/esparto)
[![codecov](https://codecov.io/gh/domvwt/esparto/branch/main/graph/badge.svg?token=35J8NZCUYC)](https://codecov.io/gh/domvwt/esparto)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=domvwt_esparto&metric=alert_status)](https://sonarcloud.io/dashboard?id=domvwt_esparto)
![PyPI - Downloads](https://img.shields.io/pypi/dm/esparto)

Introduction
------------

**esparto** is a Python library for generating reports with content from popular data analysis packages. **esparto** outputs well presented documents by default, abstracting away as many layout and formatting decisions as possible. Documents can be saved as self-contained HTML pages or in PDF format, allowing them to be viewed, shared, and stored easily and conveniently.

Basic Usage
-----------

```python
import esparto as es

# Create a Page object
page = es.Page(title="My Report")

# Add Python objects as content
page["Data Analysis"] = (pandas_dataframe, plotly_figure)

# Save to HTML or PDF
page.save_html("my-report.html")
page.save_pdf("my-report.pdf")

```

Main Features
-------------

- Adaptive layout
- Customisable with CSS and Jinja
- Jupyter Notebook friendly
- Output as HTML or PDF
- Built-in adaptors for:
  - Markdown
  - Images
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

If PDF output is required, [Weasyprint](https://weasyprint.org/) must also be installed.

Dependencies
------------

- [python](https://python.org/) >= 3.6
- [jinja2](https://palletsprojects.com/p/jinja/)
- [markdown](https://python-markdown.github.io/)
- [Pillow](https://python-pillow.org/)
- [PyYAML](https://pyyaml.org/)
- [weasyprint](https://weasyprint.org/) _(optional - required for PDF output)_

License
-------

[MIT](https://opensource.org/licenses/MIT)

Documentation
-------------

Full documentation and examples are available at [domvwt.github.io/esparto/](https://domvwt.github.io/esparto/).

Contributions, Issues, and Requests
-----------------------------------

All feedback and contributions are welcome - please raise an issue or pull request on [GitHub][GitHub].

Examples
--------

Iris Report - [Webpage](https://domvwt.github.io/esparto/examples/iris-report.html) |
[PDF](https://domvwt.github.io/esparto/examples/iris-report.pdf)

Bokeh and Plotly - [Webpage](https://domvwt.github.io/esparto/examples/interactive-plots.html) |
[PDF](https://domvwt.github.io/esparto/examples/interactive-plots.pdf)

<br>

<p width=100%>
<img width=80%  src="https://github.com/domvwt/esparto/blob/fdc0e787c0bc013d16667773e82e21c647b71d91/docs/images/iris-report-compressed.png?raw=true" alt="example page" style="border-radius:0.5%;">
</p>

<!-- ! List alternative libraries -->
<!-- Pandoc -->
<!-- Datapane -->
<!-- Dash / Plotly -->
<!-- Panel / Bokeh -->
<!-- Voila -->

<!-- * Links -->
[PyPI]: https://pypi.org/project/esparto/
[Conda]: https://anaconda.org/conda-forge/esparto
[Bootstrap]: https://getbootstrap.com/docs/4.6/getting-started/introduction/
[Pandas]: https://pandas.pydata.org/
[Matplotlib]: https://matplotlib.org/
[Bokeh]: https://docs.bokeh.org/en/latest/index.html
[Plotly]: https://plotly.com/
[GitHub]: https://github.com/domvwt/esparto
