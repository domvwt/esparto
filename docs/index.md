# Welcome
Esparto is a simple toolkit for creating accessible and shareable HTML documents.
The library provides a streamlined API that lets users define their page in terms of 
sections, rows, and columns; and an intelligent wrapping system that automatically 
converts content to a format compatible with modern web browsers.

## Overview
We use the grid system and components from [Bootstrap](https://getbootstrap.com/) to ensure 
documents adapt to the viewing device and appear immediately familiar and accessible.
No knowledge of Bootstrap or web development is required to use the library, however, as these 
details are conveniently abstracted.

At publishing time, the completed document is passed to [Jinja2](https://palletsprojects.com/p/jinja/) 
and fed into an HTML template with all style details and dependencies captured inline.

Esparto supports content rendering within Jupyter Notebooks, allowing users to interactively 
and iteratively build documents without disrupting their workflow.

## Features 
* Lightweight API
* Jupyter Notebook support
* Familiar and accessible page format
* Device responsive display
* Self contained / inline dependencies
* MIT License


## Integrations
The following content types are currently supported

* Markdown text
* Images
* Matplotlib figures
* Pandas DataFrames

<br>