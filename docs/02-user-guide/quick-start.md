# Quick Start

## Create a Page

```python
import esparto as es

page = es.Page(title="Page Title")
page["Section Title"] += "Some text"
page["Section Title"] += "More text"

page.tree()
```

```
{'Page Title': [{'Section Title': [{'Row 0': [{'Column 0': ['Markdown']}]},
                                   {'Row 1': [{'Column 0': ['Markdown']}]}]}]}
```

## Add Content

### Define Rows and Columns

```python
page["Section Title"]["Row Title"][0] = "Some content"
page["Section Title"]["Row Title"][1] = "More content"
```

```
{'Page Title': [{'Section Title': [{'Row Title': [{'Column 0': ['Markdown']},
                                                  {'Column 1': ['Markdown']}]}]}]}
```

### Define multiple Columns

```python
page["Section Title"]["Row Title"] = (
    {"Column Title": "Some content"},
    {"Column Two": "More content"}
)
```

```
{'Page Title': [{'Section Title': [{'Row Title': [{'Column Title': ['Markdown']},
                                                  {'Column Two': ['Markdown']}]}]}]}
```

## Update Content

### Access existing content via Indexing or as Attributes

```python
page["Section Title"]["Row Title"]["Column Title"] = image_01
page.section_title.row_title.column_two = image_02
```

```
{'Page Title': [{'Section Title': [{'Row Title': [{'Column Title': ['Image']},
                                                  {'Column Two': ['Image']}]}]}]}
```

## Delete Content

### Delete the last Column

```python
del page.section_title.row_title[-1]
```

```
{'Page Title': [{'Section Title': [{'Row Title': [{'Column Title': ['Image']}]}]}]}
```

### Delete a named Column

```python
del page.section_title.row_title.column_two
page.tree()
```

```
{'Page Title': [{'Section Title': [{'Row Title': [{'Column Title': ['Image']}]}]}]}
```

## Save the Document

### As a webpage

```python
my_page.save_html("my-esparto-doc.html")
```

### As a PDF

```python
my_page.save_pdf("my-esparto-doc.pdf")
```

<br>
