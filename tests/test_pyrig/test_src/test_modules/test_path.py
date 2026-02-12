"""module."""

from contextlib import chdir
from pathlib import Path

from pyrig.src.modules.module import create_module
from pyrig.src.modules.package import create_package
from pyrig.src.modules.path import (
    ModulePath,
    default_init_module_content,
    make_dir_with_init_file,
    make_init_module,
    make_init_modules_for_package,
    make_package_dir,
)


def test_make_init_modules_for_package(tmp_path: Path) -> None:
    """Test function."""
    with chdir(tmp_path):
        package_path = tmp_path / "test_package"
        path = package_path / "subdir1" / "subdir2"
        path.mkdir(parents=True)
        make_init_modules_for_package(package_path)
        assert (Path.cwd() / "test_package" / "__init__.py").exists()
        assert (Path.cwd() / "test_package" / "subdir1" / "__init__.py").exists()
        assert (
            Path.cwd() / "test_package" / "subdir1" / "subdir2" / "__init__.py"
        ).exists()


def test_make_dir_with_init_file(tmp_path: Path) -> None:
    """Test function."""
    with chdir(tmp_path):
        test_dir = Path.cwd() / "test_package" / "subdir1" / "subdir2"
        make_dir_with_init_file(test_dir)
        assert test_dir.exists()
        assert test_dir.is_dir()
        assert (test_dir / "__init__.py").exists()


def test_default_init_module_content() -> None:
    """Test function."""
    result = default_init_module_content()
    # assert is str
    assert isinstance(result, str), f"Expected str, got {type(result)}"


def test_make_init_module(tmp_path: Path) -> None:
    """Test function."""
    with chdir(tmp_path):
        make_init_module(Path.cwd())
        assert (Path.cwd() / "__init__.py").exists(), (
            "Expected __init__.py file to be created"
        )


def test_make_package_dir(tmp_path: Path) -> None:
    """Test function."""
    with chdir(tmp_path):
        mpath = Path.cwd() / "test" / "package"
        make_package_dir(mpath)
        assert (Path.cwd() / "test" / "__init__.py").exists(), (
            "Expected __init__.py file to be created"
        )
        assert (Path.cwd() / "test" / "package" / "__init__.py").exists(), (
            "Expected __init__.py file to be created"
        )
        assert not (Path.cwd() / "__init__.py").exists(), (
            "Did not expect __init__.py file to be created"
        )


class TestModulePath:
    """Test class."""

    def test_cwd(self, tmp_path: Path) -> None:
        """Test method."""
        with chdir(tmp_path):
            assert ModulePath.cwd() == tmp_path

    def test_rel_cwd(self, tmp_path: Path) -> None:
        """Test method."""
        with chdir(tmp_path):
            assert ModulePath.rel_cwd() == Path()

    def test_meipass(self) -> None:
        """Test method."""
        assert ModulePath.meipass() == Path()

    def test_in_frozen_env(self) -> None:
        """Test method."""
        assert ModulePath.in_frozen_env() is False

    def test_module_type_to_file_path(self, tmp_path: Path) -> None:
        """Test method."""
        test_module_name = self.test_module_type_to_file_path.__name__
        with chdir(tmp_path):
            test_module_name = test_module_name + ".py"
            module_path = tmp_path / test_module_name
            module = create_module(module_path)
            assert ModulePath.module_type_to_file_path(module) == module_path
            assert module.__file__ == str(module_path)

    def test_package_type_to_dir_path(self, tmp_path: Path) -> None:
        """Test method."""
        test_package_name = self.test_package_type_to_dir_path.__name__
        with chdir(tmp_path):
            package_path = tmp_path / test_package_name
            package = create_package(package_path)
            assert ModulePath.package_type_to_dir_path(package) == package_path

    def test_package_type_to_file_path(self, tmp_path: Path) -> None:
        """Test method."""
        test_package_name = self.test_package_type_to_file_path.__name__
        with chdir(tmp_path):
            package_path = tmp_path / test_package_name
            package = create_package(package_path)
            assert (
                ModulePath.package_type_to_file_path(package)
                == package_path / "__init__.py"
            )

    def test_module_name_to_relative_file_path(self) -> None:
        """Test method."""
        name = self.test_module_name_to_relative_file_path.__name__ + "." + "module"
        path = ModulePath.module_name_to_relative_file_path(name)
        assert path == Path(name.replace(".", "/") + ".py")

    def test_package_name_to_relative_dir_path(self) -> None:
        """Test method."""
        name = self.test_package_name_to_relative_dir_path.__name__ + "." + "package"
        path = ModulePath.package_name_to_relative_dir_path(name)
        assert path == Path(name.replace(".", "/"))

    def test_package_name_to_relative_file_path(self) -> None:
        """Test method."""
        name = self.test_package_name_to_relative_file_path.__name__ + "." + "package"
        path = ModulePath.package_name_to_relative_file_path(name)
        assert path == Path(name.replace(".", "/") + "/__init__.py")

    def test_relative_path_to_module_name(self) -> None:
        """Test method."""
        path = Path("test/package.py")
        name = ModulePath.relative_path_to_module_name(path)
        assert name == "test.package"

    def test_absolute_path_to_module_name(self, tmp_path: Path) -> None:
        """Test method."""
        with chdir(tmp_path):
            path = tmp_path / "test_module.py"
            name = ModulePath.absolute_path_to_module_name(path)
            assert name == "test_module"

        # Test that relative paths are converted directly without resolving
        path = Path("video_vault/src/ui/pages/add_downloads.py")
        name = ModulePath.absolute_path_to_module_name(path)
        assert name == "video_vault.src.ui.pages.add_downloads"
