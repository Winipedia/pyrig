"""module."""

from collections.abc import Callable
from contextlib import chdir
from pathlib import Path
from types import ModuleType

from pyrig.core.modules.path import (
    ModulePath,
)


class TestModulePath:
    """Test class."""

    def test_module_type_to_file_path(
        self, tmp_path: Path, create_module: Callable[[Path], ModuleType]
    ) -> None:
        """Test method."""
        test_module_name = self.test_module_type_to_file_path.__name__
        with chdir(tmp_path):
            test_module_name = test_module_name + ".py"
            module_path = tmp_path / test_module_name
            module = create_module(module_path)
            assert ModulePath.module_type_to_file_path(module) == module_path
            assert module.__file__ == str(module_path)

    def test_package_type_to_dir_path(
        self, tmp_path: Path, create_package: Callable[[Path], ModuleType]
    ) -> None:
        """Test method."""
        test_package_name = self.test_package_type_to_dir_path.__name__
        with chdir(tmp_path):
            package_path = tmp_path / test_package_name
            package = create_package(package_path)
            assert ModulePath.package_type_to_dir_path(package) == package_path

    def test_module_name_to_relative_file_path(self) -> None:
        """Test method."""
        name = self.test_module_name_to_relative_file_path.__name__ + "." + "module"
        path = ModulePath.module_name_to_relative_file_path(name, root=Path("src"))
        assert path == Path("src") / Path(name.replace(".", "/") + ".py")

    def test_package_name_to_relative_dir_path(self) -> None:
        """Test method."""
        name = self.test_package_name_to_relative_dir_path.__name__ + "." + "package"
        path = ModulePath.package_name_to_relative_dir_path(name, root=Path())
        assert path == Path(name.replace(".", "/"))

    def test_relative_path_to_module_name(self) -> None:
        """Test method."""
        path = Path("src/test/package.py")
        name = ModulePath.relative_path_to_module_name(path, root=Path("src"))
        assert name == "test.package"

    def test_absolute_path_to_module_name(self, tmp_path: Path) -> None:
        """Test method."""
        with chdir(tmp_path):
            path = tmp_path / "test_module.py"
            name = ModulePath.absolute_path_to_module_name(path, root=Path())
            assert name == "test_module"

        # Test that relative paths are converted directly without resolving
        path = Path("project/core/ui/pages/add_downloads.py")
        name = ModulePath.absolute_path_to_module_name(path, root=Path())
        assert name == "project.core.ui.pages.add_downloads"
