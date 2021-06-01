# Examples

These examples demonstrate recommended ways of working with `esparto`.
Note that Jupyter Notebooks do not preserve the formatting of rendered
content between sessions - be sure to re-run the examples in order to
view the output as intended.

## Data Analysis

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/domvwt/esparto/blob/main/docs/examples/iris-report.ipynb)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/domvwt/esparto/main?filepath=docs%2Fexamples%2Firis-report.ipynb)
[![GitHub](https://img.shields.io/badge/view%20on-GitHub-lightgrey)](https://github.com/domvwt/esparto/blob/main/docs/examples/iris-report.ipynb)

The iris dataset is one of the most well known datasets in statistics and
data science. This notebook shows how we can put together a simple
data analysis report in `esparto`.

This example covers:

* Text content with markdown formatting
* Including images from files
* Converting a Pandas DataFrame to a table
* Adding plots from Matplotlib and Seaborn

Output: [HTML](../examples/iris-report.html) | [PDF](../examples/iris-report.pdf)

----



## Interactive Plotting

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/domvwt/esparto/blob/main/docs/examples/interactive-plots.ipynb)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/domvwt/esparto/main?filepath=docs%2Fexamples%2Finteractive-plots.ipynb)
[![GitHub](https://img.shields.io/badge/view%20on-GitHub-lightgrey)](https://github.com/domvwt/esparto/blob/main/docs/examples/interactive-plots.ipynb)

The [pandas-bokeh](https://github.com/PatrikHlobil/Pandas-Bokeh) library
offers convenient functions for producing interactive Bokeh plots with
few lines of code.

With the [Plotly backend for Pandas](https://plotly.com/python/pandas-backend/)
we can access the Plotly Express API directly from the `.plot()` method of
any DataFrame or Series.

This notebook shows basic examples from each library:

* Interactive plotting with Bokeh and Plotly
* Adding interactive content to the page

Output: [HTML](../examples/interactive-plots.html) | [PDF](../examples/interactive-plots.pdf)

!!! note
    PDF output is not officially supported for `Bokeh` at this time.

<br>
