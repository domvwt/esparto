# esparto._adaptors
!!! info
    The ```content_adaptor``` is called internally when an explicit Content class is not provided.

    Input objects are matched to a suitable Content class through [_single dispatch_](https://docs.python.org/3/library/functools.html#functools.singledispatch).

    ``` python
    import esparto as es

    # Text automatically converted to Markdown content.
    section = es.Section()
    section += "Example _markdown_ text."
    print(section)
    ```
    ```
    {'Section': [{'Row': [{'Column': ['Markdown']}]}]}
    ```


## ::: esparto._adaptors

<br>
