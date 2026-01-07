"""Path utilities for module and package management.

Runtime utilities for working with Python module and package paths. This module
provides bidirectional conversions between dotted module names and filesystem paths,
support for frozen environments (PyInstaller), and package structure creation.

Part of pyrig's src utilities for production use.

Key Components:
    ModulePath: Static utility class for path/module name conversions.
    make_init_modules_for_package: Recursively create __init__.py files.
    make_dir_with_init_file: Create a directory as a Python package.
    make_init_module: Create a single __init__.py file.
    make_pkg_dir: Create __init__.py files up the directory hierarchy.
"""

import logging
import sys
from pathlib import Path
from types import ModuleType

logger = logging.getLogger(__name__)


class ModulePath:
    """Static utility class for module and package path operations.

    Provides bidirectional conversions between Python dotted module/package names
    and filesystem paths. All methods are static and the class is not meant to be
    instantiated.

    Key Operations:
        - Module name → file path: ``module_name_to_relative_file_path``
        - File path → module name: ``relative_path_to_module_name``,
          ``absolute_path_to_module_name``
        - Package name → directory path: ``pkg_name_to_relative_dir_path``
        - Module/package object → file path: ``module_type_to_file_path``,
          ``pkg_type_to_dir_path``

    Frozen Environment Support:
        Methods ``get_cwd``, ``get_rel_cwd``, ``get_meipass``, and ``in_frozen_env``
        handle PyInstaller frozen executables where files are extracted to a
        temporary ``_MEIPASS`` directory.
    """

    @staticmethod
    def get_cwd() -> Path:
        """Get the base directory for module path resolution.

        In normal execution, returns the current working directory. In frozen
        environments (PyInstaller), returns the _MEIPASS temporary directory
        where bundled files are extracted.

        Returns:
            Absolute path to CWD, or _MEIPASS directory in frozen environment.
        """
        return (
            Path.cwd() if not ModulePath.in_frozen_env() else ModulePath.get_meipass()
        )

    @staticmethod
    def get_rel_cwd() -> Path:
        """Get the relative base path for module path resolution.

        Returns an empty ``Path()`` (representing current directory ".") in normal
        execution. In frozen environments, returns the _MEIPASS path since relative
        paths must be resolved from the extraction directory.

        Returns:
            Empty Path in normal execution, or _MEIPASS in frozen environment.
        """
        return Path() if not ModulePath.in_frozen_env() else ModulePath.get_meipass()

    @staticmethod
    def get_meipass() -> Path:
        """Get the PyInstaller _MEIPASS temporary extraction directory.

        PyInstaller bundles Python files into a single executable and extracts
        them to a temporary directory at runtime. The path is stored in
        ``sys._MEIPASS``.

        Returns:
            Path to _MEIPASS directory, or empty Path("") if not in frozen
            environment.
        """
        return Path(getattr(sys, "_MEIPASS", ""))

    @staticmethod
    def in_frozen_env() -> bool:
        """Check if running in a PyInstaller frozen executable.

        Returns:
            True if ``sys.frozen`` is set (PyInstaller environment),
            False otherwise.
        """
        return getattr(sys, "frozen", False)

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
    def pkg_type_to_dir_path(pkg: ModuleType) -> Path:
        """Convert an imported package object to its directory path.

        Args:
            pkg: An imported Python package (a module with an ``__init__.py``).

        Returns:
            Absolute path to the package's directory (parent of ``__init__.py``).
        """
        return ModulePath.module_type_to_file_path(pkg).parent

    @staticmethod
    def pkg_type_to_file_path(pkg: ModuleType) -> Path:
        """Convert an imported package object to its ``__init__.py`` file path.

        This is an alias for ``module_type_to_file_path`` since a package's
        ``__file__`` attribute points to its ``__init__.py``.

        Args:
            pkg: An imported Python package (a module with an ``__init__.py``).

        Returns:
            Absolute path to the package's ``__init__.py`` file.
        """
        return ModulePath.module_type_to_file_path(pkg)

    @staticmethod
    def module_name_to_relative_file_path(module_name: str) -> Path:
        """Convert a dotted module name to a relative file path.

        Replaces dots with path separators and appends ``.py`` extension.
        Used by pyrig's CLI system to locate module files for dynamic import.

        Args:
            module_name: Dotted Python module name (e.g., ``'pkg.subpkg.module'``).

        Returns:
            Relative path to the module file (e.g., ``Path('pkg/subpkg/module.py')``).
        """
        return Path(module_name.replace(".", "/") + ".py")

    @staticmethod
    def pkg_name_to_relative_dir_path(pkg_name: str) -> Path:
        """Convert a dotted package name to a relative directory path.

        Args:
            pkg_name: Dotted Python package name (e.g., ``'pkg.subpkg'``).

        Returns:
            Relative path to the package directory (e.g., ``Path('pkg/subpkg')``).
        """
        return Path(pkg_name.replace(".", "/"))

    @staticmethod
    def pkg_name_to_relative_file_path(pkg_name: str) -> Path:
        """Convert a dotted package name to its ``__init__.py`` file path.

        Args:
            pkg_name: Dotted Python package name (e.g., ``'pkg.subpkg'``).

        Returns:
            Relative path to the package's ``__init__.py``
            (e.g., ``Path('pkg/subpkg/__init__.py')``).
        """
        return ModulePath.pkg_name_to_relative_dir_path(pkg_name) / "__init__.py"

    @staticmethod
    def relative_path_to_module_name(path: Path) -> str:
        """Convert a relative file or directory path to a dotted module name.

        Handles both module files (``.py``) and package directories. The file
        extension is stripped if present.

        Args:
            path: Relative path to a module file or package directory
                (e.g., ``Path('pkg/subpkg/module.py')`` or ``Path('pkg/subpkg')``).

        Returns:
            Dotted module name (e.g., ``'pkg.subpkg.module'`` or ``'pkg.subpkg'``).
        """
        path = path.with_suffix("")
        return path.as_posix().replace("/", ".")

    @staticmethod
    def absolute_path_to_module_name(path: Path) -> str:
        """Convert an absolute file path to a dotted module name.

        Resolves the path relative to the current working directory (or _MEIPASS
        in frozen environments) and converts to a dotted module name.

        Args:
            path: Absolute path to a module file or package directory. Must be
                within the current working directory.

        Returns:
            Dotted module name.

        Raises:
            ValueError: If the path is not relative to the CWD (raised by
                ``Path.relative_to``).
        """
        cwd = ModulePath.get_cwd()
        rel_path = path.resolve().relative_to(cwd)
        return ModulePath.relative_path_to_module_name(rel_path)


