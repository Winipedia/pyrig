"""Contains pytest fixtures.

Any pytest fixtures defined under the fixtures package in
any file like this one will be automatically discovered and
are available in all projects inheriting from this one.
"""

import platform
from collections.abc import Callable
from contextlib import chdir
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

from pyrig.core.modules.imports import import_package_with_dir_fallback
from pyrig.core.modules.module import import_module_with_file_fallback
from pyrig.core.modules.package import make_package_dir
from pyrig.core.modules.path import path_as_module_name
from pyrig.core.types.config_file import ConfigData
from pyrig.rig.configs.base.config_file import ConfigFile
from pyrig.rig.configs.pyproject import PyprojectConfigFile
from pyrig.rig.tools.package_manager import PackageManager


@pytest.fixture
def command_works() -> Callable[[Callable[..., Any]], None]:
    """Fixture to check if a pyrig command is available and works.

    Usage:
        returns a function that takes a command function (e.g. mkroot) and
        checks if it can be run with --help without error.
        This is a basic check to ensure the command is properly registered
        and can be executed.
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
def config_file_factory[T: ConfigFile[ConfigData]](
    tmp_path: Path,
) -> Callable[[type[T]], type[T]]:
    """Provide a factory for creating test-safe ConfigFile subclasses.

    Creates dynamic subclasses that redirect all file operations to pytest's
    tmp_path for isolated testing. Overrides ``path()``, ``parent_path()``,
    ``_dump()``, ``_load()``, and ``create_file()`` to ensure complete isolation.

    Args:
        tmp_path: Pytest's temporary directory, auto-provided per test.

    Returns:
        Factory function ``(type[T]) -> type[T]`` that wraps a ConfigFile
        subclass with tmp_path-based file operations.
    """

    def _make_test_config(
        base_class: type[T],
    ) -> type[T]:
        """Create a test config class that uses tmp_path.

        Args:
            base_class: The ConfigFile subclass to wrap.

        Returns:
            A subclass with path() redirected to tmp_path.
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

            def _dump(self, config: ConfigData) -> None:
                """Write config to tmp_path, ensuring isolated test execution."""
                with chdir(tmp_path):
                    super()._dump(config)

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
def create_module() -> Callable[[Path], ModuleType]:
    """Fixture to create a module from a given path."""

    def create(path: Path) -> ModuleType:
        """Create a module from the given path."""
        make_package_dir(path.parent, until=(), content="")
        path.touch()
        return import_module_with_file_fallback(path, name=path_as_module_name(path))

    return create


@pytest.fixture
def create_package() -> Callable[[Path], ModuleType]:
    """Fixture to create a package from a given path."""

    def create(path: Path) -> ModuleType:
        """Create a package from the given path."""
        make_package_dir(path, until=(), content="")
        return import_package_with_dir_fallback(path, name=path_as_module_name(path))

    return create


@pytest.fixture
def create_source_package(
    tmp_source_root_path: Path, create_package: Callable[[Path], ModuleType]
) -> Callable[[Path], ModuleType]:
    """Creates a package in the source directory."""

    def create(path: Path) -> ModuleType:
        """Creates the package."""
        with chdir(tmp_source_root_path):
            return create_package(path)

    return create


@pytest.fixture
def create_source_module(
    tmp_source_root_path: Path, create_module: Callable[[Path], ModuleType]
) -> Callable[[Path], ModuleType]:
    """Creates a package in the source directory."""

    def create(path: Path) -> ModuleType:
        """Creates the package."""
        with chdir(tmp_source_root_path):
            return create_module(path)

    return create


@pytest.fixture
def tmp_project_root_path(tmp_path: Path) -> Path:
    """Fixture to provide a temporary project path for testing."""
    path = tmp_path / PackageManager.I.project_name()
    path.mkdir()
    return path


@pytest.fixture
def tmp_source_root_path(tmp_project_root_path: Path) -> Path:
    """Fixture to provide a temporary source path for testing."""
    path = tmp_project_root_path / PackageManager.I.source_root()
    path.mkdir()
    return path


@pytest.fixture
def tmp_package_root_path(
    tmp_project_root_path: Path,
    tmp_source_root_path: Path,
    create_source_package: Callable[[Path], ModuleType],
) -> tuple[Path, ModuleType]:
    """Creates the package root."""
    path = tmp_project_root_path / PackageManager.I.package_root()

    package = create_source_package(path.relative_to(tmp_source_root_path))
    return path, package


@pytest.fixture(scope="session")
def standard_output_error_template() -> str:
    """Fixture to provide a standard template for stdout and stderr in tests."""
    return """The standard output:
{stdout}
--------------------------------------------------------------------------------
The standard error:
{stderr}"""


@pytest.fixture
def on_linux_and_latest_python() -> bool:
    """Check if the current system is Linux and running the latest Python version."""
    system = platform.system()
    if system != "Linux":
        return False
    latest_python_version = str(PyprojectConfigFile.I.latest_python_version("micro"))
    sys_python_version = platform.python_version()
    return sys_python_version == latest_python_version
