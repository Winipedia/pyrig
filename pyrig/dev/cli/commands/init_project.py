"""Project initialization orchestration for pyrig.

This module provides the complete initialization flow for pyrig projects,
transforming a basic Python project into a fully-configured, production-ready
pyrig project through a comprehensive 9-step automated sequence.

The initialization process is orchestrated by the `init_project()` function,
which executes a series of setup steps in a specific order to ensure all
dependencies and configurations are properly established.

Initialization Steps:
    1. **Adding dev dependencies**: Installs pyrig-dev and other development
       dependencies via `uv add --dev`
    2. **Syncing venv**: Installs all dependencies via `uv sync`
    3. **Creating priority config files**: Creates essential configuration files
       (pyproject.toml, .gitignore, LICENSE) that other steps depend on
    4. **Syncing venv again**: Ensures new configurations are applied and any
       new dependencies are installed
    5. **Creating project root**: Generates all remaining configuration files
       and directory structure
    6. **Creating test files**: Generates test skeletons for all source code
    7. **Running pre-commit hooks**: Installs hooks, stages files, and runs
       formatters/linters on all code
    8. **Running tests**: Validates everything works via pytest
    9. **Committing initial changes**: Creates initial git commit with all
       changes

Each step is implemented as a separate function and executed sequentially.
If any step fails, the process stops and reports the error.

Functions:
    - `init_project`: Main orchestration function that runs all steps
    - `adding_dev_dependencies`: Step 1 - Install dev dependencies
    - `syncing_venv`: Steps 2 & 4 - Sync virtual environment
    - `creating_priority_config_files`: Step 3 - Create essential configs
    - `creating_project_root`: Step 5 - Create all config files
    - `creating_test_files`: Step 6 - Generate test skeletons
    - `running_pre_commit_hooks`: Step 7 - Run formatters and linters
    - `running_tests`: Step 8 - Run test suite
    - `committing_initial_changes`: Step 9 - Create initial commit

Example:
    Run from command line::

        $ uv run pyrig init

    Or programmatically::

        >>> from pyrig.dev.cli.commands.init_project import init_project
        >>> init_project()

Note:
    - The initialization process is designed for initial setup, not repeated
      execution
    - Individual steps (like mkroot, mktests) are idempotent, but the full
      sequence is optimized for first-time setup
    - Requires a git repository to be initialized for pre-commit and final
      commit steps
    - All steps are logged with clear progress messages

See Also:
    pyrig.dev.cli.subcommands.init: CLI wrapper for this functionality
    pyrig.dev.cli.commands.create_root: Config file creation
    pyrig.dev.cli.commands.create_tests: Test skeleton generation
"""

import logging
from collections.abc import Callable
from typing import Any

import pyrig
from pyrig.dev.cli.subcommands import mkroot, mktests
from pyrig.src.consts import STANDARD_DEV_DEPS
from pyrig.src.management.package_manager import PackageManager
from pyrig.src.management.pre_committer import (
    PreCommitter,
)
from pyrig.src.management.project_tester import ProjectTester
from pyrig.src.management.pyrigger import Pyrigger
from pyrig.src.management.version_controller import VersionController
from pyrig.src.string import make_name_from_obj

logger = logging.getLogger(__name__)


def adding_dev_dependencies() -> None:
    """Install development dependencies for the project (Step 1).

    Executes `uv add --dev <dependencies>` to install pyrig's standard
    development dependencies. This is the first step in the initialization
    sequence and must complete before other steps can proceed.

    The command adds development dependencies to the `[project.optional-dependencies]`
    section of pyproject.toml under the "dev" group, making them available for
    development tasks like testing, linting, and building.

    Dependencies Installed:
        The standard dev dependencies are defined in `STANDARD_DEV_DEPS` and
        typically include packages like pyrig-dev, pytest, ruff, etc.

    Note:
        - This step modifies pyproject.toml to add the dev dependencies
        - The actual installation happens in the next step (syncing_venv)
        - Uses PackageManager to construct the appropriate uv command
        - Runs as a subprocess with check=True to ensure it completes successfully
    """
    args = PackageManager.get_add_dev_dependencies_args(*STANDARD_DEV_DEPS)
    args.run()


