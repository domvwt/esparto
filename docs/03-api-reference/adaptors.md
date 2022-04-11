# esparto.design.adaptors

!!! info
    The `content_adaptor` function is called internally when an explicit `Content` class is not provided.

    Objects are matched to a suitable `Content` class through [_single dispatch_](https://docs.python.org/3/library/functools.html#functools.singledispatch).

    ``` python
    import esparto as es

    # Text automatically converted to Markdown content.
    page = es.Page(title="New Page")
    page["New Section"] = "Example _markdown_ text."
    page.tree()
    ```
    ```
    {'New Page': [{'New Section': [{'Row 0': [{'Column 0': ['Markdown']}]}]}]}
    ```

## ::: esparto.design.adaptors

<br>
