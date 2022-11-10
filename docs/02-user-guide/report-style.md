# Report Style

## Output Options

Customising the look and feel of **esparto** pages is best achieved through
modifying the default Jinja template and CSS style sheet.
New templates and styles can be passed to `es.options` to replace the global
defaults, or passed to the `es.Page` constructor using the `es.OutputOptions` class.

```python
# Updating global defaults.
es.options.esparto_css = "./esparto.css"
es.options.jinja_template = "./esparto.html.jinja"
es.options.matplotlib.notebook_format = "png"
```

```python
# Using page level options.
output_options = es.OutputOptions()

output_options.esparto_css = "./esparto.css"
output_options.jinja_template = "./esparto.html.jinja"
output_options.matplotlib.notebook_format = "png"

page = es.Page(output_options=output_options)
```

Options can be saved and loaded from disk using class methods.
If an `esparto-config.yaml` file is found in the working directory, or at
`~/esparto-data/esparto-config.yaml`, it will be loaded automatically when
**esparto** is imported.

```python
# These options will be loaded automatically for sessions in the same directory.
output_options.save("./esparto-config.yaml")

# These will be loaded only if no yaml file is found in the working directory.
output_options.save("~/esparto-data/esparto-config.yaml")
```

## Printing Default Resources

It's recommended to use the standard CSS and Jinja template files as a starting
point for any changes.
A command line interface is provided for printing the default resources.

```bash
# Print default esparto.css to `esparto.css`.
python -m esparto print_esparto_css > esparto.css
```

```bash
# Print default jinja template to `esparto.html.jinja`.
python -m esparto print_jinja_template > esparto.html.jinja
```

```bash
# Print default Bootstrap CSS to `bootstrap.css`.
python -m esparto print_bootstrap_css > bootstrap.css
```

```bash
# Print default output options to `esparto-config.yaml`.
python -m esparto print_default_options > esparto-config.yaml
```

## More Options

For details on additional options please read the
[documentation for the Options module.](/03-api-reference/options/)

<br>
