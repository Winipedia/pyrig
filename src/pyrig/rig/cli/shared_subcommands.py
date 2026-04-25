"""Shared CLI commands available across all dependent projects.

Every public function defined here is automatically discovered and registered
as a CLI command in all projects that depend on this project.
"""


def version() -> None:
    """Display the installed version of the project.

    Echos the project name and version to the console.

    Example:
        $ uv run pyrig version
        pyrig version 1.2.3

        $ uv run myproject version
        myproject version 1.2.3
    """
    from pyrig.rig.cli.commands.version import project_version  # noqa: PLC0415

    project_version()
