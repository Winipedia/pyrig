"""Project-specific CLI commands.

Add custom CLI commands here as public functions. All public functions are
automatically discovered and registered as CLI commands.
"""

import typer


def mkroot() -> None:
    """Create or update project configuration files and directory structure.

    Discovers all ConfigFile subclasses across the project and its dependencies,
    then validates each one to create or update configuration files. Generates
    the complete project structure including pyproject.toml, .gitignore, GitHub
    workflows, prek hooks, and other configuration files.

    The command is idempotent: safe to run multiple times, overwrites incorrect
    files but respects opt-out markers.

    Example:
        $ uv run pyrig mkroot

    """
    # local imports in pyrig to avoid cli failure when installing without dev deps
    # as some pyrig commands are dependend on dev deps and can only be used in a dev env
    from pyrig.rig.cli.commands.create_root import make_project_root  # noqa: PLC0415

    make_project_root()


def mktests() -> None:
    """Generate test skeleton files for all source code.

    Creates test files mirroring the source package structure. For each module,
    class, function, and method in the source code, generates corresponding test
    skeletons with `NotImplementedError` placeholders.

    Naming Conventions:
        - Test modules: `test_<module_name>.py`
        - Test classes: `Test<ClassName>`
        - Test functions: `test_<function_name>`
        - Test methods: `test_<method_name>`

    The command is idempotent and non-destructive: safe to run multiple times,
    only adds new test skeletons for untested code, preserves all existing tests.
    Uses parallel execution for performance.

    Example:
        $ uv run pyrig mktests

    Note:
        Generated test functions raise `NotImplementedError` and must be
        implemented. Test skeletons include minimal docstrings.
    """
    from pyrig.rig.cli.commands.create_tests import create_tests  # noqa: PLC0415

    create_tests()


def mkinits() -> None:
    """Create missing __init__.py files for all namespace packages.

    Scans the project for namespace packages (directories with Python files but
    no __init__.py) and creates minimal __init__.py files for them. Ensures all
    packages follow traditional Python package conventions and are properly
    importable.

    The command is idempotent and non-destructive: safe to run multiple times,
    only creates missing files, never modifies existing ones. Uses parallel
    execution for performance.

    Example:
        $ uv run pyrig mkinits

    Note:
        The `docs` directory is excluded from scanning. Created __init__.py
        files contain a minimal docstring.
    """
    from pyrig.rig.cli.commands.make_inits import make_init_files  # noqa: PLC0415

    make_init_files()


def init() -> None:
    """Initialize a complete pyrig project from scratch.

    Transforms a basic Python project into a fully-configured, production-ready
    pyrig project through a comprehensive automated sequence.

    The initialization steps execute in the following order:
        - Initialize version control (git init)
        - Add development dependencies (uv add --group dev)
        - Sync virtual environment (uv sync)
        - Create project root (mkroot)
        - Sync virtual environment again (apply new configs)
        - Generate test skeletons (mktests)
        - Install prek hooks (prek install)
        - Add all files to version control (git add .)
        - Run prek hooks (format/lint all files)
        - Run test suite (pytest)
        - Create initial git commit

    The process is automated and logged. Each step executes sequentially; if any
    step fails, the process stops immediately.

    Example:
        $ cd my-project
        $ uv init
        $ uv add pyrig
        $ uv run pyrig init

    Note:
        Run once when setting up a new project. Individual steps are idempotent,
        but the full sequence is designed for initial setup.
    """
    from pyrig.rig.cli.commands.init_project import init_project  # noqa: PLC0415

    init_project()


def build() -> None:
    """Build all distributable artifacts for the project.

    Discovers and invokes all BuilderConfigFile subclasses across the project and
    its dependencies to create distributable artifacts (e.g., PyInstaller
    executables, documentation archives, custom build processes).

    Build Process:
        1. Discovers all non-abstract BuilderConfigFile subclasses
        2. Validates each builder (triggers build via ``dump()``)
        3. Creates artifacts in temporary directories
        4. Renames with platform-specific suffixes (e.g., ``-Linux``, ``-Windows``)
        5. Moves artifacts to ``dist/`` directory

    Builders within the same priority group execute in parallel. Priority groups
    are processed sequentially (highest first).

    Example:
        $ uv run pyrig build

    Note:
        Artifacts are placed in ``dist/`` by default. Platform-specific naming
        uses ``platform.system()``. Only non-abstract BuilderConfigFile subclasses
        are executed.
    """
    from pyrig.rig.cli.commands.build_artifacts import build_artifacts  # noqa: PLC0415

    build_artifacts()


