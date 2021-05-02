from dataclasses import dataclass


@dataclass
class ConfigOptions:
    offline_mode: bool = False
    _online_source: str = "cdn"
    _offline_source: str = "inline"


options = ConfigOptions()


def _get_source_from_options(mode):
    if mode == "esparto.options":
        if options.offline_mode:
            return options._offline_source
        else:
            return options._online_source
    elif mode in ["cdn", "inline"]:
        return mode
    else:
        raise ValueError(f"Unrecognised source: {mode}")
