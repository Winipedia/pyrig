"""Project-specific CLI command wrappers for pyrig.

This module defines the main CLI commands for pyrig. All public functions in
this module are automatically discovered and registered as CLI commands by
pyrig's dynamic command discovery system (see `pyrig.dev.cli.cli.add_subcommands`).

Architecture:
    This module contains thin wrapper functions that delegate to implementation
    functions in the `pyrig.dev.cli.commands` package. This separation provides:

    - **Clean CLI interface**: Command signatures focus on CLI arguments only
    - **Testable logic**: Implementation functions can be tested independently
    - **Lazy imports**: Dev dependencies are imported only when commands execute,
      preventing import errors when pyrig is installed without dev dependencies

Commands:
    - `init`: Complete project initialization (9-step automated setup)
    - `mkroot`: Create project structure and configuration files
    - `mktests`: Generate test skeleton files for all source code
    - `mkinits`: Create missing __init__.py files for namespace packages
    - `build`: Build all distributable artifacts
    - `protect_repo`: Configure GitHub repository protection rules

Extensibility:
    Projects that depend on pyrig can create their own `subcommands.py` module
    at `<package>/dev/cli/subcommands.py`. All public functions in that module
    will be automatically discovered and registered as CLI commands for the
    project.

Example:
    Creating custom commands in a dependent project::

        # myproject/dev/cli/subcommands.py
        def deploy() -> None:
            '''Deploy the application to production.'''
            from myproject.deployment import deploy_app
            deploy_app()

        def status() -> None:
            '''Check application status.'''
            from myproject.monitoring import check_status
            check_status()

    Then run::

        $ uv run myproject deploy
        $ uv run myproject status
        $ uv run myproject version  # Shared command from pyrig

Note:
    - All imports from `pyrig.dev.cli.commands` are local (inside functions)
      to avoid import errors when dev dependencies are not installed
    - Functions are registered as commands in the order they are defined
    - Only public functions (not starting with `_`) are registered

See Also:
    pyrig.dev.cli.cli.add_subcommands: Command discovery mechanism
    pyrig.dev.cli.commands: Implementation functions for commands
    pyrig.dev.cli.shared_subcommands: Shared commands across all pyrig projects
"""

import typer


def mkroot(
    *,
    priority: bool = typer.Option(
        default=False,
        help="Only create priority config files.",
    ),
) -> None:
    """Create or update all project configuration files and directory structure.

    Discovers all ConfigFile subclasses across the project and its dependencies,
    then initializes each one to create or update configuration files. This
    generates the complete project structure including pyproject.toml, .gitignore,
    GitHub workflows, pre-commit hooks, and other configuration files.

    The command uses pyrig's multi-package architecture to discover ConfigFile
    implementations across all packages in the dependency chain, enabling
    projects to define their own configuration files that are automatically
    created alongside pyrig's standard configs.

    Behavior:
        - **Idempotent**: Safe to run multiple times; will not overwrite existing
          files unless they are missing required configuration
        - **Non-destructive**: Only adds missing configs or updates incomplete
          files; never removes existing configuration
        - **Priority-aware**: Can create only high-priority files first (useful
          during initialization when some configs depend on others)

    Args:
        priority: If True, only creates config files with priority > 0 (e.g.,
            pyproject.toml, .gitignore, LICENSE). This is used during the `init`
            command to create essential files before installing dependencies.
            If False (default), creates all config files.

    Example:
        Create all configuration files::

            $ uv run pyrig mkroot

        Create only priority configuration files::

            $ uv run pyrig mkroot --priority

    Note:
        - This command is automatically called twice by `pyrig init`: once with
          `--priority` to create essential files, then again without to create
          all remaining files
        - Config files are created in parallel within each priority group for
          performance
        - The command delegates to `ConfigFile.init_all_subclasses()` or
          `ConfigFile.init_priority_subclasses()` depending on the flag

    See Also:
        pyrig.dev.cli.commands.create_root.make_project_root: Implementation
        pyrig.dev.configs.base.base.ConfigFile: Base class for config files
        pyrig.dev.cli.subcommands.init: Full initialization command
    """
    # local imports in pyrig to avoid cli failure when installing without dev deps
    # as some pyrig commands are dependend on dev deps and can only be used in a dev env
    from pyrig.dev.cli.commands.create_root import make_project_root  # noqa: PLC0415

    make_project_root(priority=priority)