def protect_repo() -> None:
    """Configure GitHub repository protection rules and security settings.

    Applies comprehensive security protections to the GitHub repository,
    including repository-level settings and branch protection rulesets. Enforces
    pyrig's opinionated security defaults to maintain code quality and prevent
    accidental destructive operations.

    Repository Settings:
        - Description from pyproject.toml
        - Default branch set to 'main'
        - Delete branches on merge enabled
        - Merge commits disabled (squash and rebase only)

    Branch Protection Rules:
        - Required pull request reviews with code owner approval
        - Required status checks (health check workflow must pass)
        - Linear commit history required
        - Signed commits required
        - Force pushes and branch deletions disabled

    Protection rules are loaded from `branch-protection.json` and can be
    customized for your project.

    Example:
        $ uv run pyrig protect-repo

    Note:
        Requires `REPO_TOKEN` environment variable with `repo` scope permissions.
        Idempotent: safe to run multiple times, updates existing rulesets.

    Raises:
        ValueError: If REPO_TOKEN is not found in environment or .env file.
    """
    from pyrig.rig.cli.commands.protect_repo import protect_repository  # noqa: PLC0415

    protect_repository()


def scratch() -> None:
    """Execute the .scratch file for temporary, ad-hoc code.

    The .scratch file is a Python script located at the project root, intended
    for temporary, experimental code that doesn't belong in the main source
    files. This command checks for the existence of .scratch and executes it in
    a clean namespace.

    Example usage:
        $ uv run pyrig scratch

    Note:
        The .scratch file is not tracked by version control and should be used
        for one-off scripts, debugging, or experimental code related to the
        project.
    """
    from pyrig.rig.cli.commands.scratch import run_scratch_file  # noqa: PLC0415

    run_scratch_file()


def rmpyc() -> None:
    """Remove all __pycache__ directories and their contents from the project.

    This command recursively searches the project directory for any __pycache__
    directories and deletes them along with their contents. Useful for cleaning up
    compiled Python files that may be causing issues or taking up unnecessary
    space.

    Example usage:
        $ uv run pyrig rmpyc
    Note:
        Use with caution, as this will permanently delete all __pycache__ directories
        and their contents. Safe to run multiple times, as it only targets existing
        __pycache__ directories.
    """
    from pyrig.rig.cli.commands.remove_pycache import remove_pycache  # noqa: PLC0415

    remove_pycache()


def mkcmd(
    name: str = typer.Argument(help="Name of the command to create."),
    *,
    shared: bool = typer.Option(
        default=False,
        help="Whether the command should be shared in subsequent projects.",
    ),
) -> None:
    """Create a new CLI subcommand scaffold.

    This will create the subcommands.py file under the rig package
    if it doesn't exist yet, and add a new function with the given name

    Args:
        name: Name of the command to generate.
        shared: Whether to add the command to the shared subcommands module.
    """
    from pyrig.rig.cli.commands.make_subcommand import make_subcommand  # noqa: PLC0415

    make_subcommand(name, shared=shared)


def subcls(
    import_path: str | None = typer.Argument(
        default=None,
        help="""The dotted import path to the class to subclass (e.g., 'package.module.ClassName').
If not given, you can search and choose the class in an interactive session.""",  # noqa: E501
    ),
) -> None:
    """Create a subclass scaffold for a class specified by import path.

    Args:
        import_path: Optional dotted import path to the class to subclass. If
            omitted, an interactive selector is used.
    """
    from pyrig.rig.cli.commands.make_subclass import make_subclass  # noqa: PLC0415

    make_subclass(import_path)


def mkfixture(
    name: str = typer.Argument(help="Name of the fixture to create."),
) -> None:
    """Create a new pytest fixture scaffold.

    This command creates a new pytest fixture function in the fixtures module.

    Args:
        name: Name of the fixture to generate.
    """
    from pyrig.rig.cli.commands.make_fixture import make_fixture  # noqa: PLC0415

    make_fixture(name)


def resources() -> None:
    """Scaffolds the resources package for the project."""
    from pyrig.rig.cli.commands.make_resources import make_resources  # noqa: PLC0415

    make_resources()
