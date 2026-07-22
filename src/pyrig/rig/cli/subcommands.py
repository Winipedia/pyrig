"""Project-specific CLI commands.

Functions defined directly in this module are discovered and registered as
top-level CLI commands. Module-level `typer.Typer` instances are registered
as command groups, with each group named after the kebab-case form of its
variable name.
"""

from pathlib import Path
from typing import Annotated

import typer

from pyrig.rig.cli import make

mk = make.app


def init() -> None:
    """Initialize a new project from scratch.

    Runs the full ordered setup sequence — one command to go from installing
    pyrig to a production-ready project with version control, dependencies,
    configuration, test scaffolding, pre-commit hooks, and an initial commit.
    The process stops immediately if any step fails.

    Example:
        ```
        $ cd my-project
        $ uv init
        $ uv add pyrig
        $ uv run pyrig init
        ```
    """
    from pyrig.rig.cli.commands.init_project import init_project  # noqa: PLC0415

    init_project()


def rmpyc() -> None:
    """Remove all `__pycache__` directories from the project's source and test trees.

    Useful for clearing stale bytecode that may cause import errors or
    test-isolation issues after refactors, branch switches, or moving files
    around. Safe to run repeatedly.
    """
    from pyrig.rig.cli.commands.remove_pycache import remove_pycache  # noqa: PLC0415

    remove_pycache()


def scratch() -> None:
    """Run the `.scratch.py` file at the project root.

    `.scratch.py` is a throwaway Python script kept at the project root for
    local experimentation. It is automatically excluded from version control
    via `.gitignore` and never committed. Use it to prototype ideas, test
    quick snippets, or exercise library code without touching the main
    source tree.

    The script runs in an isolated namespace and does not affect the calling
    environment.

    It runs it as `__main__`.

    """
    from pyrig.rig.cli.commands.scratch import run_scratch_file  # noqa: PLC0415

    run_scratch_file()


def sync(
    files: Annotated[
        list[Path],
        typer.Argument(
            default_factory=list,
            help=(
                "Specific files to synchronize. If omitted, all files are synchronized."
            ),
        ),
    ],
) -> None:
    """Reconcile all pyrig-managed project structure into its correct state.

    Safe to run repeatedly: existing user content is preserved, and only what
    is missing or incorrect is changed. Run it after adding source code,
    pulling changes, or adding a new pyrig dependency.

    Args:
        files: Specific files to synchronize. If omitted, all files are
            synchronized.

    Exits with code 1 if any file was created or updated, 0 if everything was
    already in sync. This makes it suitable as a git hook: auto-fixes are
    applied, the hook fails, the developer stages the changes and recommits.
    """
    from pyrig.rig.cli.commands.synchronize import synchronize_project  # noqa: PLC0415

    synchronize_project(files)
