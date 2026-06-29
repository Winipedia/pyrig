"""Project-specific CLI commands.

All functions in this module are automatically discovered and registered
as CLI commands for this project. Module-level `typer.Typer` instances are
registered as command groups named after their variable.
"""

# Bind the make module's Typer app to `mk` so the CLI discovery registers it
# as the `mk` command group; importing the module also registers the group's
# sub-commands. Import the module (not the app instance) so only `mk` is a
# Typer in this namespace and the discovery registers exactly one group.
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


def sync() -> None:
    """Reconcile all pyrig-managed project structure into its correct state.

    Runs the ordered structural fixups that create missing package files,
    update managed configuration, and refresh generated test scaffolding.
    Every fixup preserves existing user content and only adds what is missing
    or corrects what is wrong, making this command safe to run repeatedly.
    Run it after adding source code, pulling changes, or adding a new pyrig
    dependency to bring the project back into a fully conformant state.

    Exits with code 1 if any file was created or updated, 0 if everything was
    already in sync. This makes it suitable as a git hook: auto-fixes are
    applied, the hook fails, the developer stages the changes and recommits.
    """
    from pyrig.rig.cli.commands.synchronize import synchronize_project  # noqa: PLC0415

    synchronize_project()


def scratch() -> None:
    """Run the .scratch.py file at the project root.

    .scratch.py is a throwaway Python script kept at the project root for
    local experimentation. It is automatically excluded from version control
    via .gitignore and never committed. Use it to prototype ideas, test quick
    snippets, or exercise library code without touching the main source tree.

    The script runs in an isolated namespace and does not affect the calling
    environment.
    """
    from pyrig.rig.cli.commands.scratch import run_scratch_file  # noqa: PLC0415

    run_scratch_file()


def rmpyc() -> None:
    """Remove all `__pycache__` directories from the project's source and test trees.

    Recursively scans the package root and tests package root, printing each
    path before deleting it. Useful for clearing stale bytecode that may cause
    import errors or test-isolation issues after refactors, branch switches, or
    moving files around.

    Safe to run multiple times — only directories that currently exist are
    removed.
    """
    from pyrig.rig.cli.commands.remove_pycache import remove_pycache  # noqa: PLC0415

    remove_pycache()
