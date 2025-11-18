"""This module contains the CLI entrypoint."""

import sys
from pathlib import Path

import typer

from pyrig import main as pyrig_main
from pyrig.dev.cli import subcommands
from pyrig.dev.configs.base.base import ConfigFile
from pyrig.dev.configs.pyproject import PyprojectConfigFile
from pyrig.src.modules.function import get_all_functions_from_module
from pyrig.src.modules.module import import_module_from_path

app = typer.Typer()


def add_subcommands() -> None:
    """Add subcommands to the CLI."""
    # extract project name from sys.argv[0]
    project_name = Path(sys.argv[0]).name
    pkg_name = PyprojectConfigFile.get_pkg_name_from_project_name(project_name)

    main_module_name = PyprojectConfigFile.get_module_name_replacing_start_module(
        pyrig_main, pkg_name
    )
    main_module = import_module_from_path(main_module_name)
    app.command()(main_module.main)

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
