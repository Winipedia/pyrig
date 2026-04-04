"""Path utilities for module and package management.

Runtime utilities for working with Python module and package paths. This module
provides bidirectional conversions between dotted module names and filesystem paths,
support for frozen environments (PyInstaller), and package structure creation.

Part of the ``pyrig.src.modules`` subpackage.

Key Components:
    ModulePath: Static utility class for path/module name conversions.
    make_init_modules_for_package: Recursively create __init__.py files.
    make_dir_with_init_file: Create a directory as a Python package.
    make_init_module: Create a single __init__.py file.
    make_package_dir: Create __init__.py files up the directory hierarchy.
"""

from pathlib import Path
from types import ModuleType

import typer


class ModulePath:
    """Static utility class for module and package path operations.

    Provides bidirectional conversions between Python dotted module/package names
    and filesystem paths. All methods are static and the class is not meant to be
    instantiated.

    Key Operations:
        - Module name → file path: ``module_name_to_relative_file_path``
        - File path → module name: ``relative_path_to_module_name``,
          ``absolute_path_to_module_name``
        - Package name → directory path: ``package_name_to_relative_dir_path``
        - Module/package object → file path: ``module_type_to_file_path``,
          ``package_type_to_dir_path``

    """

    @staticmethod
    def module_type_to_file_path(module: ModuleType) -> Path:
        """Convert an imported module object to its source file path.

        Args:
            module: An imported Python module (e.g., from ``import mymodule``).

        Returns:
            Absolute path to the module's source file.

        Raises:
            ValueError: If the module has no ``__file__`` attribute (e.g.,
                built-in modules or namespace packages).
        """
        file = module.__file__
        if file is None:
            msg = f"Module {module} has no __file__"
            raise ValueError(msg)
        return Path(file)

    @staticmethod
    def package_type_to_dir_path(package: ModuleType) -> Path:
        """Convert an imported package object to its directory path.

        Args:
            package: An imported Python package (a module with an ``__init__.py``).

        Returns:
            Absolute path to the package's directory (parent of ``__init__.py``).
        """
        return ModulePath.module_type_to_file_path(package).parent

    @staticmethod
    def module_name_to_relative_file_path(module_name: str, root: Path) -> Path:
        """Convert a dotted module name to a relative file path.

        Replaces dots with path separators and appends ``.py`` extension.
        Used across pyrig's subsystems (CLI, configs, tests) to locate module files.

        Args:
            module_name: Dotted Python module name
            (e.g., ``'package.subpackage.module'``).
            root: The relative root directory to prepend to the path
                (e.g., ``Path('src')``).

        Returns:
            Relative path to the module file
            (e.g., ``Path('package/subpackage/module.py')``).
        """
        return root / Path(module_name.replace(".", "/") + ".py")

    @staticmethod
    def package_name_to_relative_dir_path(package_name: str, root: Path) -> Path:
        """Convert a dotted package name to a relative directory path.

        Args:
            package_name: Dotted Python package name (e.g., ``'package.subpackage'``).
            root: The relative root directory to prepend to the path
                (e.g., ``Path('src')``).

        Returns:
            Relative path to the package directory
            (e.g., ``Path('package/subpackage')``).
        """
        return root / Path(package_name.replace(".", "/"))

    @staticmethod
    def relative_path_to_module_name(path: Path, root: Path) -> str:
        """Convert a relative file or directory path to a dotted module name.

        Handles both module files (``.py``) and package directories. The file
        extension is stripped if present.

        Args:
            path: Relative path to a module file or package directory
                (e.g., ``Path('package/subpackage/module.py')``
                or ``Path('package/subpackage')``).
            root: The relative root directory to remove from the path
                (e.g., ``Path('src')``).

        Returns:
            Dotted module name (e.g., ``'package.subpackage.module'``
            or ``'package.subpackage'``).
        """
        path = path.relative_to(root)
        return path.as_posix().removesuffix(".py").replace("/", ".")

    @staticmethod
    def absolute_path_to_module_name(path: Path, root: Path) -> str:
        """Convert an absolute or relative file path to a dotted module name.

        For relative paths, converts directly to a module name (e.g.,
        ``Path('package/mod.py')`` → ``'package.mod'``).

        For absolute paths, resolves relative to the current working directory
        (or _MEIPASS in frozen environments) first.

        Args:
            path: Absolute or relative path to a module file or package
                directory. Absolute paths must be within the current working
                directory.
            root: The relative root directory to remove from the path
                (e.g., ``Path('src')``).

        Returns:
            Dotted module name.

        Raises:
            ValueError: If an absolute path is not relative to the CWD
                (raised by ``Path.relative_to``).
        """
        if not path.is_absolute():
            return ModulePath.relative_path_to_module_name(path, root)
        rel_path = path.resolve().relative_to(Path.cwd())
        root = root.resolve().relative_to(Path.cwd())
        return ModulePath.relative_path_to_module_name(rel_path, root)


def default_init_module_content() -> str:
    """Generate the default content for new ``__init__.py`` files.

    Returns:
        A string containing a minimal docstring for the ``__init__`` module.
    """
    return '''"""__init__ module."""
'''


def make_init_module(path: Path) -> None:
    """Create an ``__init__.py`` file in the specified directory.

    Creates the file with default content from ``default_init_module_content``.
    Logs the creation at INFO level.

    Args:
        path: Directory path where ``__init__.py`` should be created.

    Note:
        No-op if ``__init__.py`` already exists in the directory.
    """
    path = path / "__init__.py"

    if path.exists():
        return

    typer.echo(f"Creating: {path}")

    content = default_init_module_content()
    path.write_text(content)


def make_package_dir(path: Path, until: tuple[Path, ...]) -> None:
    """Create a directory and add ``__init__.py`` files up the directory tree.

    Creates the target directory (and missing parents), then adds ``__init__.py``
    files to the target and all parent directories up to (but not including) the
    current working directory. This ensures the entire path is importable as a
    Python package hierarchy.

    Args:
        path: Directory path to create. must be relative to the cwd.
        until: Directory path to stop at when adding ``__init__.py`` files. The
            directory specified by ``until`` will not get an __init__.py


    Note:
        Skips directories that already contain an ``__init__.py`` file.
        Does not create ``__init__.py`` in the CWD itself.
    """
    path.mkdir(parents=True, exist_ok=True)
    until = (*until, Path(), Path.cwd())
    for p in (path, *path.parents):
        if p in until:
            break
        make_init_module(p)
