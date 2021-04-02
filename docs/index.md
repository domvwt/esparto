# Welcome

## Introduction
A simple toolkit for creating accessible and shareable HTML documents.

## Overview
Document layout and formatting is provided by [Bootstrap](https://getbootstrap.com/). 
A responsive grid system ensures that documents will adapt to any device size and appear
immediately accessible with a familiar style and appearance. 
No knowledge of Bootstrap or web development is required to use the library, however, as these 
details are conveniently abstracted.

At publishing time, the completed document is passed to [Jinja2](https://palletsprojects.com/p/jinja/) 
and fed into an HTML template with all style details and dependencies captured inline.

Esparto supports content rendering within Jupyter Notebooks, allowing users to interactively 
and iteratively build documents without disrupting their workflow.

## Features 
* Lightweight API
* Familiar and accessible page format
* Device responsive display
* Self contained / inline dependencies
* Jupyter Notebook support
* MIT License


## Integrations
The following content types are currently supported

* Markdown text
* Images
* Matplotlib figures
* Pandas DataFrames
