"""Version display command for pyrig-based project CLIs."""

from importlib.metadata import version

import typer

from pyrig.rig.cli.cli.cli import CLI


def project_version() -> None:
    """Print the installed version of the invoking project.

    Prints the version of whichever project's CLI entry point was used to
    invoke this command, not pyrig's own version. The project must be installed
    (an editable install is sufficient) for the metadata lookup to succeed.
    """
    project_name = CLI.I.project_name()
    typer.echo(f"{project_name} {version(project_name)}")
