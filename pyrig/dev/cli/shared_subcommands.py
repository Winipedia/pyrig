"""Shared CLI commands available across all pyrig-based projects.

Defines CLI commands that are automatically available in all projects that
depend on pyrig, with project-specific behavior through dynamic discovery.

The shared commands system enables creating commands that work consistently
across an ecosystem of related packages while adapting to each project's
context. For example, the `version` command displays the version of the
project being run, not pyrig's version.

Discovery Mechanism:
    The discovery process (in `pyrig.dev.cli.cli.add_shared_subcommands`):
    1. Extracts package name from `sys.argv[0]`
    2. Builds dependency chain from pyrig to current package
    3. Finds `dev.cli.shared_subcommands` modules in each package
    4. Extracts and registers all public functions as commands

    This enables intermediate packages to define shared commands that are
    automatically available in all dependent projects.

Extensibility:
    To add shared commands to your pyrig-based package, create
    `<package>/dev/cli/shared_subcommands.py` with public functions.

Example:
    Running the version command::

        $ uv run pyrig version
        pyrig version 3.1.5

        $ uv run myproject version
        myproject version 1.2.3

Note:
    - Commands are registered in dependency order (pyrig first)
    - Later registrations override earlier ones with the same name
    - Use `get_project_name_from_argv()` to make commands project-aware
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
