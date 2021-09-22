# Quick Reference


### Create a New Page
All pages start with a `Page` object. Additional options are available for
including a Table of Contents and a brand name in the header.
```python
import esparto as es
page = es.Page(title="My Page", navbrand="esparto", table_of_contents=True)
```
### Page Layout
Pages items always follow the same hierarchy:

`Page` -> `Section` -> `Row` -> `Column` -> `Content`

If content is passed without explicitly defining the hierarcy it will be automatically inferred.

### Add Content
`Page` elements can be created and retrieved by title or by index. Elements can also be retrieved as attributes if they already exist.
If new content is passed to an index it will either overwrite the content at that position or be appended to the parent element's child list.

```python
page["Section Title"]["Row Title"]["Column Title"] = content  # get element by title
page.section_title.row_title.column_title = content  # get element by attribute name (if it exists)
page[0][1][2] = content  # get element by index
page[0][1][-1] = content  # overwrite the last item
page["Section Title"] = {"column title": column content}  # use a dict to pass a column title

page["Section Title"] << content  # add content and return original object
page["Section Title"] >> content  # add content and return esparto element

page["Section Title"][0] = (content_a, content_b)  # use a tuple to place content in the same row
page["Section Title"]["Row Title"][0] = (content_a, content_b)  # or the same column
```

_NOTE:
When an item is added to the page it will either overwrite an existing item or be appended to the end of the parent element child list, regardless of the given index._

### Remove content
```python
del page["Section Title"]["Row Title"]["Column Title"]  # by title
del page.section_title.row_title.column_title  # by attribute name
del page[0][0][0]  # by index
```
### View the Page
```python
page.tree()  # print the page structure
page.display()  # render the page in Jupyter cell output
```

### Save the Page
```python
page.save_html("my-page.html")
page.save_pdf("my-page.pdf")
```

### Using Cards
`Card` objects are a useful way of grouping related content items. They can be added explicitly as content:
```python
page["Section Title"][0][0] = es.Card(title="Card Title", children=[content])
```
Or generated implicitly in a `CardSection`:
```python
page["Section Title"] = es.CardSection()
page["Section Title"][0][0] = {"Card Title": content}
```

### Spacers and PageBreaks
A `Spacer` is used to fill add empty space to a `Row`. The `PageBreak` object is used to force a page-break in printed or PDF output.
```python
page["Section Title"]["Row Title"] = content, es.Spacer()  # content will share row space equally with Spacer
page["Section Title"] += es.PageBreak()  # add a page break at the end of the section
```

### Config Options
There are several options available for configuring the behaviour and appearance of the `Page`. Call `help` on the `options` object for more information or check the relevant documentation.
```python
help(es.options)
# or
es.options?
```
