"""Global configuration options."""

import pprint
from dataclasses import dataclass
from typing import Optional

from esparto import _MODULE_PATH


@dataclass
class ConfigOptions:

    offline_mode: bool = False
    _online_source: str = "cdn"
    _offline_source: str = "inline"

    matplotlib_output_format: str = "svg"
    matplotlib_notebook_format: str = "png"

    css_styles: str = str(_MODULE_PATH / "resources/css/esparto.css")
    jinja_template: str = str(_MODULE_PATH / "resources/jinja/base.html.jinja")

    pdf_temp_dir: str = ".pdf-temp"

    def _to_dict(self) -> dict:
        return {
            attr: getattr(self, attr) for attr in dir(self) if not attr.startswith("_")
        }

    def __repr__(self) -> str:
        return f"{pprint.pformat(self._to_dict())}\n{type(self)}"

    def __str__(self) -> str:
        return f"{pprint.pformat(self._to_dict())}"


options = ConfigOptions()


def get_dep_source_from_options(source: Optional[str]):
    if source is None:
        if options.offline_mode:
            return options._offline_source
        else:
            return options._online_source
    elif source in [options._online_source, options._offline_source]:
        return str(source)
    raise ValueError(f"Unrecognised source: {source}")


def resolve_config_option(config_option: str, value: Optional[str]):
    if value is None:
        return getattr(options, config_option)
    else:
        return value
