"""This module contains the CLI entrypoint."""

import sys
from pathlib import Path

import typer

from py_dev.dev.cli import subcommands
from py_dev.dev.configs.base.base import ConfigFile
from py_dev.dev.configs.pyproject import PyprojectConfigFile
from py_dev.utils.modules.function import get_all_functions_from_module
from py_dev.utils.modules.module import import_module_from_path

app = typer.Typer()


def add_subcommands() -> None:
    """Add subcommands to the CLI."""
    # extract project name from sys.argv[0]
    project_name = Path(sys.argv[0]).name

    pkg_name = PyprojectConfigFile.get_pkg_name_from_project_name(project_name)

    # replace the first parent with pkg_name
    subcommands_module_name = ConfigFile.get_module_name_replacing_start_module(
        subcommands, pkg_name
    )

    subcommands_module = import_module_from_path(subcommands_module_name)

    sub_cmds = get_all_functions_from_module(subcommands_module)

    for sub_cmd in sub_cmds:
        app.command()(sub_cmd)


def main() -> None:
    """Entry point for the CLI."""
    add_subcommands()
    app()
