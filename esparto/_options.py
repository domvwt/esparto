"""Global configuration options."""

from dataclasses import dataclass

from esparto import _MODULE_PATH


@dataclass
class ConfigOptions:
    default = "esparto.options"

    offline_mode = False
    _online_source = "cdn"
    _offline_source = "inline"

    matplotlib_output_format = "svg"
    matplotlib_notebook_format = "png"

    css_styles = str(_MODULE_PATH / "resources/css/esparto.css")
    jinja_template = str(_MODULE_PATH / "resources/jinja/base.html.jinja")

    pdf_temp_dir = ".pdf-temp"


options = ConfigOptions


def get_dep_source_from_options(source: str):
    if source == options.default:
        if options.offline_mode:
            return options._offline_source
        else:
            return options._online_source
    elif source in [options._online_source, options._offline_source]:
        return str(source)
    raise ValueError(f"Unrecognised source: {source}")


def resolve_config_option(config_option: str, value: str):
    if value == options.default:
        return getattr(options, config_option)
    else:
        return value
