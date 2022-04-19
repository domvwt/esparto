"""Command line utilities for esparto."""

from argparse import SUPPRESS, ArgumentParser, _SubParsersAction
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple

import esparto._options as opt
from esparto import __version__

PROG = "esparto"
DESCRIPTION = "Command line utilities for esparto."
EPILOG = "Run program with no arguments for subcommand help."

parser = ArgumentParser(prog=PROG, usage=None, description=DESCRIPTION, epilog=EPILOG)
subparsers = parser.add_subparsers(dest="subcommand")

parser.add_argument("-v", "--version", action="version", version=__version__)


CliArg = Tuple[List[str], Dict[str, Any]]


def argument(*name_or_flags: str, **kwargs: Dict[str, Any]) -> CliArg:
    """Convenience function to properly format arguments to pass to the
    subcommand decorator.
    """
    return (list(name_or_flags), kwargs)


def subcommand(
    *subparser_args: CliArg, parent: _SubParsersAction = subparsers
) -> Callable[..., Any]:
    """Decorator to define a new subcommand in a sanity-preserving way.
    The function will be stored in the ``func`` variable when the parser
    parses arguments so that it can be called directly like so::
        args = cli.parse_args()
        args.func(args)
    Usage example::
        @subcommand([argument("-d", help="Enable debug mode", action="store_true")])
        def subcommand(args):
            print(args)
    Then on the command line::
        $ python cli.py subcommand -d
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        parser_ = parent.add_parser(
            func.__name__, description=func.__doc__, add_help=False, usage=SUPPRESS
        )
        for args, kwargs in subparser_args:
            parser_.add_argument(*args, **kwargs)
        parser_.set_defaults(func=func)
        return func

    return decorator


@subcommand()
def print_esparto_css(*args: Any) -> None:
    """print default esparto CSS"""
    css = Path(opt.OutputOptions.esparto_css).read_text()
    print(css)


@subcommand()
def print_bootstrap_css(*args: Any) -> None:
    """print default Bootstrap CSS"""
    css = Path(opt.OutputOptions.bootstrap_css).read_text()
    print(css)


@subcommand()
def print_jinja_template(*args: Any) -> None:
    """print default jinja template"""
    css = Path(opt.OutputOptions.jinja_template).read_text()
    print(css)


@subcommand()
def print_default_options(*args: Any) -> None:
    """print default output options"""
    print(opt.OutputOptions()._to_yaml_str())


def print_subcommand_help() -> None:
    """Print help for subcommands."""
    subparser_actions = [
        action for action in parser._actions if isinstance(action, _SubParsersAction)
    ]
    print("subcommands:")
    for subparsers_action in subparser_actions:
        left_pad_size = max(len(x) for x in subparsers_action.choices.keys()) + 2
        left_pad_size = max(left_pad_size, 22)
        for choice, subparser in subparsers_action.choices.items():
            print(f"  {choice:<{left_pad_size}}{subparser.format_help().strip()}")


def main() -> None:
    args = parser.parse_args()
    if args.subcommand is None:
        parser.print_help()
        print()
        print_subcommand_help()
    else:
        args.func(args)
