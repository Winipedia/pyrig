"""Project-specific CLI commands.

Add custom CLI commands here as public functions. All public functions are
automatically discovered and registered as CLI commands.
"""

import typer


def mkroot(
    *,
    priority: bool = typer.Option(
        default=False,
        help="Only create priority config files.",
    ),
) -> None:
    """Create or update project configuration files and directory structure.

    Discovers all ConfigFile subclasses across the project and its dependencies,
    then initializes each one to create or update configuration files. Generates
    the complete project structure including pyproject.toml, .gitignore, GitHub
    workflows, pre-commit hooks, and other configuration files.

    The command is idempotent: safe to run multiple times, overwrites incorrect
    files but respects opt-out markers.

    Args:
        priority: If True, only creates high-priority config files (e.g.,
            LICENSE, pyproject.toml). Used during `init` to create essential
            files before installing dependencies. Default: False.

    Example:
        $ uv run pyrig mkroot
        $ uv run pyrig mkroot --priority

    Note:
        Config files are created in parallel within each priority group for
        performance. The command is automatically called twice by `pyrig init`.
    """
    # local imports in pyrig to avoid cli failure when installing without dev deps
    # as some pyrig commands are dependend on dev deps and can only be used in a dev env
    from pyrig.dev.cli.commands.create_root import make_project_root  # noqa: PLC0415

    make_project_root(priority=priority)


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
    from pyrig.dev.cli.commands.create_tests import make_test_skeletons  # noqa: PLC0415

    make_test_skeletons()


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
    from pyrig.dev.cli.commands.make_inits import make_init_files  # noqa: PLC0415

    make_init_files()


def init() -> None:
    """Initialize a complete pyrig project from scratch.

    Transforms a basic Python project into a fully-configured, production-ready
    pyrig project through a comprehensive 9-step automated sequence.

    Initialization Steps:
        1. Add development dependencies (uv add --dev)
        2. Sync virtual environment (uv sync)
        3. Create priority config files (mkroot --priority)
        4. Sync virtual environment again
        5. Create complete project structure (mkroot)
        6. Generate test skeletons (mktests)
        7. Run pre-commit hooks (install, stage, format/lint)
        8. Run test suite (pytest)
        9. Create initial git commit

    The process is automated and logged. Each step executes sequentially; if any
    step fails, the process stops immediately.

    Example:
        $ git clone https://github.com/username/my-project.git
        $ cd my-project
        $ uv init
        $ uv add pyrig
        $ uv run pyrig init

    Note:
        Run once when setting up a new project. Requires a git repository to be
        initialized. Individual steps are idempotent, but the full sequence is
        designed for initial setup.
    """
    from pyrig.dev.cli.commands.init_project import init_project  # noqa: PLC0415

    init_project()


def build() -> None:
    """Build all distributable artifacts for the project.

    Discovers and invokes all BuilderConfigFile subclasses across the project and
    its dependencies to create distributable artifacts (e.g., PyInstaller
    executables, documentation archives, custom build processes).

    Build Process:
        1. Discovers all non-abstract BuilderConfigFile subclasses
        2. Instantiates each builder (triggers build via ``dump()``)
        3. Creates artifacts in temporary directories
        4. Renames with platform-specific suffixes (e.g., ``-Linux``, ``-Windows``)
        5. Moves artifacts to ``dist/`` directory

    Builders execute sequentially. Each builder runs independently; if one fails,
    others are not affected.

    Example:
        $ uv run pyrig build

    Note:
        Artifacts are placed in ``dist/`` by default. Platform-specific naming
        uses ``platform.system()``. Only leaf BuilderConfigFile classes are executed.
    """
    from pyrig.dev.cli.commands.build_artifacts import build_artifacts  # noqa: PLC0415

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
    from pyrig.dev.cli.commands.protect_repo import protect_repository  # noqa: PLC0415

    protect_repository()
