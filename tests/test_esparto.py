import sys

import esparto


def test_package_version():
    if sys.version > "3.7":
        from importlib.metadata import version

        assert esparto.__version__ == version("esparto")
    else:
        assert True
