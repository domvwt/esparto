"""Global configuration options."""

import pprint
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple, Union

import yaml  # type: ignore

from esparto import _MODULE_PATH
from esparto._utils import public_dict


@dataclass
class ConfigOptions:

    matplotlib_output_format: str = "svg"
    matplotlib_notebook_format: str = "svg"
    matplotlib_pdf_figsize: Optional[Union[Tuple[int, int], float]] = 0.7

    dependency_source: str = "cdn"
    bootstrap_cdn: str = (
        '<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css" '
        + 'integrity="sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh" crossorigin="anonymous">'
    )
    bootstrap_inline: str = str(_MODULE_PATH / "resources/css/bootstrap.min.css")
    esparto_css: str = str(_MODULE_PATH / "resources/css/esparto.css")
    jinja_template: str = str(_MODULE_PATH / "resources/jinja/base.html.jinja")

    _pdf_temp_dir: str = ".pdf-temp"

    _options_source: str = ""

    def save(self, path: Union[str, Path] = "./esparto-config.yaml") -> None:
        """Save config to `path`."""
        path = Path(path)
        yaml_str = yaml.safe_dump(self._to_dict())
        path.write_text(yaml_str)

    def load(self, path: Union[str, Path]) -> None:
        """Load config from `path`."""
        path = Path(path)
        yaml_str = path.read_text()
        opts = yaml.safe_load(yaml_str)
        self.__dict__.update(opts)
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

    def _to_dict(self) -> dict:
        return public_dict(self.__dict__)

    def __repr__(self) -> str:
        return str(self) + f"\n{type(self)}"

    def __str__(self) -> str:
        string = f"{pprint.pformat(self._to_dict())}"
        string += f"\nSource: {self._options_source}" if self._options_source else ""
        return string


options = ConfigOptions()


def resolve_config_option(config_option: str, value: Optional[str]):
    if value is None:
        return getattr(options, config_option)
    else:
        return value
