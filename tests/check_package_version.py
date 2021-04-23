import sys

import esparto


def check_package_version():
    if sys.version >= "3.8.0":
        from importlib.metadata import version

        if esparto.__version__ == version("esparto"):
            print("Version number up to date!")
        else:
            print("Please bump version number!")
    else:
        assert True


if __name__ == "__main__":
    check_package_version()
