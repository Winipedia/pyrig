"""Project-specific CLI commands.

Functions defined directly in this module are discovered and registered as
top-level CLI commands. Module-level `typer.Typer` instances are registered
as command groups, with each group named after the kebab-case form of its
variable name.
"""

from pathlib import Path
from typing import Annotated

import typer

from pyrig.rig.cli import make, remove

mk = make.app
rm = remove.app


def init() -> None:
    """Initialize a new project from scratch.

    Runs pyrig's full project-setup sequence, taking a bare directory to a
    production-ready project in one command.

    Example:
        ```
        $ cd my-project
        $ uv init
        $ uv add pyrig
        $ uv run pyrig init
        ```

    Note:
        Intended to be run once, right after creating the project — not as
        part of routine development. Stops at the first step that fails.
    """
    from pyrig.rig.cli.commands.init_project import init_project  # noqa: PLC0415

    init_project()


def scratch() -> None:
    """Run the `.scratch.py` file at the project root as `__main__`.

    `.scratch.py` is a throwaway script kept at the project root for local
    experimentation, excluded from version control and never committed. Use
    it to prototype ideas, test quick snippets, or exercise library code
    without touching the main source tree.
    """
    from pyrig.rig.cli.commands.scratch import run_scratch_file  # noqa: PLC0415

    run_scratch_file()


def sync(
    files: Annotated[
        list[Path] | None,
        typer.Argument(
            help="Files to synchronize. If omitted, all files are synchronized.",
        ),
    ] = None,
) -> None:
    """Reconcile all pyrig-managed project structure into its correct state.

    Safe to run repeatedly: existing user content is preserved, and only what
    is missing or incorrect is changed. Run it after adding source code,
    pulling changes, or adding a new pyrig dependency.

    Args:
        files: Files to synchronize. If omitted, all files are
            synchronized.

    Raises:
        typer.Exit: With code 1 if any file was created or updated.

    Note:
        Suitable as a git hook: fixes are applied and the command exits
        non-zero so the hook blocks until the developer stages the changes
        and recommits. Only relative paths are supported in `files`;
        absolute paths are silently dropped.
    """
    from pyrig.rig.cli.commands.synchronize import synchronize_project  # noqa: PLC0415

    synchronize_project(files)
