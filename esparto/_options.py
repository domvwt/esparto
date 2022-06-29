"""Esparto configuration options."""

import collections.abc
import copy
import pprint
import traceback
from contextlib import ContextDecorator
from dataclasses import dataclass, field
from pathlib import Path
from tempfile import TemporaryDirectory
from types import TracebackType
from typing import Any, Dict, Mapping, Optional, Tuple, Type, Union

import yaml

from esparto import _MODULE_PATH


class ConfigMixin(object):
    _options_source: str

    def _to_dict(self) -> Dict[str, Any]:
        return public_dict(self.__dict__)

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        string = f"{pprint.pformat(self._to_dict(), sort_dicts=False)}"
        if hasattr(self, "_options_source"):
            string += (
                f"\nSource: {self._options_source}" if self._options_source else ""
            )
        return string


@dataclass(repr=False)
class MatplotlibOptions(yaml.YAMLObject, ConfigMixin):
    """Options for Matplotlib output.

    Attributes:
        html_output_format (str):
            How plots are rendered in HTML: 'png' or 'svg'.
        notebook_format (str):
            How plots are rendered in Jupyter Notebooks: 'png' or 'svg'.
        pdf_figsize (tuple or int):
            Specify size of Matplotlib figures in PDF output.
            An integer tuple can be passed as: (height, width).
            A float can be passed as a scaling factor.

    """

    yaml_loader = yaml.SafeLoader
    yaml_tag = "!MatplotlibOptions"

    html_output_format: str = "svg"
    notebook_format: str = "svg"
    pdf_figsize: Optional[Union[Tuple[int, int], float]] = 1.0


@dataclass(repr=False)
class PlotlyOptions(yaml.YAMLObject, ConfigMixin):
    """Options for Plotly output.

    Attributes:
        layout_args (dict):
            Arguments passed to `figure.update_layout()` at rendering time.

    """

    yaml_loader = yaml.SafeLoader
    yaml_tag = "!PlotlyOptions"

    layout_args: Dict[str, Any] = field(default_factory=lambda: {})


@dataclass(repr=False)
class BokehOptions(yaml.YAMLObject, ConfigMixin):
    """Options for Bokeh output.

    Attributes:
        layout_attributes (dict):
            Bokeh layout object attributes to set at rendering time.

    """

    yaml_loader = yaml.SafeLoader
    yaml_tag = "!BokehOptions"

    layout_attributes: Dict[str, Any] = field(
        default_factory=lambda: {"sizing_mode": "scale_width"}
    )


@dataclass(repr=False)
class OutputOptions(yaml.YAMLObject, ConfigMixin):
    """Options for configuring page rendering and output.

    Config options will automatically be loaded if a yaml file is found at
    either `./esparto-config.yaml` or `~/esparto-data/esparto-config.yaml`.

    Attributes:
        dependency_source (str):
            How dependencies should be provisioned: 'cdn' or 'inline'.
        bootstrap_cdn (str):
            Link to Bootstrap CDN. Used if dependency source is 'cdn'.
        bootstrap_css (str):
            Path to Bootstrap CSS file. Used if dependency source is 'inline'.
        esparto_css (str):
            Path to additional CSS file with esparto specific styles.
        esparto_js (str):
            Path to JavaScript file for interactive page elements.
        jinja_template (str):
            Path to Jinja HTML page template.

        matplotlib: Additional config options for Matplotlib.
        plotly: Additional config options for Plotly.
        bokeh: Additional config options for Bokeh.

    """

    yaml_loader = yaml.SafeLoader
    yaml_tag = "!OutputOptions"

    dependency_source: str = "cdn"
    bootstrap_cdn: str = (
        "<link rel='stylesheet' "
        "href='https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/5.1.3/css/bootstrap.min.css' "
        "integrity='sha512-GQGU0fMMi238uA+a/bdWJfpUGKUkBdgfFdgBm72SUQ6BeyWjoY/ton0tEjH+OSH9iP4Dfh+7HM0I9f5eR0L/4w==' "
        "crossorigin='anonymous' referrerpolicy='no-referrer'>"
    )
    bootstrap_css: str = str(_MODULE_PATH / "resources/css/bootstrap.min.css")
    esparto_css: str = str(_MODULE_PATH / "resources/css/esparto.css")
    esparto_js: str = str(_MODULE_PATH / "resources/js/esparto.js")
    jinja_template: str = str(_MODULE_PATH / "resources/jinja/base.html.jinja")

    matplotlib: MatplotlibOptions = MatplotlibOptions()
    bokeh: BokehOptions = BokehOptions()
    plotly: PlotlyOptions = PlotlyOptions()

    _pdf_temp_dir: str = TemporaryDirectory().name

    _options_source: str = ""

    def save(self, path: Union[str, Path] = "./esparto-config.yaml") -> None:
        """Save config to yaml file at `path`."""
        Path(path).write_text(self._to_yaml_str())

    @classmethod
    def load(cls, path: Union[str, Path]) -> "OutputOptions":
        """Load config from yaml file at `path`."""
        yaml_str = Path(path).read_text()
        opts: OutputOptions = yaml.safe_load(yaml_str)
        opts._options_source = str(path)
        return opts

    def _to_yaml_str(self) -> str:
        self_copy = copy.copy(self)
        del self_copy._options_source
        return str(yaml.dump(self_copy, default_flow_style=False, sort_keys=False))

    @classmethod
    def _autoload(cls) -> "OutputOptions":
        config_paths = [
            Path("./esparto-config.yaml"),
            Path.home() / "esparto-data/esparto-config.yaml",
        ]

        for p in config_paths:
            if p.is_file():
                opts = cls.load(p)
                opts._options_source = str(p)
                print("esparto config loaded from:", p)
                return opts
        return cls()


options = OutputOptions._autoload()


def update_recursive(
    source_dict: Dict[Any, Any], update_map: Mapping[Any, Any]
) -> Dict[Any, Any]:
    """Recursively update nested dictionaries.
    https://stackoverflow.com/a/3233356/8065696
    """
    for k, v in update_map.items():
        if isinstance(v, collections.abc.Mapping):
            source_dict[k] = update_recursive(source_dict.get(k, {}), v)
        else:
            source_dict[k] = v
    return source_dict


class options_context(ContextDecorator):
    def __init__(self, page_options: OutputOptions):
        self.page_options = page_options
        self.default_options = copy.copy(options)

    def __enter__(self) -> None:
        update_recursive(options.__dict__, self.page_options.__dict__)

    def __exit__(
        self, exc_type: Type[BaseException], exc_value: BaseException, tb: TracebackType
    ) -> None:
        if exc_type is not None:  # pragma: no cover
            traceback.print_exception(exc_type, exc_value, tb)
        update_recursive(options.__dict__, self.default_options.__dict__)


def resolve_config_option(config_option: str, value: Optional[str]) -> Any:
    if value is None:
        return getattr(options, config_option)
    else:
        return value


def public_dict(d: Dict[str, Any]) -> Dict[str, Any]:
    """Remove keys starting with '_' from dict."""
    return {
        k: v for k, v in d.items() if not (isinstance(k, str) and k.startswith("_"))
    }
