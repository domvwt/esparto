# Welcome
Esparto is a simple HTML and PDF document generator for Python. Its primary use is for generating shareable single page reports
with content from popular analytics and data science libraries.

## Overview
The library features a streamlined API that defines pages in terms of
sections, rows, and columns; and an intelligent wrapping system that automatically
converts Python objects into content.

We use the grid system and components from [Bootstrap](https://getbootstrap.com/) to ensure
documents adapt to the viewing device and appear immediately familiar and accessible.
No knowledge of Bootstrap or web development is required to use the library, however, as these
details are conveniently abstracted.

At publishing time, the completed document is passed to [Jinja2](https://palletsprojects.com/p/jinja/)
and fed into an HTML template with all style details and dependencies captured inline.

Esparto supports content rendering within Jupyter Notebooks, allowing users to interactively
and iteratively build documents without disrupting their workflow.

PDF conversion is provided by [Weasyprint](https://weasyprint.org/).

### Features
* Lightweight API
* No CSS or HTML required
* Device responsive display
* Self contained / inline dependencies
* Jupyter Notebook support
* Printer friendly formatting
* PDF output
* MIT License

### Supported Content
* Markdown
* Images
* Pandas DataFrames
* Plots from:
    * Matplotlib
    * Bokeh
    * Plotly

<br>
