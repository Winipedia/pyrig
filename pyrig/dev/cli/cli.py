"""CLI entry point and command registration.

This module provides the main CLI entry point for pyrig projects. It uses
Typer to build a command-line interface and automatically discovers
subcommands from the project's subcommands module.

The CLI supports both pyrig's built-in commands and project-specific
commands defined in the consuming project's subcommands module.

Example:
    $ uv run pyrig init
    $ uv run pyrig create-root
    $ uv run pyrig build
"""

import sys
from importlib.metadata import version as get_version
from pathlib import Path

import typer

from pyrig import main as pyrig_main
from pyrig.dev.cli import subcommands
from pyrig.src.modules.function import get_all_functions_from_module
from pyrig.src.modules.module import (
    get_module_name_replacing_start_module,
    import_module_from_path,
)
from pyrig.src.modules.package import (
    get_pkg_name_from_project_name,
)

app = typer.Typer(no_args_is_help=True)
"""The main Typer application instance."""


def get_project_name_from_argv() -> str:
    """Get the project name."""
    return Path(sys.argv[0]).name


def get_pkg_name_from_argv() -> str:
    """Get the project and package name."""
    project_name = get_project_name_from_argv()
    return get_pkg_name_from_project_name(project_name)


def add_subcommands() -> None:
    """Discover and register all CLI subcommands.

    Dynamically loads the main module and subcommands module for the
    current project, registering all public functions as CLI commands.
    This enables projects depending on pyrig to define their own commands.
    """
    # extract project name from sys.argv[0]
    pkg_name = get_pkg_name_from_argv()

    main_module_name = get_module_name_replacing_start_module(pyrig_main, pkg_name)
    main_module = import_module_from_path(main_module_name)
    app.command()(main_module.main)

    # replace the first parent with pkg_name
    subcommands_module_name = get_module_name_replacing_start_module(
        subcommands, pkg_name
    )

    subcommands_module = import_module_from_path(subcommands_module_name)

    sub_cmds = get_all_functions_from_module(subcommands_module)

    for sub_cmd in sub_cmds:
        app.command()(sub_cmd)


@app.command()
def version() -> None:
    """Display the version information."""
    project_name = get_project_name_from_argv()
    typer.echo(f"{project_name} version {get_version(project_name)}")


def main() -> None:
    """Entry point for the CLI.

    Registers all subcommands and invokes the Typer application.
    This function is called by the console script entry point.
    """
    add_subcommands()
    app()
