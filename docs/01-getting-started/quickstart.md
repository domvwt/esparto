Quickstart
==========

The esparto library can be installed with pip. Only the minimal package requirements will be installed by default:

```bash
pip install esparto
```

<br>

For PDF output we will also require [weasyprint]("https://weasyprint.org/"), although
this is optional:

```bash
pip install weasyprint
```


<br>

Documents start with a Page object, to which user content can be added iteratively.
Creating a page, adding basic content, and saving the file can be achieved in a few
short lines:

```python
import esparto as es

my_page = es.Page(title="Esparto Quickstart")

content_md = """
Your *content* goes **here!**
"""

my_page += content_md
my_page.save_html("esparto-quick.html")
```
<br>

The rendered HTML document:

<img src='../esparto-quickstart-screenshot.png' style='border: 1px dotted lightgrey; width: 60%; height: auto'>

<br>

To add an image, pass a filepath to the page:

```python
import esparto as es

my_page = es.Page(title="Esparto Quickstart")

content_md = """
Your *content* goes **here!**
"""

my_page += content_md
my_page += "image.jpg"

my_page.save_html("esparto-quick-image.html")
```
<br>

Esparto determines that the string points to a valid image and loads the file:

<img src='../esparto-image-screenshot.png' height=70% style='border: 1px dotted lightgrey; width: 60%; height: auto%'>

<br>

And for PDF output:

```python
my_page.save_pdf("esparto-quick-image.pdf")
```

<br>

Please see the [examples page](../02-user-guide/examples.md) for more.

<br>
