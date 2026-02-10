"""Shared CLI commands available across all dependent projects.

All public functions are automatically discovered and registered as shared CLI commands.
This means that any function defined in this module becomes a CLI command that is
available in all dependent projects as a shared command.
"""

from importlib.metadata import version as get_version

import typer

from pyrig.src.cli import get_project_name_from_argv


def version() -> None:
    """Display the current project's version.

    Retrieves and displays the version of the project being run (not pyrig's
    version) from installed package metadata.

    The project name is automatically determined from `sys.argv[0]`, enabling
    this command to work in any pyrig-based project without modification.

    Example:
        $ uv run pyrig version
        pyrig version 3.1.5

        $ uv run myproject version
        myproject version 1.2.3

    Note:
        The package must be installed (even in editable mode) for version
        retrieval to work.
    """
    project_name = get_project_name_from_argv()
    typer.echo(f"{project_name} version {get_version(project_name)}")
