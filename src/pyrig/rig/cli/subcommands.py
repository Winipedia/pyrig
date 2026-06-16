"""Project-specific CLI commands.

All functions in this module are automatically discovered and registered
as CLI commands for this project. Module-level ``typer.Typer`` instances are
registered as command groups named after their variable (e.g. the ``mk`` group,
invoked as ``pyrig mk <command>``).
"""

# Bind the make module's Typer app to ``mk`` so the CLI discovery registers it
# as the ``mk`` command group; importing the module also registers the group's
# sub-commands. Import the module (not the app instance) so only ``mk`` is a
# Typer in this namespace and the discovery registers exactly one group.
from pyrig.rig.cli import make

mk = make.app


def init() -> None:
    """Initialize a new project from scratch.

    Runs the full setup sequence — one command to go from installing pyrig to a
    fully-configured, production-ready project with version control, dependencies,
    configs, test skeletons, pre-commit hooks, and an initial commit.

    Steps executed in order:

        1.  git init            (initialize version control)
        2.  uv add --group dev  (adds all tool dev dependencies)
        3.  uv sync             (install all dependencies)
        4.  pyrig sync          (generate config files, inits, and test skeletons)
        5.  uv sync             (re-install to apply updated pyproject.toml)
        6.  prek install        (install pre-commit hooks)
        7.  git add .           (stage all files for commit)
        8.  git commit          (initial commit)

    Each step runs sequentially and is tracked with a progress bar.
    The process stops immediately if any step fails.

    Example:
        $ cd my-project
        $ uv init
        $ uv add pyrig
        $ uv run pyrig init
    """
    from pyrig.rig.cli.commands.init_project import init_project  # noqa: PLC0415

    init_project()


def sync() -> None:
    """Reconcile all pyrig-managed project structure into its correct state.

    Runs the three idempotent structural fixups in order, bringing the project
    into the exact state pyrig's autouse conformance checks require:

        1. Create any missing `__init__.py` files, so every directory is a
           proper package (satisfies the `no_namespace_packages` check).
        2. Create or update every managed `ConfigFile` — discovered across the
           project and its installed pyrig dependencies and validated in
           priority order (satisfies the `all_config_files_correct` check).
        3. Generate mirror test skeletons for all source modules, adding
           `NotImplementedError` stubs for any untested function, class, or
           method (satisfies the `all_modules_tested` check).

    Every step preserves existing user content and only adds what is missing or
    corrects what is wrong, so this command is idempotent and safe to run
    repeatedly. Run it after adding source code, pulling changes, or adding a
    new pyrig dependency to bring the project back into a fully conformant state.
    """
    from pyrig.rig.cli.commands.synchronize import synchronize_project  # noqa: PLC0415

    synchronize_project()


def protect_repo() -> None:
    """Apply GitHub repository settings and branch protection rulesets.

    Configures your GitHub repository with pyrig's opinionated security
    defaults, then creates or updates branch protection rulesets on the
    default branch.

    Repository settings applied:
        - Description synced from pyproject.toml
        - Default branch set to main
        - Branches deleted automatically after merge
        - Merge commits disabled (squash and rebase merges only)
        - Branch updates allowed

    Branch protection rules applied (read from branch-protection.json):
        - Pull request reviews required, including code owner approval
        - Status checks required (health check workflow must pass)
        - Linear commit history enforced
        - Signed commits required
        - Force pushes and branch deletions disabled

    Idempotent: safe to run multiple times; existing rulesets are updated
    in place.

    Requires REPO_TOKEN with repo scope — set as an environment variable
    or in your .env file (never commit your token).

    Examples:
        $ REPO_TOKEN=ghp_... uv run pyrig protect-repo
        $ uv run pyrig protect-repo  # with REPO_TOKEN already in .env

    Note:
        Despite being able to run this locally, the command is mainly intended
        for use in CI/CD workflows, where it can be used to automatically apply
        repository settings and branch protection rules.
    """
    from pyrig.rig.cli.commands.protect_repo import protect_repository  # noqa: PLC0415

    protect_repository()


def scratch() -> None:
    """Run the .scratch.py file at the project root.

    .scratch.py is a throwaway Python script kept at the project root for
    local experimentation. It is automatically excluded from version control
    via .gitignore and never committed. Use it to prototype ideas, test quick
    snippets, or exercise library code without touching the main source tree.

    The file is executed with `runpy.run_path` in a fresh, isolated namespace
    so it has no side-effects on the calling environment.
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
