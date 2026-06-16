"""test module."""

from collections.abc import Callable
from contextlib import chdir
from pathlib import Path
from types import ModuleType


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


def test_create_source_package(
    create_source_package: Callable[[Path], ModuleType], tmp_source_root_path: Path
) -> None:
    """Test function."""
    path = Path("package/subpackge")
    package = create_source_package(path)
    assert package.__name__ == path.as_posix().replace("/", ".")
    assert Path(package.__file__) == tmp_source_root_path / path / "__init__.py"  # ty:ignore[invalid-argument-type]
