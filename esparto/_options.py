"""Global configuration options."""

from dataclasses import dataclass


@dataclass
class ConfigOptions:
    offline_mode: bool = False
    _online_source: str = "cdn"
    _offline_source: str = "inline"

    matplotlib_output_format: str = "svg"
    matplotlib_notebook_format: str = "png"

    pdf_temp_dir: str = ".pdf-temp"


options = ConfigOptions()


def get_source_from_options(source):
    if source == "esparto.options":
        if options.offline_mode:
            return options._offline_source
        else:
            return options._online_source
    elif source in ["cdn", "inline"]:
        return source
    raise ValueError(f"Unrecognised source: {source}")
