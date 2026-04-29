"""Shared pytest fixtures for pyrig and all projects built with it.

Fixtures defined here or any other file in the same package
are automatically discovered by pytest and made available to any pytest suite
that inherits from this project.
"""

import platform
from collections.abc import Callable
from contextlib import chdir
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest
from pytest_mock import MockerFixture

from pyrig.core.introspection.modules import import_module_with_file_fallback
from pyrig.core.introspection.packages import (
    import_package_with_dir_fallback,
    make_package_dir,
)
from pyrig.core.introspection.paths import path_as_module_name
from pyrig.rig.configs.base.config_file import ConfigData, ConfigFile
from pyrig.rig.configs.pyproject import PyprojectConfigFile
from pyrig.rig.tools.package_manager import PackageManager
from pyrig.rig.tools.version_control.remote import (
    RemoteVersionController,
)


@pytest.fixture
def command_works() -> Callable[[Callable[..., Any]], None]:
    """Return a callable that verifies a CLI command is registered and executable.

    The returned function runs the command with ``--help`` and asserts that
    the process exits with return code 0 and that the command name appears
    in stdout.

    Returns:
        A callable ``(cmd) -> None`` that accepts a CLI function and asserts
        it is reachable and produces help output.
    """

    def check(cmd: Callable[..., Any]) -> None:
        # run --help comd to see if its available
        args = PackageManager.I.project_cmd_args("--help", cmd=cmd)
        completed_process = args.run()
        assert completed_process.returncode == 0
        stoud = completed_process.stdout
        name = cmd.__name__.replace("_", "-")  # ty:ignore[unresolved-attribute]
        assert name in stoud

    return check


@pytest.fixture
def command_calls_function(
    mocker: MockerFixture,
) -> Callable[[Callable[..., Any], Callable[..., Any]], None]:
    """Return a callable that verifies a CLI command delegates to the expected function.

    The returned function patches the target function by its fully qualified
    name, invokes the command, and asserts the patch was called exactly once.

    Args:
        mocker: pytest-mock fixture for patching.

    Returns:
        A callable ``(cmd, function) -> None`` that asserts ``cmd`` calls
        ``function`` exactly once.
    """

    def check(cmd: Callable[..., Any], function: Callable[..., Any]) -> None:
        mock = mocker.patch(function.__module__ + "." + function.__name__)  # ty:ignore[unresolved-attribute]
        cmd()
        mock.assert_called_once()

    return check


@pytest.fixture
def config_file_factory[T: ConfigFile[ConfigData]](
    tmp_path: Path,
) -> Callable[[type[T]], type[T]]:
    """Return a factory that wraps a ``ConfigFile`` subclass for isolated testing.

    The factory creates a dynamic subclass that redirects all file operations
    to pytest's ``tmp_path``. This prevents tests from reading or writing
    real project files. The following methods are overridden to enforce
    isolation:

    - ``path()`` and ``parent_path()``: prepend ``tmp_path`` to the original
      path if it is not already inside ``tmp_path`` and the current working
      directory is not ``tmp_path``.
    - ``_dump()`` and ``_load()``: change the working directory to
      ``tmp_path`` before delegating to the parent implementation.
    - ``create_file()``: changes the working directory to ``tmp_path`` before
      delegating to the parent implementation.

    Args:
        tmp_path: Pytest's per-test temporary directory.

    Returns:
        A callable ``(type[T]) -> type[T]`` that accepts a ``ConfigFile``
        subclass and returns a test-safe subclass with ``tmp_path``-based
        file operations.
    """

    def _make_test_config(
        base_class: type[T],
    ) -> type[T]:
        """Wrap ``base_class`` with ``tmp_path``-redirected file operations.

        Args:
            base_class: The ``ConfigFile`` subclass to wrap.

        Returns:
            A subclass of ``base_class`` with all file paths redirected to
            ``tmp_path``.
        """

        class TestConfigFile(base_class):  # ty: ignore[unsupported-base]
            """Test config file with tmp_path override."""

            def path(self) -> Path:
                """Get the file path redirected to tmp_path.

                Returns:
                    Path within tmp_path.
                """
                path = super().path()
                # append tmp_path to path if not already in tmp_path
                if not (path.is_relative_to(tmp_path) or Path.cwd() == tmp_path):
                    path = tmp_path / path
                return path

            def _dump(self, configs: ConfigData) -> None:
                """Write config to tmp_path, ensuring isolated test execution."""
                with chdir(tmp_path):
                    super()._dump(configs)

            def _load(self) -> ConfigData:
                """Load config from tmp_path, ensuring isolated test execution."""
                with chdir(tmp_path):
                    return super()._load()

            def parent_path(self) -> Path:
                """Get parent path redirected to tmp_path for test isolation."""
                # append tmp_path to path if not already in tmp_path
                path = super().parent_path()
                if not (path.is_relative_to(tmp_path) or Path.cwd() == tmp_path):
                    path = tmp_path / path
                return path

            def create_file(self) -> None:
                """Create file in tmp_path, ensuring isolated test execution."""
                with chdir(tmp_path):
                    super().create_file()

        return TestConfigFile  # ty:ignore[invalid-return-type]

    return _make_test_config


