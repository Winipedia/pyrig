"""test module."""

from collections.abc import Callable
from contextlib import chdir
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

import pyrig
from pyrig.rig.cli.shared_subcommands import version
from pyrig.rig.configs.base.base import ConfigFile


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
        module_path = tmp_path / f"{test_create_module.__name__}.py"
        module = create_module(module_path)
        assert isinstance(module, ModuleType)
        assert module.__name__ == test_create_module.__name__
        assert module.__file__ == str(module_path)


def test_create_package(
    tmp_path: Path, create_package: Callable[[Path], ModuleType]
) -> None:
    """Test function."""
    with chdir(tmp_path):
        package_dir = tmp_path / test_create_package.__name__
        package = create_package(package_dir)
        assert isinstance(package, ModuleType), f"Expected package, got {type(package)}"
        assert package.__name__ == test_create_package.__name__
        assert package.__file__ == str(package_dir / "__init__.py")


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


def test_create_source_module(
    tmp_package_root_path: tuple[Path, ModuleType],
    create_source_module: Callable[[Path], ModuleType],
) -> None:
    """Test function."""
    package_path, _ = tmp_package_root_path
    path = Path(package_path.name) / "module.py"
    module = create_source_module(path)
    assert isinstance(module, ModuleType)
    assert module.__name__ == "pyrig.module"
    assert Path(module.__file__) == package_path / "module.py"  # ty:ignore[invalid-argument-type]