def creating_priority_config_files() -> None:
    """Create essential configuration files (Step 3).

    Executes `uv run pyrig mkroot --priority` to create high-priority
    configuration files that other initialization steps depend on. This
    includes files like pyproject.toml, .gitignore, and LICENSE.

    Priority config files are those with priority > 0 in their ConfigFile
    subclass definitions. These files must exist before other configs can
    be created or before dependencies can be properly installed.

    Note:
        - Uses Pyrigger to construct the command to run mkroot with --priority flag
        - Runs as a subprocess with check=True to ensure it completes successfully
        - This is idempotent; running multiple times is safe
    """
    # local imports to avoid failure on init when dev deps are not installed yet.
    args = Pyrigger.get_cmd_args(mkroot, "--priority")
    args.run()


def syncing_venv() -> None:
    """Sync the virtual environment with dependencies (Steps 2 & 4).

    Executes `uv sync` to install all dependencies listed in pyproject.toml,
    including both regular dependencies and optional dev dependencies. This
    step is run twice during initialization: once after adding dev dependencies
    (step 2) and again after creating priority config files (step 4).

    The sync operation:
    - Reads dependencies from pyproject.toml
    - Installs or updates packages in the virtual environment
    - Ensures the environment matches the project configuration

    Note:
        - Uses PackageManager to construct the appropriate uv command
        - Runs as a subprocess with check=True to ensure it completes successfully
        - This is idempotent; running multiple times is safe
    """
    args = PackageManager.get_install_dependencies_args()
    args.run()


def creating_project_root() -> None:
    """Create complete project structure and all config files (Step 5).

    Executes `uv run pyrig mkroot` to generate all remaining configuration
    files and the complete project directory structure. This creates all
    ConfigFile subclass instances that weren't created in the priority step.

    The command discovers all ConfigFile subclasses across the project and
    its dependencies, then initializes each one to create or update
    configuration files.

    Note:
        - Uses Pyrigger to construct the command to run mkroot
        - Runs as a subprocess with check=True to ensure it completes successfully
        - This is idempotent; running multiple times is safe
    """
    args = Pyrigger.get_cmd_args(mkroot)
    args.run()


def creating_test_files() -> None:
    """Generate test skeleton files for all source code (Step 6).

    Executes `uv run pyrig mktests` to generate test files that mirror the
    structure of the source package. For each module, class, function, and
    method in the source code, this creates corresponding test skeletons with
    NotImplementedError placeholders.

    The generated tests follow pyrig's naming conventions and provide a
    starting point for implementing comprehensive test coverage.

    Note:
        - Uses Pyrigger to construct the command to run mktests
        - Runs as a subprocess with check=True to ensure it completes successfully
        - This is idempotent; running multiple times is safe
    """
    args = Pyrigger.get_cmd_args(mktests)
    args.run()


def running_pre_commit_hooks() -> None:
    """Install and run pre-commit hooks on all files (Step 7).

    Performs three operations to ensure the codebase is in a clean, linted,
    and formatted state:

    1. **Install hooks**: Installs pre-commit hooks into .git/hooks/
    2. **Stage files**: Adds all files to git staging area
    3. **Run hooks**: Executes all pre-commit hooks on all files

    The pre-commit hooks typically include formatters (ruff format, prettier),
    linters (ruff check, mypy), and other code quality checks. This step
    ensures all generated code follows the project's style guidelines.

    Note:
        - Uses PreCommitter to construct pre-commit commands
        - Uses VersionController to stage files with git
        - Runs as subprocesses with check=True to ensure they complete successfully
        - This step may modify files (formatting), so it runs before tests
    """
    # install pre-commit hooks
    PreCommitter.get_install_args().run()
    # add all files to git
    VersionController.get_add_all_args().run()
    # run pre-commit hooks
    PreCommitter.get_run_all_files_args().run()


