"""Shared CLI commands available across all dependent projects.

Every public function defined here is automatically discovered and registered
as a CLI command in all projects that depend on this project.
"""


def version() -> None:
    """Print the installed version of the invoking project.

    Reads the version from installed package metadata and prints it to the
    console. The project name is derived from sys.argv[0], so this command
    always reports the version of whichever project's CLI entry point was
    used to invoke it — not pyrig's own version.

    The project must be installed (an editable install is sufficient) for
    the metadata lookup to succeed.

    Examples:
        $ uv run pyrig version
        pyrig version 1.2.3

        $ uv run myproject version
        myproject version 0.4.1
    """
    from pyrig.rig.cli.commands.version import project_version  # noqa: PLC0415

    project_version()