def mktests() -> None:
    """Generate test skeleton files for all source code.

    Automatically creates test files that mirror the structure of the source
    package. For each module, class, function, and method in the source code,
    this command generates corresponding test skeletons with `NotImplementedError`
    placeholders, ensuring every piece of code has a test waiting to be
    implemented.

    The command walks through the entire source package hierarchy and creates:
    - Test packages mirroring source packages
    - Test modules mirroring source modules
    - Test functions for each source function
    - Test classes for each source class
    - Test methods for each source method

    Naming Conventions:
        - Test modules: `test_<module_name>.py` (e.g., `test_utils.py`)
        - Test classes: `Test<ClassName>` (e.g., `TestMyClass`)
        - Test functions: `test_<function_name>` (e.g., `test_calculate`)
        - Test methods: `test_<method_name>` (e.g., `test_process`)

    Behavior:
        - **Idempotent**: Safe to run multiple times; will not overwrite existing
          test functions, only add new ones for untested code
        - **Non-destructive**: Preserves all existing test code and only appends
          new test skeletons
        - **Parallel execution**: Uses ThreadPoolExecutor for fast test generation
          across multiple modules

    Example:
        Generate test skeletons for all source code::

            $ uv run pyrig mktests

        This creates test files like::

            tests/test_myproject/test_src/test_utils.py
            tests/test_myproject/test_src/test_models/test_user.py

    Note:
        - Generated test functions raise `NotImplementedError` and must be
          implemented to pass
        - Tests are also automatically generated when missing by pytest through
          pyrig's conftest configuration (see autouse fixtures)
        - The command only processes the main source package, not the tests
          package itself
        - Test skeletons include minimal docstrings ("Test function." or
          "Test method.")

    See Also:
        pyrig.dev.cli.commands.create_tests.make_test_skeletons: Implementation
        pyrig.dev.tests.fixtures.autouse.session: Autouse fixtures that also
            generate tests
    """
    from pyrig.dev.cli.commands.create_tests import make_test_skeletons  # noqa: PLC0415

    make_test_skeletons()


def mkinits() -> None:
    """Create missing __init__.py files for all namespace packages.

    Scans the project directory structure to find namespace packages (directories
    containing Python files but no __init__.py) and creates minimal __init__.py
    files for them. This ensures all packages follow traditional Python package
    conventions and are properly importable.

    The command discovers namespace packages using pyrig's package discovery
    utilities and creates __init__.py files with a minimal docstring. It uses
    parallel execution for performance when creating multiple files.

    Behavior:
        - **Idempotent**: Safe to run multiple times; will not overwrite existing
          __init__.py files, only create missing ones
        - **Non-destructive**: Never modifies or removes existing files
        - **Parallel execution**: Uses ThreadPoolExecutor for fast file creation
        - **Minimal content**: Created files contain only a basic docstring

    Example:
        Create all missing __init__.py files::

            $ uv run pyrig mkinits

        If namespace packages are found, creates files like::

            myproject/utils/__init__.py
            myproject/models/__init__.py

    Note:
        - This command is useful when you've created new package directories
          manually or when restructuring your project
        - The command skips the `docs` directory to avoid interfering with
          documentation structure
        - If no namespace packages are found, the command logs an info message
          and exits without creating any files
        - Created __init__.py files contain a minimal docstring: `module.`

    See Also:
        pyrig.dev.cli.commands.make_inits.make_init_files: Implementation
        pyrig.dev.utils.packages.get_namespace_packages: Namespace package discovery
        pyrig.src.modules.path.make_init_module: __init__.py file creation
    """
    from pyrig.dev.cli.commands.make_inits import make_init_files  # noqa: PLC0415

    make_init_files()


def init() -> None:
    """Initialize a complete pyrig project from scratch.

    This is the main setup command that transforms a basic Python project into
    a fully-configured, production-ready pyrig project. It orchestrates a
    comprehensive 9-step initialization sequence that automates all setup tasks.

    Initialization Steps:
        1. **Add development dependencies**: Installs pyrig-dev and other dev
           dependencies via `uv add --dev`
        2. **Sync virtual environment**: Installs all dependencies via `uv sync`
        3. **Create priority config files**: Creates essential files (pyproject.toml,
           .gitignore, LICENSE) via `mkroot --priority`
        4. **Sync virtual environment again**: Ensures new configs are applied
        5. **Create complete project structure**: Creates all remaining config
           files and directory structure via `mkroot`
        6. **Generate test skeletons**: Creates test files for all source code
           via `mktests`
        7. **Run pre-commit hooks**: Installs hooks, stages files, and runs
           formatters/linters on all code
        8. **Run test suite**: Validates everything works via pytest
        9. **Create initial git commit**: Commits all changes with message
           "pyrig: Initial commit"

    The entire process is automated, logged for transparency, and typically
    completes in a few seconds. Each step is executed sequentially, and if any
    step fails, the process stops and reports the error.

    Example:
        Initialize a new project::

            $ git clone https://github.com/username/my-project.git
            $ cd my-project
            $ uv init
            $ uv add pyrig
            $ uv run pyrig init

        After completion, you have a production-ready project with:
        - Complete configuration files
        - Test skeletons for all code
        - Pre-commit hooks installed and run
        - All tests passing
        - Initial git commit created

    Note:
        - **Run once**: This command should be run once when setting up a new
          project, not repeatedly
        - **Git required**: Requires a git repository to be initialized (for
          pre-commit and final commit)
        - **Idempotent steps**: Individual steps (mkroot, mktests) are idempotent,
          but the full sequence is designed for initial setup
        - **Logged progress**: All steps are logged with clear messages showing
          progress
        - **Error handling**: If any step fails, the process stops immediately
          and reports the error

    See Also:
        pyrig.dev.cli.commands.init_project.init_project: Implementation
        pyrig.dev.cli.subcommands.mkroot: Config file creation
        pyrig.dev.cli.subcommands.mktests: Test skeleton generation
    """
    from pyrig.dev.cli.commands.init_project import init_project  # noqa: PLC0415

    init_project()


