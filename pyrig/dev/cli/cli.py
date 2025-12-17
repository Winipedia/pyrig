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

from importlib import import_module

import typer

import pyrig
from pyrig import main as pyrig_main
from pyrig.dev.cli import shared_subcommands, subcommands
from pyrig.dev.utils.cli import get_pkg_name_from_argv
from pyrig.src.modules.function import get_all_functions_from_module
from pyrig.src.modules.module import (
    get_module_name_replacing_start_module,
    get_same_modules_from_deps_depen_on_dep,
    import_module_from_file,
)

app = typer.Typer(no_args_is_help=True)
"""The main Typer application instance."""


def add_subcommands() -> None:
    """Discover and register all CLI subcommands.

    Dynamically loads the main module and subcommands module for the
    current project, registering all public functions as CLI commands.
    This enables projects depending on pyrig to define their own commands.
    """
    # extract project name from sys.argv[0]
    pkg_name = get_pkg_name_from_argv()

    main_module_name = get_module_name_replacing_start_module(pyrig_main, pkg_name)
    main_module = import_module_from_file(main_module_name)
    app.command()(main_module.main)

    # replace the first parent with pkg_name
    subcommands_module_name = get_module_name_replacing_start_module(
        subcommands, pkg_name
    )

    subcommands_module = import_module_from_file(subcommands_module_name)

    sub_cmds = get_all_functions_from_module(subcommands_module)

    for sub_cmd in sub_cmds:
        app.command()(sub_cmd)


def add_shared_subcommands() -> None:
    """Discover and register all shared CLI subcommands.

    This discovers all packages inheriting from pyrig and loads their
    shared_subcommands modules, registering all public functions as CLI
    commands. This enables cross-package commands that are available
    in all pyrig projects. Example is pyrigs version command that is
    available in all pyrig projects.
    So you can do:
        uv run pyrig version -> pyrig version 0.1.0
        uv run my-awesome-project version -> my-awesome-project version 0.1.0
    """
    package_name = get_pkg_name_from_argv()
    package = import_module(package_name)
    all_shared_subcommands_modules = get_same_modules_from_deps_depen_on_dep(
        shared_subcommands,
        pyrig,
        until_pkg=package,
    )
    for shared_subcommands_module in all_shared_subcommands_modules:
        sub_cmds = get_all_functions_from_module(shared_subcommands_module)
        for sub_cmd in sub_cmds:
            app.command()(sub_cmd)


def main() -> None:
    """Entry point for the CLI.

    Registers all subcommands and invokes the Typer application.
    This function is called by the console script entry point.
    """
    add_subcommands()
    add_shared_subcommands()
    app()
