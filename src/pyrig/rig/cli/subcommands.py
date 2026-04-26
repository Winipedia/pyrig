"""Project-specific CLI commands.

All functions in this module are automatically discovered and registered
as CLI commands for this project.
"""

import typer


def init() -> None:
    """Initialize a new project from scratch.

    Runs the full setup sequence — one command to go from installing pyrig to a
    fully-configured, production-ready project with version control, dependencies,
    configs, test skeletons, pre-commit hooks, and an initial commit.

    Steps executed in order:

        1.  git init            (initialize version control)
        2.  uv add --group dev  (adds all pyrig dev dependencies)
        3.  uv sync             (install dev deps)
        4.  pyrig mkroot        (generate all config files and project structure)
        5.  uv sync             (re-install to apply updated pyproject.toml)
        6.  pyrig mktests       (generate test skeletons)
        7.  prek install        (install pre-commit hooks)
        8.  git add .           (stage all files for commit)
        9.  prek run            (format and lint all files)
        10. pytest              (run the test suite)
        11. git commit          (initial commit)

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


def mkroot() -> None:
    """Create or update all managed project configuration files.

    Discovers every concrete `ConfigFile` subclass registered in the project
    and its installed dependencies, then validates each one in priority order.
    Missing files are created (including parent directories); existing files are
    updated only when their content is not correct. User customisations are
    preserved wherever possible.

    Managed files are all concrete implemented as subclasses of `ConfigFile`
    across all installed projects that depend on pyrig.

    Idempotent: safe to run multiple times. Re-run after adding a new pyrig
    dependency to pick up the config files it contributes.

    Example:
        $ uv run pyrig mkroot
    """
    from pyrig.rig.cli.commands.make_root import make_project_root  # noqa: PLC0415

    make_project_root()


def mktests() -> None:
    """Generate mirror test skeletons for all source modules.

    Scans the project's source package and writes test files that mirror the
    source structure. For each module, class, function, and method that does
    not already have a test, a stub is added that raises `NotImplementedError`.

    Existing test implementations are never overwritten — only new stubs are
    added. This command is idempotent and safe to run multiple times.
    Run it after refactors, moving files around, or adding new source code to
    ensure all new code has corresponding tests.

    Example:
        $ uv run pyrig mktests
    """
    from pyrig.rig.cli.commands.make_tests import make_tests  # noqa: PLC0415

    make_tests()


def mkinits() -> None:
    """Create `__init__.py` files for all namespace packages in the project.

    Scans the src and tests package roots for any directories that do not yet contain an
    `__init__.py` file, then creates one with minimal content.
    Existing `__init__.py` files are left untouched; only missing ones are created.
    This command is idempotent and safe to run multiple times.

    Example:
        $ uv run pyrig mkinits
    """
    from pyrig.rig.cli.commands.make_inits import make_init_files  # noqa: PLC0415

    make_init_files()


def build() -> None:
    """Build all distributable artifacts defined in the builders package.

    Discovers every concrete `BuilderConfigFile` subclass under the `builders`
    package and runs each one through its full pipeline:

        1. Creates a temporary working directory
        2. Calls create_artifacts() to produce raw output files there
        3. Appends a platform suffix to each file
           (e.g., myapp-Linux, myapp-Darwin, myapp-Windows)
        4. Moves the renamed artifacts to dist/

    Builders are skipped when output already exists in dist/.
    Delete the existing dist/ artifacts if you want to rebuild them.

    Extend pyrig by subclassing `BuilderConfigFile` (for custom builds) or
    `PyInstallerBuilder` (for standalone executables) and placing the subclass
    inside your project's `builders` package.

    Example:
        $ uv run pyrig build
    """
    from pyrig.rig.cli.commands.build_artifacts import build_artifacts  # noqa: PLC0415

    build_artifacts()


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


def resources() -> None:
    """Scaffold the `resources` package for bundling static assets.

    Creates a `your-project/rig/resources/__init__.py` file.
    This is the conventional home for templates, data files, and other non-code assets
    bundled with the project. Resources are accessible at runtime via
    `resource_path()`.

    This command is idempotent and safe to run multiple times.
    If the file already exists, it is left untouched.

    Example:
        $ uv run pyrig resources
    """
    from pyrig.rig.cli.commands.make_resources_package import (  # noqa: PLC0415
        make_resources_package,
    )

    make_resources_package()


def mkcmd(
    name: str = typer.Argument(help="Name of the command to create."),
    *,
    shared: bool = typer.Option(
        default=False,
        help="Whether the command should be shared in subsequent projects.",
    ),
) -> None:
    """Create a new CLI subcommand stub for this project.

    Appends a minimal function stub to `rig/cli/subcommands.py`.
    The target module is created automatically if it does not yet exist.
    Kebab-case names are normalized to snake_case for the generated function name.

    Args:
        name: Name of the subcommand to create. Accepts kebab-case or snake_case.
        shared: If `True`, the stub is added to `rig/cli/shared_subcommands.py` instead,
            making it accessible to all projects that depend on this one.

    Examples:
        $ uv run pyrig mkcmd my-command
        $ uv run pyrig mkcmd my-command --shared
    """
    from pyrig.rig.cli.commands.make_subcommand import make_subcommand  # noqa: PLC0415

    make_subcommand(name, shared=shared)


def subcls() -> None:
    """Scaffold a subclass of any pyrig class interactively.

    Launches a fuzzy-search prompt listing all `RigDependencySubclass` leaf classes
    found in pyrig and its dependents — both concrete classes (shown with their string
    representation) and abstract classes (shown by qualified name), sorted
    alphabetically by import path.

    After you select a class, pyrig creates the matching module file in your
    project (or validates it if it already exists), copies the source module's
    docstring into it, and appends a ready-to-edit subclass skeleton that
    imports and extends the class you chose.

    Example:
        $ uv run pyrig subcls
    """
    from pyrig.rig.cli.commands.make_subclass import make_subclass  # noqa: PLC0415

    make_subclass()


def mkfixture(
    name: str = typer.Argument(help="Name of the fixture to create."),
) -> None:
    """Scaffold a new pytest fixture stub in the project's shared fixtures module.

    Appends an `@pytest.fixture`-decorated function stub to the shared fixtures
    module. The file is created if it does not already exist. If `import pytest`
    is not already present in the module, it is inserted automatically.

    The name is normalized from kebab-case to snake_case so it forms a valid
    Python identifier (e.g. `my-new-fixture` becomes `my_new_fixture`).

    Example:
        $ uv run pyrig mkfixture my-new-fixture
    """
    from pyrig.rig.cli.commands.make_fixture import make_fixture  # noqa: PLC0415

    make_fixture(name)


def scratch() -> None:
    """Run the .scratch.py file at the project root.

    .scratch.py is a throwaway Python script kept at the project root for
    local experimentation. It is automatically excluded from version control
    via .gitignore and never committed. Use it to prototype ideas, test quick
    snippets, or exercise library code without touching the main source tree.

    The file is executed with `runpy.run_path` in a fresh, isolated namespace
    so it has no side-effects on the calling environment.

    Example:
        $ uv run pyrig scratch
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

    Example:
        $ uv run pyrig rmpyc
    """
    from pyrig.rig.cli.commands.remove_pycache import remove_pycache  # noqa: PLC0415

    remove_pycache()
