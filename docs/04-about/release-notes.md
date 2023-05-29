Release Notes
=============

4.3.0 (2023-05-29)
------------------

- Compatibility
    - Python 3.11 support added

4.2.0 (2022-11-10)
------------------

- Fixes
    - Fix bug preventing some Matplotlib figures from being converted to SVG and HTML [(#127)](https://github.com/domvwt/esparto/issues/127)

4.1.0 (2022-06-29)
------------------

- Page Style
    - Replace footer with icon buttons
        - Esparto home
        - Share document (for compatible systems)
        - Print page
    - Add CSS style for icon buttons
    - Prefer fully specified fonts to system fonts
    - Remove underline from URLs

4.0.0 (2022-04-19)
------------------

- New Features
    - Command line tools for printing default Jinja and CSS files
- Fixes
    - Config YAML now read with safe loader
- Deprecations
    - Removed CDN theme links
- Dependencies
    - Image content now supported without PIL

3.0.2 (2022-02-28)
------------------

- Fixes
    - Set minimum page height to fill device screen
    - Read page additional output options when publishing HTML and PDF

3.0.1 (2022-02-24)
------------------

- Fixes
    - Remove call to `fig.tight_layout()` when converting Matplotlib figure to SVG for PDF

3.0.0 (2022-02-23)
------------------

- API
    - Page now accepts `max_width` and `output_options` arguments
    - Content classes no longer accept `width` or `height` arguments
- New Features
    - Output rendering options can now be configured at page level
    - Additional markdown features recognised
- Fixes
    - JavaScript is now placed at end of page so HTML is loaded first
- Page Style
    - Removed unnecessary indentation
    - Tables now render in minimal, clean style
    - Improvements to sizing and centring of plots
    - Cleaned up unnecessary HTML and CSS
    - Majority of CSS attributes moved to `esparto.css`
- Dependencies
    - Pillow is now optional
    - BeautifulSoup4 is now required
    - Upper version limits removed from all
- Other
    - Type hints implemented with ~100% coverage

2.0.0 (2021-09-19)
------------------

- New Features
    - Links to Bootswatch CDN for page themes
    - Reorganise and add options to `esparto.options`
    - Table of Contents generator for Page element
    - Save and Load config options
    - Define Columns and Cards as dict of {"title": content}
    - Add or replace Content by positional index
- New Layout Classes
    - CardSection: Section with Cards as the default Content container
    - CardRow: Row of Cards
    - CardRowEqual: Row of equal width cards

1.3.0 (2021-07-19)
------------------

- New Layout class
    - Card: Bordered container for grouping content
- Updated Content class
    - FigureMpl: SVG rendered plots now flex up to 150% of original size
- Other
    - Defined string and repr representations for current settings
    - Updated CSS so maintain distance from header if main title is not defined
    - Updated content adaptor to allow other Layout objects as valid children for Column

1.2.0 (2021-06-28)
------------------

- Implicitly read Markdown text files

1.1.0 (2021-06-18)
------------------

- New Layout classes
    - Spacer: make an empty column within a Row
    - PageBreak: enforce a page break in printed / PDF documents
- New Content class
    - RawHTML: place raw HTML code in the page
- Updated Content classes
    - DataFramePd: add new CSS style to minimise row height
    - FigureMpl: SVG rendered plots are now responsive and horizontally centred
- New publishing features
    - CSS stylesheet path can be passed to options.css_styles
    - Jinja template path can be passed to options.jinja_template

1.0.1 (2021-06-01)
------------------

- Update dependencies
- Fix SVG rendering in PDF
- Update docs and examples

1.0.0 (2021-05-31)
------------------

- Improve API
- Responsive SVG plots
- Update Jinja template to remove branding
- Refactor codebase

0.2.5 (2021-05-06)
------------------

- Fix linting errors
- Add dataclasses dependency for Python < 3.7

0.2.4 (2021-05-04)
------------------

- Fix bug corrupting page titles
- Lazy load the content dependency dict
- Remove unused code

0.2.3 (2021-05-03)
------------------

- Make documents 'print friendly'
- Output to PDF with weasyprint
- Export matplotlib plots as SVG by default
- Use  `esparto.options` for configuring behaviour

0.2.2 (2021-04-24)
------------------

- Fix notebook display for Colab

0.2.1 (2021-04-24)
------------------

- Add Bootstrap dependencies for relevant content classes
- Inherit FigureBokeh height from Bokeh object
- Fix issues with in-notebook content rendering

0.2.0 (2021-04-23)
------------------

- Add support for Bokeh and Plotly

0.1.2 (2021-04-09)
------------------

- Relax dependency on Pillow to allow versions >=7.0.0 and <9.0.0

0.1.1 (2021-04-08)
------------------

- Update package metadata for pypi

0.1.0 (2021-04-07)
------------------

- First public release

<br>