def build() -> None:
    """Build all distributable artifacts for the project.

    Discovers and invokes all Builder subclasses across the project and its
    dependencies to create distributable artifacts. This typically includes
    PyInstaller executables, documentation archives, and any custom build
    processes defined in Builder subclasses.

    The command uses pyrig's multi-package architecture to discover Builder
    implementations across all packages in the dependency chain, enabling
    projects to define their own builders that are automatically executed
    alongside pyrig's standard builders.

    Build Process:
        1. **Discovery**: Finds all non-abstract Builder subclasses across all
           packages that depend on pyrig
        2. **Instantiation**: Instantiates each builder class (instantiation
           triggers the build process via `__init__`)
        3. **Artifact creation**: Each builder creates its artifacts in a
           temporary directory
        4. **Platform naming**: Artifacts are renamed with platform-specific
           suffixes (e.g., `-Linux`, `-Darwin`, `-Windows`)
        5. **Output**: Artifacts are moved to the `dist/` directory

    Behavior:
        - **Sequential execution**: Builders are instantiated and executed
          sequentially, not in parallel
        - **Platform-specific**: Artifacts are automatically named with the
          current platform (e.g., `myapp-Linux`, `myapp-Windows`)
        - **Temporary directory**: Each builder works in a temporary directory
          that is cleaned up after the build
        - **Leaf classes only**: Only leaf Builder classes are executed; parent
          classes in inheritance hierarchies are excluded

    Example:
        Build all artifacts::

            $ uv run pyrig build

        This discovers and executes all builders, creating artifacts like::

            dist/myapp-Linux
            dist/docs-Linux.zip

    Note:
        - Artifacts are placed in the `dist/` directory by default (configurable
          via `Builder.get_artifacts_dir()`)
        - Each builder runs independently; if one fails, others are not affected
        - Platform-specific naming uses `platform.system()` to determine the
          current platform
        - The command delegates to `Builder.init_all_non_abstract_subclasses()`

    See Also:
        pyrig.dev.cli.commands.build_artifacts.build_artifacts: Implementation
        pyrig.dev.builders.base.base.Builder: Base class for builders
        pyrig.dev.builders.pyinstaller.PyInstallerBuilder: PyInstaller builder
    """
    from pyrig.dev.cli.commands.build_artifacts import build_artifacts  # noqa: PLC0415

    build_artifacts()


def protect_repo() -> None:
    """Configure GitHub repository protection rules and security settings.

    Applies comprehensive security protections to the GitHub repository,
    including both repository-level settings and branch protection rulesets.
    This enforces pyrig's opinionated security defaults to maintain code
    quality and prevent accidental destructive operations.

    The command performs two main tasks:
    1. **Repository settings**: Configures repository-level security and merge
       settings
    2. **Branch protection**: Creates or updates a ruleset for the default
       branch (main)

    Repository Settings:
        - Description from pyproject.toml
        - Default branch set to 'main'
        - Delete branches on merge enabled
        - Allow update branch button enabled
        - Merge commits disabled (squash and rebase only)

    Branch Protection Rules:
        - Required pull request reviews with code owner approval
        - Required status checks (health check workflow must pass)
        - Linear commit history required (no merge commits)
        - Signed commits required
        - Force pushes disabled
        - Branch deletions disabled

    The protection rules are loaded from `branch-protection.json` configuration
    file and can be customized for your project's needs.

    Example:
        Set up repository protection::

            $ uv run pyrig protect-repo

        This configures the repository and creates/updates the branch protection
        ruleset.

    Note:
        - **Authentication required**: Requires a `REPO_TOKEN` environment
          variable or in `.env` file with `repo` scope permissions
        - **Idempotent**: Safe to run multiple times; updates existing rulesets
          if present rather than creating duplicates
        - **GitHub API**: Uses GitHub's REST API to configure settings and
          rulesets
        - **Error handling**: Raises ValueError if REPO_TOKEN is not found

    Raises:
        ValueError: If REPO_TOKEN is not found in environment variables or
            .env file.

    See Also:
        pyrig.dev.cli.commands.protect_repo.protect_repository: Implementation
        pyrig.dev.configs.branch_protection: Branch protection configuration
        pyrig.dev.utils.git.create_or_update_ruleset: Ruleset creation/update
    """
    from pyrig.dev.cli.commands.protect_repo import protect_repository  # noqa: PLC0415

    protect_repository()
