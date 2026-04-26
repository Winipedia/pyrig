"""test module."""

import platform
from collections.abc import Callable
from contextlib import chdir
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

import pyrig
from pyrig.rig.cli.commands.make_root import make_project_root
from pyrig.rig.cli.shared_subcommands import version
from pyrig.rig.cli.subcommands import mkroot
from pyrig.rig.configs.base.config_file import ConfigFile
from pyrig.rig.configs.pyproject import PyprojectConfigFile
from pyrig.rig.tools.remote_version_controller import RemoteVersionController


@pytest.fixture
def sample_config_file(
    config_file_factory: Callable[
        [type[ConfigFile[dict[str, Any]]]], type[ConfigFile[dict[str, Any]]]
    ],
) -> type[ConfigFile[dict[str, Any]]]:
    """Create a sample config file class for testing the factory."""

    class SampleConfigFile(config_file_factory(ConfigFile)):  # ty: ignore[unsupported-base]
        """Sample config file for testing."""

        def parent_path(self) -> Path:
            """Get the parent path."""
            return Path()

        def stem(self) -> str:
            """Get the stem."""
            return "sample"

        def _load(self) -> dict[str, Any]:
            """Load the config."""
            return {}

        def _dump(self, config: dict[str, Any] | list[Any]) -> None:
            """Dump the config."""

        def extension(self) -> str:
            """Get the file extension."""
            return "test"

        def _configs(self) -> dict[str, Any]:
            """Get the configs."""
            return {"key": "value"}

    return SampleConfigFile


def test_config_file_factory(
    sample_config_file: type[ConfigFile[dict[str, Any]]], tmp_path: Path
) -> None:
    """Test that config_file_factory wraps path to use tmp_path."""
    assert issubclass(sample_config_file, ConfigFile), (
        "Expected sample_config_file to be a class"
    )
    # The factory should wrap the path method to use tmp_path
    path = sample_config_file().path()

    # The path should be inside tmp_path
    assert str(path).startswith(str(tmp_path)), (
        f"Expected path {path} to start with {tmp_path}"
    )

    # The path should have the correct extension
    assert path.suffix == ".test", f"Expected extension '.test', got {path.suffix}"

    assert path.name == "sample.test", (
        f"Expected filename 'sample.test', got {path.name}"
    )


def test_command_works(command_works: Callable[[Callable[..., Any]], None]) -> None:
    """Test function."""
    command_works(version)


def test_create_module(
    tmp_path: Path, create_module: Callable[[Path], ModuleType]
) -> None:
    """Test function."""
    with chdir(tmp_path):
        module_path = Path(f"{test_create_module.__name__}.py")
        module = create_module(module_path)
        assert isinstance(module, ModuleType)
        assert module.__name__ == test_create_module.__name__
        assert module.__file__ == str(module_path.resolve())


def test_create_package(
    tmp_path: Path, create_package: Callable[[Path], ModuleType]
) -> None:
    """Test function."""
    with chdir(tmp_path):
        package_dir = Path(test_create_package.__name__)
        package = create_package(package_dir)
        assert isinstance(package, ModuleType), f"Expected package, got {type(package)}"
        assert package.__name__ == test_create_package.__name__
        assert Path(package.__file__) == package_dir.resolve() / "__init__.py"  # ty:ignore[invalid-argument-type]


def test_tmp_project_root_path(tmp_path: Path, tmp_project_root_path: Path) -> None:
    """Test function."""
    assert tmp_project_root_path == tmp_path / "pyrig"


def test_tmp_source_root_path(
    tmp_project_root_path: Path, tmp_source_root_path: Path
) -> None:
    """Test function."""
    assert tmp_source_root_path == tmp_project_root_path / "src"


def test_tmp_package_root_path(
    tmp_source_root_path: Path, tmp_package_root_path: tuple[Path, ModuleType]
) -> None:
    """Test function."""
    package_root, package = tmp_package_root_path
    assert package_root == tmp_source_root_path / "pyrig"
    assert isinstance(package, ModuleType)
    assert package.__name__ == pyrig.__name__


def test_create_source_package(
    create_source_package: Callable[[Path], ModuleType], tmp_source_root_path: Path
) -> None:
    """Test function."""
    path = Path("package/subpackge")
    package = create_source_package(path)
    assert package.__name__ == path.as_posix().replace("/", ".")
    assert Path(package.__file__) == tmp_source_root_path / path / "__init__.py"  # ty:ignore[invalid-argument-type]


def test_standard_output_error_template(standard_output_error_template: str) -> None:
    """Test function."""
    assert "{stdout}" in standard_output_error_template
    assert "{stderr}" in standard_output_error_template


def test_on_linux_and_latest_python_version(
    *, on_linux_and_latest_python_version: bool
) -> None:
    """Test function."""
    current_platform = platform.system()
    current_version = platform.python_version()
    latest_version = PyprojectConfigFile.I.latest_python_version("micro")
    if current_platform == "Linux" and current_version == str(latest_version):
        assert on_linux_and_latest_python_version is True
    else:
        assert on_linux_and_latest_python_version is False


def test_on_platform(on_platform: Callable[[str], bool]) -> None:
    """Test function."""
    current_platform = platform.system()
    assert on_platform(current_platform) is True


def test_on_linux(*, on_linux: bool) -> None:
    """Test function."""
    current_platform = platform.system()
    if current_platform == "Linux":
        assert on_linux is True
    else:
        assert on_linux is False


def test_on_python_version(on_python_version: Callable[[str], bool]) -> None:
    """Test function."""
    current_version = platform.python_version()
    assert on_python_version(current_version) is True


def test_on_latest_python_version(*, on_latest_python_version: bool) -> None:
    """Test function."""
    latest_version = PyprojectConfigFile.I.latest_python_version("micro")
    current_version = platform.python_version()
    if current_version == str(latest_version):
        assert on_latest_python_version is True
    else:
        assert on_latest_python_version is False


def test_on_linux_and_latest_python_version_or_not_in_ci(
    *, on_linux_and_latest_python_version_or_not_in_ci: bool
) -> None:
    """Test function."""
    in_ci = RemoteVersionController.I.running_in_ci()
    current_platform = platform.system()
    latest_version = PyprojectConfigFile.I.latest_python_version("micro")
    current_version = platform.python_version()
    if (
        current_platform == "Linux" and current_version == str(latest_version)
    ) or not in_ci:
        assert on_linux_and_latest_python_version_or_not_in_ci is True
    else:
        assert on_linux_and_latest_python_version_or_not_in_ci is False


def test_command_calls_function(
    command_calls_function: Callable[[Callable[..., Any], Callable[..., Any]], None],
) -> None:
    """Test function."""
    command_calls_function(mkroot, make_project_root)