@pytest.fixture
def create_source_package(
    tmp_source_root_path: Path, create_package: Callable[[Path], ModuleType]
) -> Callable[[Path], ModuleType]:
    """Return a callable that creates a Python package under the temporary source root.

    Wraps ``create_package`` with a ``chdir`` to ``tmp_source_root_path``
    so that all relative path operations resolve within the temporary source
    tree.

    Args:
        tmp_source_root_path: Temporary source root directory.
        create_package: Fixture that creates a package from a relative path.

    Returns:
        A callable ``(path) -> ModuleType`` that creates and imports the
        package at ``path`` relative to the temporary source root.
    """

    def create(path: Path) -> ModuleType:
        """Create the package relative to the source root."""
        with chdir(tmp_source_root_path):
            return create_package(path)

    return create


@pytest.fixture
def create_package() -> Callable[[Path], ModuleType]:
    """Return a callable that creates a Python package at a given path.

    The returned function initializes the full directory tree as a package
    hierarchy by adding ``__init__.py`` files up to the current working
    directory, then imports and returns the package.

    Returns:
        A callable ``(path) -> ModuleType`` that creates and imports the
        package at ``path``.
    """

    def create(path: Path) -> ModuleType:
        """Create a package from the given path."""
        make_package_dir(path, until=(), content="")
        return import_package_with_dir_fallback(path, name=path_as_module_name(path))

    return create


@pytest.fixture
def create_module() -> Callable[[Path], ModuleType]:
    """Return a callable that creates a Python module at a given path.

    The returned function ensures the parent directory is a proper package
    hierarchy (adding ``__init__.py`` files up to the current working
    directory), touches the module file, and imports it.

    Returns:
        A callable ``(path) -> ModuleType`` that creates and imports the
        module at ``path``.
    """

    def create(path: Path) -> ModuleType:
        """Create a module from the given path."""
        make_package_dir(path.parent, until=(), content="")
        path.touch()
        return import_module_with_file_fallback(path, name=path_as_module_name(path))

    return create


@pytest.fixture
def tmp_package_root_path(
    tmp_project_root_path: Path,
    tmp_source_root_path: Path,
    create_source_package: Callable[[Path], ModuleType],
) -> tuple[Path, ModuleType]:
    """Provide the temporary package root directory and its imported package module.

    Creates the package root directory under the temporary source root,
    initializes it as a Python package, and returns both the path and the
    imported module.

    Args:
        tmp_project_root_path: Temporary project root directory.
        tmp_source_root_path: Temporary source root directory.
        create_source_package: Fixture for creating packages in the source root.

    Returns:
        Tuple of ``(path, package)`` where ``path`` is the package root
        directory and ``package`` is the imported package module.
    """
    path = tmp_project_root_path / PackageManager.I.package_root()

    package = create_source_package(path.relative_to(tmp_source_root_path))
    return path, package


