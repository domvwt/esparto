from pathlib import Path

import esparto as es


def check_package_version():
    pyproject_file = Path("pyproject.toml").read_text()
    pyproject_version = pyproject_file.split("version", 1)[1].split('"')[1]
    module_version = es.__version__

    if module_version == pyproject_version:
        print("Version number up to date!")
        exit(0)
    else:
        print("Please bump version number!")
        print("pyproject.toml:", pyproject_version)
        print("esparto.__version__:", module_version)
        exit(1)


if __name__ == "__main__":
    check_package_version()
