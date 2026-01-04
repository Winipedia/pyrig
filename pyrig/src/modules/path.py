"""Path utilities for module and package management.

Utilities for working with Python module and package paths, including bidirectional
conversions between module names and file paths, support for frozen environments
(PyInstaller), and package structure creation.
"""

import logging
import sys
from pathlib import Path
from types import ModuleType

logger = logging.getLogger(__name__)


class ModulePath:
    """Utility class for module and package path operations.

    Static methods for converting between module names and file paths, handling frozen
    environments (PyInstaller), and working with Python package structures.
    """

    @staticmethod
    def get_cwd() -> Path:
        """Get current working directory, accounting for frozen environments.

        Returns:
            CWD path or _MEIPASS in frozen environment.
        """
        return (
            Path.cwd() if not ModulePath.in_frozen_env() else ModulePath.get_meipass()
        )

    @staticmethod
    def get_rel_cwd() -> Path:
        """Get relative current working directory path.

        Returns:
            Empty Path or _MEIPASS in frozen environment.
        """
        return Path() if not ModulePath.in_frozen_env() else ModulePath.get_meipass()

    @staticmethod
    def get_meipass() -> Path:
        """Get PyInstaller _MEIPASS temporary directory path.

        Returns:
            _MEIPASS directory path, or empty Path if not frozen.
        """
        return Path(getattr(sys, "_MEIPASS", ""))

    @staticmethod
    def in_frozen_env() -> bool:
        """Check if running in a frozen environment (PyInstaller).

        Returns:
            True if frozen, False otherwise.
        """
        return getattr(sys, "frozen", False)

    @staticmethod
    def module_type_to_file_path(module: ModuleType) -> Path:
        """Convert a module object to its file path.

        Args:
            module: Module object.

        Returns:
            Absolute path to module's file.

        Raises:
            ValueError: If module has no __file__ attribute.
        """
        file = module.__file__
        if file is None:
            msg = f"Module {module} has no __file__"
            raise ValueError(msg)
        return Path(file)

    @staticmethod
    def pkg_type_to_dir_path(pkg: ModuleType) -> Path:
        """Convert a package object to its directory path.

        Args:
            pkg: Package object.

        Returns:
            Absolute path to package's directory.
        """
        return ModulePath.module_type_to_file_path(pkg).parent

    @staticmethod
    def pkg_type_to_file_path(pkg: ModuleType) -> Path:
        """Convert a package object to its __init__.py file path.

        Args:
            pkg: Package object.

        Returns:
            Absolute path to package's __init__.py file.
        """
        return ModulePath.module_type_to_file_path(pkg)

    @staticmethod
    def module_name_to_relative_file_path(module_name: str) -> Path:
        """Convert dotted module name to relative file path.

        Args:
            module_name: Dotted module name (e.g., 'pkg.subpkg.module').

        Returns:
            Relative path to module file (e.g., 'pkg/subpkg/module.py').
        """
        # gets smth like pkg.subpkg.module and turns into smth like pkg/subpkg/module.py
        return Path(module_name.replace(".", "/") + ".py")

    @staticmethod
    def pkg_name_to_relative_dir_path(pkg_name: str) -> Path:
        """Convert dotted package name to relative directory path.

        Args:
            pkg_name: Dotted package name (e.g., 'pkg.subpkg').

        Returns:
            Relative path to package directory (e.g., 'pkg/subpkg').
        """
        return Path(pkg_name.replace(".", "/"))

    @staticmethod
    def pkg_name_to_relative_file_path(pkg_name: str) -> Path:
        """Convert dotted package name to relative __init__.py path.

        Args:
            pkg_name: Dotted package name.

        Returns:
            Relative path to package's __init__.py file.
        """
        return ModulePath.pkg_name_to_relative_dir_path(pkg_name) / "__init__.py"

    @staticmethod
    def relative_path_to_module_name(path: Path) -> str:
        """Convert relative file path to dotted module name.

        Args:
            path: Relative path to convert.

        Returns:
            Dotted module name.
        """
        # we have smth like pkg/subpkg/module.py and want  pkg.subpkg.module
        # or we have pkg/subpkg and want pkg.subpkg
        path = path.with_suffix("")
        return path.as_posix().replace("/", ".")

    @staticmethod
    def absolute_path_to_module_name(path: Path) -> str:
        """Convert absolute file path to dotted module name.

        Args:
            path: Absolute path to convert.

        Returns:
            Dotted module name.
        """
        cwd = ModulePath.get_cwd()
        rel_path = path.resolve().relative_to(cwd)
        return ModulePath.relative_path_to_module_name(rel_path)


def make_init_modules_for_package(path: Path) -> None:
    """Create __init__.py files in all subdirectories of a package.

    Args:
        path: Package path to process.

    Note:
        Does not modify directories that already have __init__.py files.
    """
    # create init files in all subdirectories and in the root
    make_init_module(path)
    for p in path.rglob("*"):
        if p.is_dir():
            make_init_module(p)


def make_dir_with_init_file(path: Path) -> None:
    """Create a directory and add __init__.py files to make it a package.

    Args:
        path: Directory path to create and initialize.
    """
    path.mkdir(parents=True, exist_ok=True)
    make_init_modules_for_package(path)


def get_default_init_module_content() -> str:
    """Generate default content for an __init__.py file.

    Returns:
        String containing default __init__.py content.
    """
    return '''"""__init__ module."""
'''


def make_init_module(path: Path) -> None:
    """Create an __init__.py file in the specified directory.

    Args:
        path: Directory path where __init__.py should be created.

    Note:
        Skips if __init__.py already exists.
    """
    init_path = path / "__init__.py"

    if init_path.exists():
        return

    logger.info("Creating __init__.py file at: %s", init_path)

    content = get_default_init_module_content()
    init_path.write_text(content)


def make_pkg_dir(path: Path) -> None:
    """Create __init__.py files in a directory and all its parent directories.

    Does not include the CWD.

    Args:
        path: Path to create __init__.py files for.

    Note:
        Does not modify directories that already have __init__.py files.
    """
    if path.is_absolute():
        path = path.relative_to(Path.cwd())
    # mkdir all parents
    path.mkdir(parents=True, exist_ok=True)

    make_init_module(path)
    for p in path.parents:
        if p in (Path.cwd(), Path()):
            continue
        make_init_module(p)
