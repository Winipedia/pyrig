"""Shared CLI commands available across all dependent projects.

All public functions are automatically discovered and registered as shared CLI commands.
This means that any function defined in this module becomes a CLI command that is
available in all dependent projects as a shared command.
"""


def version() -> None:
    """Display the current project's version.

    Retrieves and displays the version of the project being run (not pyrig's
    version) from installed package metadata.

    The project name is automatically determined from `sys.argv[0]`, enabling
    this command to work in any pyrig-based project without modification.

    Example:
        $ uv run pyrig version
        pyrig version 1.2.3

        $ uv run myproject version
        myproject version 1.2.3

    Note:
        The package must be installed (even in editable mode) for version
        retrieval to work.
    """
    from pyrig.rig.cli.commands.version import project_version  # noqa: PLC0415

    project_version()