def running_tests() -> None:
    """Run the complete test suite (Step 8).

    Executes `pytest` to run the entire test suite and verify that everything
    is working correctly after initialization. This validates that:

    - All generated test skeletons are syntactically correct
    - The project structure is properly configured
    - Dependencies are correctly installed
    - No import errors or configuration issues exist

    Note:
        - Uses ProjectTester to construct the pytest command
        - Runs as a subprocess with check=True to ensure it completes successfully
        - Generated test skeletons raise NotImplementedError, which is expected
          and doesn't cause test failures in pyrig's test configuration
    """
    args = ProjectTester.get_run_tests_args()
    args.run()


def committing_initial_changes() -> None:
    """Create initial git commit with all changes (Step 9).

    Commits all changes made during initialization in a single commit with
    the message "pyrig: Initial commit". This creates a clean starting point
    for the project with all configuration files, test skeletons, and
    formatted code.

    The commit includes:
    - All configuration files created by mkroot
    - All test skeletons created by mktests
    - All formatting changes made by pre-commit hooks
    - Any other files generated during initialization

    Note:
        - Files were already staged by the running_pre_commit_hooks step
        - Uses VersionController to construct the git commit command
        - Uses --no-verify to skip pre-commit hooks (they already ran)
        - Runs as a subprocess with check=True to ensure it completes successfully
    """
    # changes were added by the run pre-commit hooks step
    args = VersionController.get_commit_no_verify_args(
        f"{pyrig.__name__}: Initial commit"
    )
    args.run()


SETUP_STEPS: list[Callable[..., Any]] = [
    adding_dev_dependencies,
    syncing_venv,
    creating_priority_config_files,
    syncing_venv,
    creating_project_root,
    creating_test_files,
    running_pre_commit_hooks,
    running_tests,
    committing_initial_changes,
]


def init_project() -> None:
    """Initialize a pyrig project by running all setup steps sequentially.

    This is the main orchestration function that executes the complete
    initialization sequence. It runs each step in `SETUP_STEPS` in order,
    logging progress for each step.

    The function is the implementation target for the `pyrig init` CLI command
    and transforms a basic Python project into a fully-configured, production-ready
    pyrig project.

    Initialization Steps:
        1. **Adding dev dependencies**: Installs pyrig-dev and other dev packages
        2. **Syncing venv**: Installs all dependencies from pyproject.toml
        3. **Creating priority config files**: Creates essential configs
           (pyproject.toml, .gitignore, LICENSE)
        4. **Syncing venv**: Ensures new configurations are applied
        5. **Creating project root**: Generates all remaining config files and
           directory structure
        6. **Creating test files**: Generates test skeletons for all source code
        7. **Running pre-commit hooks**: Installs hooks and runs formatters/linters
        8. **Running tests**: Validates everything works via pytest
        9. **Committing initial changes**: Creates initial git commit

    Each step is implemented as a separate function and executed sequentially.
    If any step fails (raises an exception), the process stops immediately.

    Logging:
        - Logs "Initializing project" at the start
        - Logs each step name before executing it (e.g., "adding dev dependencies")
        - Logs "Initialization complete!" at the end

    Note:
        - This function should be run once when setting up a new project
        - Requires a git repository to be initialized
        - All steps are logged for transparency
        - Step names are generated from function names using `make_name_from_obj`

    See Also:
        SETUP_STEPS: List of step functions executed by this function
        pyrig.dev.cli.subcommands.init: CLI wrapper for this function
    """
    logger.info("Initializing project")
    for step in SETUP_STEPS:
        step_name = make_name_from_obj(step, join_on=" ")
        logger.info(step_name)
        step()
    logger.info("Initialization complete!")
