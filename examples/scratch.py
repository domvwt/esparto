#!/usr/bin/env python
# coding: utf-8

# # Interactive Plots with Bokeh and Plotly
# This notebook demonstrates how we can incorporate interactive plots from Bokeh and Plotly into a page.
# 
# 
# We will look at:
# * Interactive plotting with Bokeh and Plotly
# * Adding interactive content to the page

# In[1]:


# Environment setup
import os
# get_ipython().system('pip install -Uqq esparto plotly bokeh pandas-bokeh')
# if os.environ.get("BINDER_SERVICE_HOST"):
#     get_ipython().system('pip install -Uqq pandas')


# In[2]:


import esparto as es
import numpy as np
import pandas as pd
import pandas_bokeh
import bokeh as bk
import plotly


# In[3]:


# bk.io.output_notebook()


# In[4]:


# From: https://github.com/PatrikHlobil/Pandas-Bokeh#Examples
np.random.seed(1)
ts = pd.Series(np.random.normal(1000), index=pd.date_range('1/1/2000', periods=1000))
df_lines = pd.DataFrame(np.random.normal(1000, 4), index=ts.index, columns=list('ABCD'))
df_lines = df_lines.cumsum()
# df_lines.head()


# In[5]:


# bokeh_lines = df_lines.plot_bokeh(title="Time Series")
bokeh_lines = df_lines.plot().get_figure()


# In[6]:


df_mpg = pd.read_csv("https://raw.githubusercontent.com/mwaskom/seaborn-data/master/mpg.csv")
# df_mpg.head()


# In[7]:


# bokeh_scatter = df_mpg.plot_bokeh.scatter(
#     title="Cars",
#     x="mpg", y="acceleration", 
#     category="origin",
#     size=8,
#     alpha=0.7,
#     line_color=None
# )

bokeh_scatter = df_mpg.plot.scatter("mpg", "acceleration").get_figure()


# In[8]:


plotly_lines = df_lines.plot(backend="plotly", template="plotly_white", title="Time Series")
# plotly_lines.show()


# In[9]:


plotly_scatter = df_mpg.plot.scatter(
    title="Cars",
    x="mpg", y="acceleration", 
    color="model_year",
    color_continuous_scale="burg_r",
    facet_col="origin",
    backend="plotly", 
    template="plotly_white",
)
# plotly_scatter.show()


# In[10]:


my_page = es.Page(title="Interactive Plots")

bokeh_section = es.Section(title="Bokeh")
bokeh_section += """

The [pandas-bokeh](https://github.com/PatrikHlobil/Pandas-Bokeh) library offers 
convenient functions for producing interactive Bokeh plots with few lines of code.

Bokeh figures will preserve their default aspect ratio by default - though this behaviour
can be configured through the Bokeh figure object in some cases. Composite objects, such
as the line chart with range slider, may need to be created using the Bokeh core API in
order to configure them correctly.

"""

bokeh_lines.sizing_mode = "stretch_width"  # Has no effect as this is a composite object
bokeh_scatter.sizing_mode = "stretch_width"  # This plot will be responsive to screen width

bokeh_section += (
    es.Row(es.Column(bokeh_lines, title="Line Plot with Range Slider")), 
    es.Row(es.Column(bokeh_scatter, title="Scatter Plot"))
)


plotly_section = es.Section(title="Plotly")
plotly_section += """

With the [Plotly backend for Pandas](https://plotly.com/python/pandas-backend/) 
we can access the Plotly Express API directly from the '.plot()' method of any DataFrame or Series.

Plotly figures will expand to fill their container space by default. 
All [esparto](https://domvwt.github.io/esparto/) figure classes can be manually adjusted 
through their width and height attributes.

"""

plotly_section += (
    es.Row(es.Column(plotly_lines, title="Line Plot")),
    es.Row(es.Column(plotly_scatter, title="Scatter Plot with Facet Columns"))
)

my_page += bokeh_section, plotly_section


# Please note that in-notebook page rendering can be temperamental when using certain components due to 
# timing issues while waiting for CDN content. If the page does not render, try rerunning the cell a few 
# times and it will eventually appear. You should have no issues when opening the HTML document.

# In[14]:


# my_page


# We can now save our page to an HTML file and share it.

# In[12]:


page_name = "interactive-plots.html"
my_page.save(page_name)


# Check your current working directory for the finished report!
