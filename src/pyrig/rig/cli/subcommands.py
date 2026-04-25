"""Project-specific CLI commands.

All functions in this module are automatically discovered and registered
as CLI commands for this project.
"""

import typer


def init() -> None:
    """Initialize a complete pyrig project from scratch.

    Transforms a basic Python project into a fully-configured, production-ready
    pyrig project through a comprehensive automated sequence.

    The initialization steps execute in the following order:

        1. Initialize version control (``git init``)
        2. Add development dependencies (``uv add --group dev``)
        3. Sync virtual environment (``uv sync``)
        4. Create project root (``mkroot``)
        5. Sync virtual environment again to apply updated configs
        6. Generate test skeletons (``mktests``)
        7. Install pre-commit hooks (``prek install``)
        8. Stage all files (``git add .``)
        9. Run pre-commit hooks to format and lint all files
        10. Run the test suite (``pytest``)
        11. Create the initial git commit

    Each step executes sequentially and is tracked with a progress bar. If any
    step fails, the process stops immediately.

    Example:
        $ cd my-project
        $ uv init
        $ uv add pyrig
        $ uv run pyrig init
    """
    from pyrig.rig.cli.commands.init_project import init_project  # noqa: PLC0415

    init_project()


def mkroot() -> None:
    """Create or update all project configuration files and directory structure.

    Discovers all ``ConfigFile`` subclasses across the project and its
    dependencies, then validates each one to create or update the corresponding
    file. This generates the complete project structure, including
    ``pyproject.toml``, ``.gitignore``, GitHub Actions workflows, prek hooks,
    and all other managed configuration files.

    Idempotent: safe to run multiple times. Existing files are updated only
    when their content is incorrect; user customizations are preserved where
    possible.

    Example:
        $ uv run pyrig mkroot
    """
    # local imports in pyrig to avoid cli failure when installing without dev deps
    # as some pyrig commands are dependend on dev deps and can only be used in a dev env
    from pyrig.rig.cli.commands.make_root import make_project_root  # noqa: PLC0415

    make_project_root()


def mktests() -> None:
    """Generate test skeleton files for all source code.

    Creates test files mirroring the source package structure. For each module,
    class, function, and method in the source code, generates a corresponding
    test skeleton with a ``NotImplementedError`` placeholder.

    Naming conventions:
        - Test modules: ``test_<module_name>.py``
        - Test classes: ``Test<ClassName>``
        - Test functions: ``test_<function_name>``
        - Test methods: ``test_<method_name>``

    Idempotent and non-destructive: only adds skeletons for untested code;
    all existing test implementations are preserved.

    Example:
        $ uv run pyrig mktests

    Note:
        Generated test functions raise ``NotImplementedError`` and must be
        implemented before the test suite will pass.
    """
    from pyrig.rig.cli.commands.make_tests import make_tests  # noqa: PLC0415

    make_tests()


def mkinits() -> None:
    """Create missing ``__init__.py`` files for all namespace packages.

    Scans the project for namespace packages (directories that contain Python
    files but no ``__init__.py``) and creates a minimal ``__init__.py`` for
    each. This ensures all packages follow standard Python package conventions
    and are properly importable.

    Idempotent and non-destructive: only creates missing files, never modifies
    existing ones. The ``docs`` directory and paths matched by ``.gitignore``
    are excluded from scanning.

    Example:
        $ uv run pyrig mkinits

    Note:
        Created ``__init__.py`` files contain only a minimal module docstring.
    """
    from pyrig.rig.cli.commands.make_inits import make_init_files  # noqa: PLC0415

    make_init_files()


def build() -> None:
    """Build all distributable artifacts for the project.

    Discovers all concrete ``BuilderConfigFile`` subclasses across the project
    and its dependencies, then validates each one to trigger the build process.
    Typical outputs include PyInstaller executables, documentation archives, and
    any other custom build artifacts defined as ``BuilderConfigFile`` subclasses.

    Build process per builder:

        1. Generates the build configuration file (e.g., a ``.spec`` file)
        2. Runs the build tool in a temporary directory
        3. Renames each output with a platform-specific suffix
           (e.g., ``app-Linux.zip``, ``app-Windows.zip``)
        4. Moves the renamed artifact to the ``dist/`` directory

    Builders that share the same priority level run in parallel; priority
    groups are processed sequentially from highest to lowest.

    Example:
        $ uv run pyrig build

    Note:
        Artifacts are written to ``dist/`` by default. The platform suffix is
        derived from ``platform.system()``.
    """
    from pyrig.rig.cli.commands.build_artifacts import build_artifacts  # noqa: PLC0415

    build_artifacts()


