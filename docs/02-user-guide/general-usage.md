## Offline Mode
When working in an environment with no internet connection it is necessary to
use inline content dependencies rather than the preferred Content Distribution Network (CDN).


Offline mode can be activated by changing the relevant `esparto.options` attribute:
```python
import esparto as es

es.options.offline_mode = True
```

## Matplotlib Output
To produce sharp and scalable images, esparto defaults to SVG format for
static plots.
This can cause a significant drain on resources when plotting a high number
of data points and so PNG format may be preferred.

PNG format can be selected for all Matplotlib plots:
```python
es.options.matplotlib_output_format = "png"
```

Or configured on a case by case basis:
```python
fig = df.plot()
esparto_fig = es.FigureMpl(fig, output_format="png")
```

Options provided directly to `FigureMpl` will override the global configuration.

## PDF Output

### From the API
Saving a page to PDF is achieved through the API by calling the `.save_pdf()`
method from a `Page` object:

```python
import esparto as es

my_page = es.Page(title="My Page")
my_page += "image.jpg"
my_page.save_pdf("my-page.pdf)
```

In order to render plots for PDF output, they must be rendered to SVG. While
this leads to consistent and attractive results for Matplotlib figures, it is
less predictable and requires additional system configuration for Bokeh and
Plotly objects.

#### Plotly
The preferred approach with Plotly is to use the Kaleido library, which is installable
with pip:
```bash
pip install kaleido
```
Esparto will automatically handle the conversion, provided Kaleido is available.

Make sure to inspect results for unusual cropping and other artifacts.

#### Bokeh
The approach taken by Bokeh is to use a browser and webdriver combination.
I have not been able to make this work during testing but the functionality
has been retained in esparto should you have more luck with it.

See the Bokeh documenation on [additional dependencies for exporting plots.](https://docs.bokeh.org/en/latest/docs/user_guide/export.html#additional-dependencies)

Conversion should be handled by esparto, provided the Bokeh dependencies
are satsified.

### Saving from a Browser
Alternatively, it is possible to save any HTML page as a PDF through the print
menu in your web browser. This method should work with all content types.

<br>
