# Quick Start

## Create a Page
```python
page = es.Page(title="Page Title")
page[0] = "Page Content"
page.tree()
```
```
{'Page Title': [{'Section 0': [{'Row 0': [{'Column 0': ['Markdown']}]}]}]}
```

## Add Content
### Define Rows and Columns
```python
page = es.Page("Page Title")
page["Section One"]["Row One"]["Column One"] = "Some content"
page["Section One"]["Row One"]["Column Two"] = "More content"
page.tree()
```
```
{'Page Title': [{'Section One': [{'Row One': [{'Column One': ['Markdown']},
                                              {'Column Two': ['Markdown']}]}]}]}
```

### Define multiple Columns as a tuple of dicts
```python
page = es.Page("Page Title")
page["Section One"]["Row One"] = (
    {"Column One": "Some content"},
    {"Column Two": "More content"}
)
page.tree()
```
```
{'Page Title': [{'Section One': [{'Row One': [{'Column One': ['Markdown']},
                                              {'Column Two': ['Markdown']}]}]}]}
```

## Update Content
### Access existing content via Indexing or as Attributes
```python
page["Section One"]["Row One"]["Column One"] = image_01
page.section_one.row_one.column_two = image_02
page.section_one.tree()
```
```
{'Page Title': [{'Section One': [{'Row One': [{'Column One': ['Image']},
                                              {'Column Two': ['Image']}]}]}]}
```

## Delete Content
### Delete the last Column
```python
del page.section_one.row_one[-1]
```
```
{'Page Title': [{'Section One': [{'Row One': [{'Column One': ['Image']}]}]}]}
```
### Delete a named Column
```python
del page.section_one.row_one.column_two
page.tree()
```
```
{'Page Title': [{'Section One': [{'Row One': [{'Column One': ['Image']}]}]}]}
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
