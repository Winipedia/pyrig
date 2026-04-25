"""Version display command for pyrig-based project CLIs."""

from importlib.metadata import version

import typer

from pyrig.core.cli import project_name_from_argv


def project_version() -> None:
    """Display the invoking project's version.

    Prints the version of the project whose CLI entry point was used to call
    this command, not pyrig's own version. The project name is derived from
    ``sys.argv[0]``, so this command adapts automatically to whichever
    pyrig-based project invokes it.

    The version is read from installed package metadata via
    ``importlib.metadata.version``. The project must be installed (editable
    installs are sufficient) for this to work.
    """
    project_name = project_name_from_argv()
    typer.echo(f"{project_name} version {version(project_name)}")
