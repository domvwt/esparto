import argparse
from pathlib import Path

import pytest

import esparto._cli as cli
import esparto._options as opt

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

    @cli.subcommand(cli.argument("--message"), parent=subparsers)
    def my_subcommand(args):
        return args.message

    args = parser.parse_args(["my_subcommand", "--message", "test"])
    assert args.func(args) == "test"


def test_print_esparto_css(capsys):
    cli.print_esparto_css()
    captured = capsys.readouterr()
    expected = Path(opt.OutputOptions.esparto_css).read_text().strip()
    assert captured.out.strip() == expected


def test_print_bootstrap_css(capsys):
    cli.print_bootstrap_css()
    captured = capsys.readouterr()
    expected = Path(opt.OutputOptions.bootstrap_css).read_text().strip()
    assert captured.out.strip() == expected


def test_print_jinja_template(capsys):
    cli.print_jinja_template()
    captured = capsys.readouterr()
    expected = Path(opt.OutputOptions.jinja_template).read_text().strip()
    assert captured.out.strip() == expected


def test_print_default_options(capsys):
    cli.print_default_options()
    captured = capsys.readouterr()
    expected = opt.OutputOptions()._to_yaml_str().strip()
    assert captured.out.strip() == expected
