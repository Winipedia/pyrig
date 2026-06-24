"""CLI commands shared across all pyrig-based projects.

Commands defined here are available in every project that depends on pyrig,
adapting their behavior to the invoking project at runtime.
"""


def version() -> None:
    """Print the installed version of the invoking project.

    Reports the version of whichever project's CLI entry point was used to
    invoke this command, not pyrig's own version. The project must be
    installed (an editable install is sufficient) for the metadata lookup
    to succeed.

    Example:
        ```
        $ uv run myproject version
        myproject 0.4.1
        ```
    """
    from pyrig.rig.cli.commands.version import project_version  # noqa: PLC0415

    project_version()
