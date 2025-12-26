"""Shared CLI commands available across all pyrig-based projects.

This module defines CLI commands that are automatically available in all
projects that depend on pyrig. These commands are discovered through pyrig's
multi-package architecture and added to each project's CLI.

The shared commands system works by:
1. pyrig discovers all packages that depend on it
2. For each package, it looks for a `shared_subcommands` module
3. All functions in these modules are registered as CLI commands
4. Each project gets its own version of the command with project-specific behavior

This enables creating commands that work consistently across an ecosystem of
related packages while adapting to each project's context.

Commands:
    - `version`: Display the project's version information

Example:
    When you run `uv run myproject version`, it displays::

        myproject version 1.2.3

    The same command works for any pyrig-based project::

        uv run pyrig version
        # Output: pyrig version 3.1.5

Note:
    To add shared commands to your own pyrig-based package, create a
    `myproject/dev/cli/shared_subcommands.py` module with public functions.
    These will be automatically discovered and added to all projects that
    depend on your package.
"""

from importlib.metadata import version as get_version

import typer

from pyrig.src.cli import get_project_name_from_argv


def version() -> None:
    """Display the project's version information.

    Retrieves and displays the version of the current project from its
    installed package metadata. The version is read from the project's
    `pyproject.toml` via `importlib.metadata`.

    Example:
        >>> uv run myproject version
        myproject version 1.2.3

    Note:
        The project name is automatically determined from the command being
        executed (e.g., `myproject` from `uv run myproject version`).
    """
    project_name = get_project_name_from_argv()
    typer.echo(f"{project_name} version {get_version(project_name)}")
