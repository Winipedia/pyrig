"""Utilities for Python packages."""

from collections.abc import Iterable, Iterator
from pathlib import Path
from types import ModuleType

import typer
from pyrig_runtime.core.introspection.packages import walk_package

from pyrig.core.introspection.modules import (
    import_module_with_file_fallback,
)
from pyrig.core.strings import write_text_utf8


def make_package_dir(path: Path, until: tuple[Path, ...], content: str) -> None:
    """Create a directory and add `__init__.py` files up the directory tree.

    Creates the target directory (and all missing parents), then places
    `__init__.py` files in the target directory and each ancestor up the
    tree. Traversal stops at the first directory (starting from the target
    itself, then its ancestors) that appears in `until`. Existing
    `__init__.py` files are not overwritten.

    Args:
        path: Directory path to create.
        until: Directories at which to stop adding `__init__.py` files.
            Directories in this tuple do not receive an `__init__.py`. The
            current working directory and the empty path are always
            implicitly included as stop points.
        content: Content to write into each `__init__.py` file.
    """
    path.mkdir(parents=True, exist_ok=True)
    until = (*until, Path(), Path.cwd())
    for p in (path, *path.parents):
        if p in until:
            break
        make_init_file(p, content=content)


def make_init_files(paths: Iterable[Path], content: str) -> tuple[Path, ...]:
    """Create `__init__.py` files in the given directories.

    Writes an `__init__.py` with the given content into each directory.
    Skips any directory that already has an `__init__.py`.

    Args:
        paths: Paths of directories to initialize as packages.
        content: Content to write into each `__init__.py` file.

    Returns:
        Tuple of paths where `__init__.py` files were created.
        Empty if all already existed.
    """
    return tuple(path for path in paths if make_init_file(path, content))


def make_init_file(path: Path, content: str) -> bool:
    """Create an `__init__.py` file in the specified directory.

    Echoes `Creating: <path>/__init__.py` to stdout when a file is created.
    No-op if `__init__.py` already exists in the directory.

    Args:
        path: Directory path where `__init__.py` should be created.
        content: Content to write into the `__init__.py` file.

    Returns:
        `True` if the file was created, `False` if it already existed.
    """
    path = path / "__init__.py"

    if path.exists():
        return False

    typer.echo(f"Creating: {path}")

    write_text_utf8(path, content)
    return True


def import_package_with_dir_fallback(path: Path, name: str) -> ModuleType:
    """Import a package by name, falling back to a direct directory import if needed.

    Attempts a standard import of `name` first. If that fails for any reason,
    imports the package directly from the directory at `path`. The fallback
    handles packages not yet on `sys.path`, such as dynamically created
    packages or packages in non-standard locations.

    Args:
        path: Path to the package directory. Resolved to an absolute path
            before the fallback import is attempted.
        name: Dotted module name for the package (e.g., `"myproject.utils"`).

    Returns:
        Imported package module.

    Raises:
        FileNotFoundError: If the fallback import is needed and the directory
            or its `__init__.py` does not exist.
        ImportError: If the fallback import is needed and the module spec
            cannot be created from the path.
    """
    return import_module_with_file_fallback(path=path, name=name, is_package=True)


def discover_modules(package: ModuleType) -> Iterator[ModuleType]:
    """Recursively discover all modules (non-packages) in a package.

    Walks the entire package hierarchy and yields only the leaf modules,
    excluding intermediate sub-packages. Each module is imported as a
    side effect of iteration.

    Args:
        package: Root package to discover modules from.

    Yields:
        Every module found anywhere within the package hierarchy, excluding
        sub-packages themselves.
    """
    return (module for module, is_pkg in walk_package(package) if not is_pkg)