def protect_repo() -> None:
    """Apply security protections to the GitHub repository.

    Configures repository-level settings and branch protection rulesets on
    GitHub, enforcing pyrig's opinionated security defaults to maintain code
    quality and prevent accidental destructive operations.

    Repository settings applied:
        - Repository description synced from ``pyproject.toml``
        - Default branch set to ``main``
        - Branches deleted automatically after merge
        - Merge commits disabled (squash and rebase merges only)

    Branch protection rules applied:
        - Pull request reviews required, including code owner approval
        - Status checks required (health check workflow must pass)
        - Linear commit history enforced
        - Signed commits required
        - Force pushes and branch deletions disabled

    Protection rules are read from ``branch-protection.json`` and can be
    customized for your project.

    Idempotent: safe to run multiple times; existing rulesets are updated in
    place.

    Example:
        $ uv run pyrig protect-repo

    Raises:
        ValueError: If ``REPO_TOKEN`` is not found in the environment or
            ``.env`` file.
    """
    from pyrig.rig.cli.commands.protect_repo import protect_repository  # noqa: PLC0415

    protect_repository()


def resources() -> None:
    """Create the resources package for the project.

    Generates the ``resources`` package (an ``__init__.py`` file under the rig
    resources directory) if it does not already exist. The resources package is
    the conventional location for static assets such as templates, data files,
    and other non-code resources bundled with the project.

    Idempotent: safe to run multiple times; does nothing if the package already
    exists.

    Example:
        $ uv run pyrig resources
    """
    from pyrig.rig.cli.commands.make_resources import make_resources  # noqa: PLC0415

    make_resources()


def mkcmd(
    name: str = typer.Argument(help="Name of the command to create."),
    *,
    shared: bool = typer.Option(
        default=False,
        help="Whether the command should be shared in subsequent projects.",
    ),
) -> None:
    """Create a new CLI subcommand scaffold.

    Appends a new stub function to the project-specific subcommands module
    (``rig/cli/subcommands.py``) or, when ``shared=True``, to the shared
    subcommands module. The target module is created first if it does not yet
    exist. The command name is normalized from kebab-case to snake_case before
    being written as a Python function name.

    Args:
        name: Name of the command to create (kebab-case accepted,
            e.g. ``my-command`` becomes ``my_command``).
        shared: When ``True``, the stub is added to the shared subcommands
            module instead of the project-specific one.

    Example:
        $ uv run pyrig mkcmd my-command
    """
    from pyrig.rig.cli.commands.make_subcommand import make_subcommand  # noqa: PLC0415

    make_subcommand(name, shared=shared)


def subcls() -> None:
    """Create a subclass scaffold for an interactively selected pyrig class.

    Presents a fuzzy-search prompt listing all concrete and abstract
    ``DependencySubclass`` subclasses discovered from pyrig and its dependents.
    After a class is chosen, the corresponding source module is mirrored as a
    new config-managed file and a subclass skeleton is appended, ready for
    method overrides.

    Example:
        $ uv run pyrig subcls
    """
    from pyrig.rig.cli.commands.make_subclass import make_subclass  # noqa: PLC0415

    make_subclass()


def mkfixture(
    name: str = typer.Argument(help="Name of the fixture to create."),
) -> None:
    """Create a new pytest fixture scaffold in the shared fixtures module.

    Appends a new ``@pytest.fixture`` stub to the shared fixtures module. The
    fixture name is normalized from kebab-case to snake_case. ``import pytest``
    is added to the module automatically if it is not already present.

    Args:
        name: Name of the fixture to create (kebab-case accepted,
            e.g. ``my-fixture`` becomes ``my_fixture``).

    Example:
        $ uv run pyrig mkfixture my-fixture
    """
    from pyrig.rig.cli.commands.make_fixture import make_fixture  # noqa: PLC0415

    make_fixture(name)


def scratch() -> None:
    """Execute the ``.scratch`` file at the project root.

    Runs the ``.scratch`` Python script in a clean namespace using
    ``runpy.run_path``. The ``.scratch`` file is intended for temporary,
    experimental code that does not belong in the main source tree.

    Example:
        $ uv run pyrig scratch

    Note:
        The ``.scratch`` file is excluded from version control. If the file
        does not exist, a ``FileNotFoundError`` is raised.
    """
    from pyrig.rig.cli.commands.scratch import run_scratch_file  # noqa: PLC0415

    run_scratch_file()


def rmpyc() -> None:
    """Remove all ``__pycache__`` directories from the source and tests packages.

    Recursively deletes every ``__pycache__`` directory found under the main
    package root and the tests package root. Useful for clearing stale bytecode
    that may cause import or test-isolation issues.

    Idempotent: safe to run multiple times; only targets directories that
    currently exist.

    Example:
        $ uv run pyrig rmpyc
    """
    from pyrig.rig.cli.commands.remove_pycache import remove_pycache  # noqa: PLC0415

    remove_pycache()
