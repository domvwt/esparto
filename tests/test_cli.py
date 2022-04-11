import argparse

import pytest

import esparto._cli as cli

arg_test_values = [
    (("--version", "-v"), {"verbose": True}, (["--version", "-v"], {"verbose": True})),
    (("positional_arg",), {}, (["positional_arg"], {})),
]


@pytest.mark.parametrize("name_or_flags,kwargs,expected", arg_test_values)
def test_argument(expected, name_or_flags, kwargs):
    output = cli.argument(*name_or_flags, **kwargs)
    assert output == expected


def test_subcommand():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="subcommand")

    @cli.subcommand(parent=subparsers)
    def my_subcommand():
        return "test"

    print(subparsers)
    assert False
