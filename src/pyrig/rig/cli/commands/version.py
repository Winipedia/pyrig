"""Contains the command to echo the version of a project."""

from importlib.metadata import version

import typer

from pyrig.core.cli import project_name_from_argv


def project_version() -> None:
    """Display the current project's version.

    Retrieves and displays the version of the project being run (not pyrig's
    version) from installed package metadata.

    The project name is automatically determined from `sys.argv[0]`, enabling
    this command to work in any pyrig-based project without modification.

    Note:
        The package must be installed (even in editable mode) for version
        retrieval to work.
    """
    project_name = project_name_from_argv()
    typer.echo(f"{project_name} version {version(project_name)}")
