from importlib.metadata import version

import esparto


def test_package_version():
    assert esparto.__version__ == version("esparto")
