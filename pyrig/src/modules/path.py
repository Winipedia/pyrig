"""Path utilities for module and package management.

This module provides utilities for working with Python module and package paths,
including support for frozen environments (PyInstaller) and conversions between
module names and file paths.
"""

import sys
from pathlib import Path
from types import ModuleType


class ModulePath:
    """Utility class for handling module and package path operations.

    Provides static methods for converting between module names and file paths,
    handling frozen environments (PyInstaller), and working with Python package
    structures. All methods are static and do not require instantiation.
    """

    @staticmethod
    def get_cwd() -> Path:
        """Get the current working directory, accounting for frozen environments.

        Returns the actual current working directory in normal Python execution,
        or the PyInstaller temporary directory (_MEIPASS) when running in a
        frozen environment.

        Returns:
            Path: The current working directory path.
        """
        return (
            Path.cwd() if not ModulePath.in_frozen_env() else ModulePath.get_meipass()
        )

    @staticmethod
    def get_rel_cwd() -> Path:
        """Get a relative current working directory path.

        Returns an empty Path in normal execution, or the PyInstaller temporary
        directory (_MEIPASS) when running in a frozen environment. Useful for
        constructing relative paths that work in both contexts.

        Returns:
            Path: An empty Path or the _MEIPASS path in frozen environments.
        """
        return Path() if not ModulePath.in_frozen_env() else ModulePath.get_meipass()

    @staticmethod
    def get_meipass() -> Path:
        """Get the PyInstaller _MEIPASS temporary directory path.

        Returns the temporary directory path where PyInstaller extracts bundled
        files when running a frozen application. Returns an empty Path if not
        in a frozen environment.

        Returns:
            Path: The _MEIPASS directory path, or an empty Path if not frozen.
        """
        return Path(getattr(sys, "_MEIPASS", ""))

    @staticmethod
    def in_frozen_env() -> bool:
        """Check if the code is running in a frozen environment.

        Determines whether the application is running as a PyInstaller frozen
        executable or as a normal Python script.

        Returns:
            bool: True if running in a frozen environment, False otherwise.
        """
        return getattr(sys, "frozen", False)

    @staticmethod
    def module_type_to_file_path(module: ModuleType) -> Path:
        """Convert a module object to its file path.

        Extracts the file path from a module object's __file__ attribute.

        Args:
            module (ModuleType): The module object to get the file path from.

        Raises:
            ValueError: If the module has no __file__ attribute
                (e.g., built-in modules).

        Returns:
            Path: The absolute path to the module's file.
        """
        file = module.__file__
        if file is None:
            msg = f"Module {module} has no __file__"
            raise ValueError(msg)
        return Path(file)

    @staticmethod
    def pkg_type_to_dir_path(pkg: ModuleType) -> Path:
        """Convert a package object to its directory path.

        Extracts the directory path containing a package by getting the parent
        directory of the package's __init__.py file.

        Args:
            pkg (ModuleType): The package object to get the directory path from.

        Returns:
            Path: The absolute path to the package's directory.
        """
        return ModulePath.module_type_to_file_path(pkg).parent

    @staticmethod
    def pkg_type_to_file_path(pkg: ModuleType) -> Path:
        """Convert a package object to its __init__.py file path.

        Extracts the file path to a package's __init__.py file.

        Args:
            pkg (ModuleType): The package object to get the file path from.

        Returns:
            Path: The absolute path to the package's __init__.py file.
        """
        return ModulePath.module_type_to_file_path(pkg)

    @staticmethod
    def module_name_to_relative_file_path(module_name: str) -> Path:
        """Convert a dotted module name to a relative file path.

        Transforms a Python module name (e.g., 'pkg.subpkg.module') into a
        relative file path (e.g., 'pkg/subpkg/module.py').

        Args:
            module_name (str): The dotted module name to convert.

        Returns:
            Path: The relative path to the module file.
        """
        # gets smth like pkg.subpkg.module and turns into smth like pkg/subpkg/module.py
        return Path(module_name.replace(".", "/") + ".py")

    @staticmethod
    def pkg_name_to_relative_dir_path(pkg_name: str) -> Path:
        """Convert a dotted package name to a relative directory path.

        Transforms a Python package name (e.g., 'pkg.subpkg') into a relative
        directory path (e.g., 'pkg/subpkg').

        Args:
            pkg_name (str): The dotted package name to convert.

        Returns:
            Path: The relative path to the package directory.
        """
        return Path(pkg_name.replace(".", "/"))

    @staticmethod
    def pkg_name_to_relative_file_path(pkg_name: str) -> Path:
        """Convert a dotted package name to a relative __init__.py path.

        Transforms a Python package name (e.g., 'pkg.subpkg') into a relative
        path to its __init__.py file (e.g., 'pkg/subpkg/__init__.py').

        Args:
            pkg_name (str): The dotted package name to convert.

        Returns:
            Path: The relative path to the package's __init__.py file.
        """
        return ModulePath.pkg_name_to_relative_dir_path(pkg_name) / "__init__.py"

    @staticmethod
    def relative_path_to_module_name(path: Path) -> str:
        """Convert a relative file path to a dotted module name.

        Transforms a relative file path (e.g., 'pkg/subpkg/module.py' or
        'pkg/subpkg') into a Python module name (e.g., 'pkg.subpkg.module'
        or 'pkg.subpkg').

        Args:
            path (Path): The relative path to convert.

        Returns:
            str: The dotted module name.
        """
        # we have smth like pkg/subpkg/module.py and want  pkg.subpkg.module
        # or we have pkg/subpkg and want pkg.subpkg
        path = path.with_suffix("")
        return path.as_posix().replace("/", ".")

    @staticmethod
    def absolute_path_to_module_name(path: Path) -> str:
        """Convert an absolute file path to a dotted module name.

        Transforms an absolute file path into a Python module name by first
        converting it to a relative path from the current working directory,
        then converting to dotted notation.

        Args:
            path (Path): The absolute path to convert.

        Returns:
            str: The dotted module name.
        """
        cwd = ModulePath.get_cwd()
        rel_path = path.resolve().relative_to(cwd)
        return ModulePath.relative_path_to_module_name(rel_path)


