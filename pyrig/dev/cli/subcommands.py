"""Project-specific CLI subcommands for pyrig.

This module defines the main CLI commands for pyrig projects. All public
functions in this module are automatically discovered and registered as
CLI commands by the pyrig CLI system.

The functions here are thin wrappers around implementation functions defined
elsewhere. This separation keeps the CLI interface clean while allowing
complex logic to be tested independently.

Commands:
    - `init`: Complete project initialization
    - `mkroot`: Create project structure and config files
    - `mktests`: Generate test skeletons
    - `mkinits`: Create __init__.py files
    - `build`: Build all artifacts
    - `protect_repo`: Configure GitHub repository protection

Note:
    When creating a project that depends on pyrig, you can create your own
    `subcommands.py` module with the same structure. Your commands will be
    automatically discovered and added to your project's CLI alongside pyrig's
    shared commands.

Example:
    In your project's `myproject/dev/cli/subcommands.py`::

        def deploy() -> None:
            '''Deploy the application to production.'''
            from myproject.deployment import deploy_app
            deploy_app()

    Then run: `uv run myproject deploy`
"""

import typer


def mkroot(
    *,
    priority: bool = typer.Option(
        default=False,
        help="Only create priority config files.",
    ),
) -> None:
    """Create the complete project structure and configuration files.

    Initializes all ConfigFile subclasses to generate the project's configuration
    files (pyproject.toml, .gitignore, GitHub workflows, etc.) and creates
    __init__.py files for packages where they are missing.

    This command is idempotent - it will not overwrite existing files, only add
    missing ones or update files that don't match the expected configuration.

    Args:
        priority: If True, only creates high-priority config files (those with
            priority > 0, such as pyproject.toml). This is useful during
            initialization when some configs depend on others being present first.

    Example:
        >>> # Create all config files
        >>> uv run pyrig mkroot

        >>> # Create only priority config files
        >>> uv run pyrig mkroot --priority

    Note:
        This command is automatically called by `pyrig init` as part of the
        initialization sequence. You typically only need to run it manually
        when adding new config files or updating existing ones.
    """
    # local imports in pyrig to avoid cli failure when installing without dev deps
    # as some pyrig commands are dependend on dev deps and can only be used in a dev env
    from pyrig.dev.cli.commands.create_root import make_project_root  # noqa: PLC0415

    make_project_root(priority=priority)


def mktests() -> None:
    """Generate test skeleton files for all source code.

    Automatically creates test files that mirror the structure of the source
    package. For each module, class, and function in the source code, this
    command generates corresponding test functions with `NotImplementedError`
    placeholders.

    The generated tests follow pyrig's naming conventions:
    - Test modules: `test_<module_name>.py`
    - Test classes: `Test<ClassName>`
    - Test functions: `test_<function_name>`

    This command is idempotent - it will not overwrite existing test functions,
    only add new ones for untested code.

    Example:
        >>> # Generate test skeletons for all source code
        >>> uv run pyrig mktests

    Note:
        - Tests are also automatically generated when missing by running pytest
          with pyrig's conftest configuration.
        - The command uses parallel execution for faster test generation.
        - Generated tests must be implemented to pass - they raise
          `NotImplementedError` by default.

    See Also:
        `pyrig.dev.cli.commands.create_tests.make_test_skeletons`: Implementation.
    """
    from pyrig.dev.cli.commands.create_tests import make_test_skeletons  # noqa: PLC0415

    make_test_skeletons()


def mkinits() -> None:
    """Create missing __init__.py files throughout the project.

    Scans the project directory structure and creates __init__.py files for
    any directories that should be Python packages but are missing the init
    file. This ensures all packages are properly importable.

    This command is idempotent - it will not overwrite existing __init__.py
    files, only create missing ones.

    Example:
        >>> # Create all missing __init__.py files
        >>> uv run pyrig mkinits

    Note:
        This command is useful when you've created new package directories
        manually or when restructuring your project.

    See Also:
        `pyrig.dev.cli.commands.make_inits.make_init_files`: Implementation.
    """
    from pyrig.dev.cli.commands.make_inits import make_init_files  # noqa: PLC0415

    make_init_files()


def init() -> None:
    """Initialize a complete pyrig project from scratch.

    This is the main setup command that transforms a basic Python project into
    a fully-configured pyrig project. It runs a comprehensive 9-step initialization
    sequence:

    1. Add development dependencies (pyrig-dev)
    2. Sync virtual environment
    3. Create priority config files (pyproject.toml, .gitignore, LICENSE)
    4. Sync virtual environment again
    5. Create complete project structure (all config files)
    6. Generate test skeletons
    7. Run pre-commit hooks (format and lint all code)
    8. Run test suite
    9. Create initial git commit

    The entire process is automated and typically completes in a few minutes,
    leaving you with a production-ready project.

    Example:
        >>> # Initialize a new project
        >>> git clone https://github.com/username/my-project.git
        >>> cd my-project
        >>> uv init
        >>> uv add pyrig
        >>> uv run pyrig init

    Note:
        - This command should be run once when setting up a new project.
        - It requires a git repository to be initialized.
        - All steps are logged for transparency.
        - If any step fails, the process stops and reports the error.

    See Also:
        `pyrig.dev.cli.commands.init_project.init_project`: Implementation details.
    """
    from pyrig.dev.cli.commands.init_project import init_project  # noqa: PLC0415

    init_project()


def build() -> None:
    """Build all project artifacts.

    Discovers and invokes all Builder subclasses to create distributable
    artifacts. This typically includes PyInstaller executables and any
    custom build processes defined in your project.

    The build process:
    1. Discovers all non-abstract Builder subclasses across all packages
    2. Instantiates each builder (which triggers the build)
    3. Creates artifacts in the `dist/` directory
    4. Names artifacts with platform-specific suffixes (e.g., `app-Linux`)

    Example:
        >>> # Build all artifacts
        >>> uv run pyrig build

    Note:
        - Artifacts are placed in the `dist/` directory by default.
        - Each builder runs independently and in parallel where possible.
        - Platform-specific artifacts are automatically named (e.g., `-Windows`,
          `-Darwin`, `-Linux`).

    See Also:
        - `pyrig.dev.builders.base.base.Builder`: Base class for builders.
        - `pyrig.dev.builders.pyinstaller.PyInstallerBuilder`: PyInstaller builder.
    """
    from pyrig.dev.cli.commands.build_artifacts import build_artifacts  # noqa: PLC0415

    build_artifacts()


def protect_repo() -> None:
    """Configure GitHub repository protection rules.

    Sets up comprehensive branch protection for the main branch using GitHub's
    ruleset API. This includes:
    - Required linear history (no merge commits)
    - Required signed commits
    - Required status checks (CI must pass)
    - Pull request requirements
    - Restrictions on force pushes and deletions

    The protection rules are defined in `branch-protection.json` and can be
    customized for your project's needs.

    Example:
        >>> # Set up repository protection
        >>> uv run pyrig protect-repo

    Note:
        - Requires a `REPO_TOKEN` environment variable or in `.env` file.
        - The token must have `repo` scope permissions.
        - This command is idempotent - it updates existing rulesets if present.
        - Protection rules help enforce code quality and prevent accidental
          destructive operations.

    Raises:
        ValueError: If REPO_TOKEN is not found in environment or .env file.

    See Also:
        `pyrig.dev.cli.commands.protect_repo.protect_repository`: Implementation.
    """
    from pyrig.dev.cli.commands.protect_repo import protect_repository  # noqa: PLC0415

    protect_repository()