def make_init_modules_for_package(path: Path) -> None:
    """Create ``__init__.py`` files in a directory and all its subdirectories.

    Recursively traverses the directory tree and creates ``__init__.py`` files
    to make every directory a valid Python package. Used by pyrig to ensure
    generated project structures are properly importable.

    Args:
        path: Root directory path to process. The directory itself and all
            subdirectories will receive ``__init__.py`` files.

    Note:
        Skips directories that already contain an ``__init__.py`` file.
    """
    make_init_module(path)
    for p in path.rglob("*"):
        if p.is_dir():
            make_init_module(p)


def make_dir_with_init_file(path: Path) -> None:
    """Create a directory structure and initialize it as a Python package.

    Creates the directory (and any missing parent directories), then adds
    ``__init__.py`` files to the directory and all its subdirectories.

    Args:
        path: Directory path to create. Parent directories are created
            automatically if they don't exist.
    """
    path.mkdir(parents=True, exist_ok=True)
    make_init_modules_for_package(path)


def get_default_init_module_content() -> str:
    """Generate the default content for new ``__init__.py`` files.

    Returns:
        A string containing a minimal docstring for the ``__init__`` module.
    """
    return '''"""__init__ module."""
'''


def make_init_module(path: Path) -> None:
    """Create an ``__init__.py`` file in the specified directory.

    Creates the file with default content from ``get_default_init_module_content``.
    Logs the creation at INFO level.

    Args:
        path: Directory path where ``__init__.py`` should be created.

    Note:
        No-op if ``__init__.py`` already exists in the directory.
    """
    init_path = path / "__init__.py"

    if init_path.exists():
        return

    logger.info("Creating __init__.py file at: %s", init_path)

    content = get_default_init_module_content()
    init_path.write_text(content)


def make_pkg_dir(path: Path) -> None:
    """Create a directory and add ``__init__.py`` files up the directory tree.

    Creates the target directory (and missing parents), then adds ``__init__.py``
    files to the target and all parent directories up to (but not including) the
    current working directory. This ensures the entire path is importable as a
    Python package hierarchy.

    Args:
        path: Directory path to create. Can be absolute or relative. Absolute
            paths are converted to relative paths from the CWD.

    Note:
        Skips directories that already contain an ``__init__.py`` file.
        Does not create ``__init__.py`` in the CWD itself.
    """
    if path.is_absolute():
        path = path.relative_to(Path.cwd())
    path.mkdir(parents=True, exist_ok=True)

    make_init_module(path)
    for p in path.parents:
        if p in (Path.cwd(), Path()):
            continue
        make_init_module(p)