def make_init_modules_for_package(path: Path) -> None:
    """Create __init__.py files in all subdirectories of a package.

    Ensures that all subdirectories of the given package have __init__.py files,
    effectively converting them into proper Python packages. Skips directories
    that match patterns in .gitignore.

    Args:
        path: The package path or module object to process

    Note:
        Does not modify directories that already have __init__.py files.
        Uses the default content for __init__.py files
        from get_default_init_module_content.

    """
    # create init files in all subdirectories and in the root
    make_init_module(path)
    for p in path.rglob("*"):
        if p.is_dir():
            make_init_module(p)


def make_dir_with_init_file(path: Path) -> None:
    """Create a directory and add __init__.py files to make it a package.

    Args:
        path: The directory path to create and initialize as a package

    """
    path.mkdir(parents=True, exist_ok=True)
    make_init_modules_for_package(path)


def get_default_init_module_content() -> str:
    """Generate standardized content for an __init__.py file.

    Creates a simple docstring for an __init__.py file based on its location,
    following the project's documentation conventions.

    Args:
        path: The path to the __init__.py file or its parent directory

    Returns:
        A string containing a properly formatted docstring for the __init__.py file

    """
    return '''"""__init__ module."""
'''


def make_init_module(path: Path) -> None:
    """Create an __init__.py file in the specified directory.

    Creates an __init__.py file with default content in the given directory,
    making it a proper Python package.

    Args:
        path: The directory path where the __init__.py file should be created

    Note:
        If the path already points to an __init__.py file, that file will be
        overwritten with the default content.
        Creates parent directories if they don't exist.

    """
    init_path = path / "__init__.py"

    if init_path.exists():
        return

    content = get_default_init_module_content()
    init_path.write_text(content)


def make_pkg_dir(path: Path) -> None:
    """Create __init__.py files in all parent directories of a path.

    It does not include the CWD.

    Args:
        path: The path to create __init__.py files for

    Note:
        Does not modify directories that already have __init__.py files.
        Uses the default content for __init__.py files
        from get_default_init_module_content.

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
