Release Notes
=============

1.3.0 (2021-07-19)
------------------
-   New Layout class
    -   Card: Bordered container for grouping content
-   Updated Content class
    -   FigureMpl: SVG rendered plots now flex up to 150% of original size
-   Other
    -   Defined string and repr representations for current settings
    -   Updated CSS so maintain distance from header if main title is not defined
    -   Updated content adaptor to allow other Layout objects as valid children for Column


1.2.0 (2021-06-28)
------------------
-   Implicitly read markdown text files


1.1.0 (2021-06-18)
------------------
-   New Layout classes
    -   Spacer: make an empty column within a Row
    -   PageBreak: enforce a page break in printed / PDF documents
-   New Content class
    -   RawHTML: place raw HTML code in the page
-   Updated Content classes
    -   DataFramePd: add new CSS style to minimise row height
    -   FigureMpl: SVG rendered plots are now responsive and horizontally centred
-   New publishing features
    -   CSS stylesheet path can be passed to options.css_styles
    -   Jinja template path can be passed to options.jinja_template


1.0.1 (2021-06-01)
------------------
-   Update dependencies
-   Fix SVG rendering in PDF
-   Update docs and examples


1.0.0 (2021-05-31)
------------------
-   Improve API
-   Responsive SVG plots
-   Update Jinja template to remove branding
-   Refactor codebase


0.2.5 (2021-05-06)
------------------
-   Fix linting errors
-   Add dataclasses dependency for Python < 3.7


0.2.4 (2021-05-04)
------------------
-   Fix bug corrupting document titles
-   Lazy load the content dependency dict
-   Remove unused code


0.2.3 (2021-05-03)
------------------
-   Make documents 'print friendly'
-   Output to PDF with weasyprint
-   Export matplotlib plots as SVG by default
-   Use  `esparto.options` for configuring behaviour


0.2.2 (2021-04-24)
------------------
-   Fix notebook display for Colab


0.2.1 (2021-04-24)
------------------
-   Add Bootstrap dependencies for relevant content classes
-   Inherit FigureBokeh height from Bokeh object
-   Fix issues with in-notebook content rendering


0.2.0 (2021-04-23)
------------------
-   Add support for Bokeh and Plotly


0.1.2 (2021-04-09)
------------------
-   Relax dependency on Pillow to allow versions >=7.0.0 and <9.0.0


0.1.1 (2021-04-08)
------------------
-   Update package metadata for pypi


0.1.0 (2021-04-07)
------------------
-   First public release

<br>