@pytest.fixture
def tmp_source_root_path(tmp_project_root_path: Path) -> Path:
    """Provide the temporary source root directory.

    Creates the ``src`` directory inside the temporary project root.

    Args:
        tmp_project_root_path: Temporary project root directory.

    Returns:
        Path to the temporary source root directory.
    """
    path = tmp_project_root_path / PackageManager.I.source_root()
    path.mkdir()
    return path


@pytest.fixture
def tmp_project_root_path(tmp_path: Path) -> Path:
    """Provide a temporary project root directory named after the current project.

    Args:
        tmp_path: Pytest's per-test temporary directory.

    Returns:
        Path to the temporary project root directory.
    """
    path = tmp_path / PackageManager.I.project_name()
    path.mkdir()
    return path


@pytest.fixture(scope="session")
def standard_output_error_template() -> str:
    """Provide a format string for displaying combined stdout and stderr output.

    Contains ``{stdout}`` and ``{stderr}`` placeholders, useful for producing
    clear assertion failure messages that include full process output.

    Returns:
        Format string with ``{stdout}`` and ``{stderr}`` placeholders.
    """
    return """The standard output:
{stdout}
--------------------------------------------------------------------------------
The standard error:
{stderr}"""


@pytest.fixture(scope="session")
def on_linux_and_latest_python_version_or_not_in_ci(
    *, on_linux_and_latest_python_version: bool
) -> bool:
    """Return whether tests that require a canonical environment should run.

    True when running on Linux with the latest Python version, or when not
    running in CI at all. This is used to gate environment-sensitive tests,
    allowing them to always run locally while restricting them to the
    canonical CI environment in GitHub Actions.

    Args:
        on_linux_and_latest_python_version: Whether the environment is Linux
            with the latest Python version.

    Returns:
        True if the canonical CI conditions are met, or if not running in CI.
    """
    return (
        on_linux_and_latest_python_version
    ) or not RemoteVersionController.I.running_in_ci()


@pytest.fixture(scope="session")
def on_linux_and_latest_python_version(
    *, on_linux: bool, on_latest_python_version: bool
) -> bool:
    """Return whether the current environment is Linux with the latest Python version.

    Args:
        on_linux: Whether the current system is Linux.
        on_latest_python_version: Whether the current Python version is the latest.

    Returns:
        True if both conditions are met.
    """
    return on_linux and on_latest_python_version


@pytest.fixture(scope="session")
def on_linux(on_platform: Callable[[str], bool]) -> bool:
    """Return whether the current system is Linux.

    Args:
        on_platform: Fixture for checking the current platform by name.

    Returns:
        True if the system is Linux.
    """
    return on_platform("Linux")


@pytest.fixture(scope="session")
def on_latest_python_version(on_python_version: Callable[[str], bool]) -> bool:
    """Return whether the running Python version matches the latest stable release.

    The latest version is read from the project's bundled
    ``LATEST_PYTHON_VERSION`` resource via ``PyprojectConfigFile``.

    Args:
        on_python_version: Fixture for checking the current Python version.

    Returns:
        True if the current Python micro version matches the latest stable
        release.
    """
    latest_version = PyprojectConfigFile.I.latest_python_version("micro")
    return on_python_version(str(latest_version))


@pytest.fixture(scope="session")
def on_platform() -> Callable[[str], bool]:
    """Check if the current system platform matches a given name.

    Returns:
        A callable ``(platform_name) -> bool`` that compares
        ``platform.system()`` against the given name (e.g., ``"Linux"``,
        ``"Windows"``, ``"Darwin"``).
    """

    def check(platform_name: str) -> bool:
        """Check if the current system is the specified platform."""
        return platform.system() == platform_name

    return check


@pytest.fixture(scope="session")
def on_python_version() -> Callable[[str], bool]:
    """Check if the current Python version matches a given version string.

    Returns:
        A callable ``(version) -> bool`` that compares
        ``platform.python_version()`` against the given version string
        (e.g., ``"3.13.2"``).
    """

    def check(version: str) -> bool:
        """Check if the current Python version matches the specified version."""
        return platform.python_version() == version

    return check
