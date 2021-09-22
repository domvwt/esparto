"""Esparto configuration options."""

import copy
import pprint
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

import yaml  # type: ignore

from esparto import _MODULE_PATH
from esparto._utils import public_dict


class ConfigMixin(object):
    _options_source: str

    def _to_dict(self) -> dict:
        return public_dict(self.__dict__)

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        string = f"{pprint.pformat(self._to_dict())}"
        if hasattr(self, "_options_source"):
            string += (
                f"\nSource: {self._options_source}" if self._options_source else ""
            )
        return string


@dataclass(repr=False)
class MatplotlibOptions(ConfigMixin):
    """Options for Matplotlib output.

    Attributes:
        html_output_format (str):
            How plots are rendered in HTML: 'png' or 'svg'.
        notebook_format (str):
            How plots are rendedered in Jupyter Notebooks: 'png' or 'svg'.
        pdf_figsize (tuple or int):
            Specify size of Matplotlib figures in PDF output.
            An integer tuple can be passed as: (height, width).
            A float can be passed as a scaling factor.

    """

    html_output_format: str = "svg"
    notebook_format: str = "svg"
    pdf_figsize: Optional[Union[Tuple[int, int], float]] = 0.7


@dataclass(repr=False)
class PlotlyOptions(ConfigMixin):
    """Options for Plotly output.

    Attributes:
        layout_args (dict):
            Arguments passed to figure.update_layout() at rendering time.

    """

    layout_args: Dict[str, Any] = field(
        default_factory=lambda: {
            "paper_bgcolor": "rgba(0,0,0,0)",
            "plot_bgcolor": "rgba(0,0,0,0)",
            "modebar": {"bgcolor": "white"},
        }
    )


@dataclass(repr=False)
class BokehOptions(ConfigMixin):
    """Options for Bokeh output.

    Attributes:
        layout_attributes (dict):
            Bokeh layout object attributes to set at rendering time.

    """

    layout_attributes: Dict[str, Any] = field(
        default_factory=lambda: {"sizing_mode": "scale_width"}
    )


@dataclass(repr=False)
class ConfigOptions(ConfigMixin):
    """Options for configuring esparto behaviour and output.

    Config options will automatically be loaded if a yaml file is found at
    either './esparto-config.yaml' or '~/esparto-data/esparto-config.yaml'.

    Attributes:
        dependency_source (str):
            How dependencies should be provisioned: 'cdn' or 'inline'.
        bootstrap_cdn (str):
            Link to Bootstrap CDN. Used if dependency source is 'cdn'.
            Alternative links are available via esparto.bootstrap_cdn_themes.
        bootstrap_css (str):
            Path to Bootstrap CSS file. Used if dependency source is 'inline'.
        esparto_css (str):
            Path to additional CSS file with esparto specific styles.
        jinja_template (str):
            Path to Jinja HTML page template.

        matplotlib: Additional config options for Matplotlib.
        plotly: Additional config options for Plotly.
        bokeh: Additional config options for Bokeh.

    """

    dependency_source: str = "cdn"
    bootstrap_cdn: str = (
        '<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css" '
        'integrity="sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh" crossorigin="anonymous">'
    )
    bootstrap_css: str = str(_MODULE_PATH / "resources/css/bootstrap.min.css")
    esparto_css: str = str(_MODULE_PATH / "resources/css/esparto.css")
    jinja_template: str = str(_MODULE_PATH / "resources/jinja/base.html.jinja")

    matplotlib: MatplotlibOptions = MatplotlibOptions()
    bokeh: BokehOptions = BokehOptions()
    plotly: PlotlyOptions = PlotlyOptions()

    _pdf_temp_dir: str = ".pdf-temp"

    _options_source: str = ""

    def save(self, path: Union[str, Path] = "./esparto-config.yaml") -> None:
        """Save config to yaml file at `path`."""
        path = Path(path)
        self_copy = copy.copy(self)
        del self_copy._options_source
        yaml_str = yaml.dump(self_copy)
        path.write_text(yaml_str)

    def load(self, path: Union[str, Path]) -> None:
        """Load config from yaml file at `path`."""
        path = Path(path)
        yaml_str = path.read_text()
        self = yaml.unsafe_load(yaml_str)
        self._options_source = str(path)

    def _autoload(self):
        config_paths = [
            Path("./esparto-config.yaml"),
            Path.home() / "esparto-data/esparto-config.yaml",
        ]
        for p in config_paths:
            if p.is_file():
                self.load(p)
                print("esparto config loaded from:", p)
                self._options_source = str(p)
                break


options = ConfigOptions()


def resolve_config_option(config_option: str, value: Optional[str]):
    if value is None:
        return getattr(options, config_option)
    else:
        return value
