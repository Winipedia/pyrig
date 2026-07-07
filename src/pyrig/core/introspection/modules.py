"""Utilities for loading, re-loading, and introspecting Python modules."""

import sys
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from pathlib import Path
from types import ModuleType

from pyrig_runtime.core.introspection.modules import safe_import_module
from pyrig_runtime.core.introspection.packages import is_package

from pyrig.core.introspection.paths import module_file_path, package_dir_path
from pyrig.core.strings import read_text_utf8


def leaf_module_name(module: ModuleType) -> str:
    """Return the last segment of a module's dotted name."""
    return module.__name__.split(".")[-1]


def module_content(module: ModuleType) -> str:
    """Read the source code of a module as a string.

    Args:
        module: Module to read.

    Returns:
        Complete source of the module, decoded as UTF-8.

    Raises:
        AttributeError: If the module's `__file__` is `None`
            (e.g., built-in modules or namespace packages).
        FileNotFoundError: If the source file does not exist.
    """
    path = module_file_path(module)
    return read_text_utf8(path)


def reimport_module(module: ModuleType) -> ModuleType:
    """Re-import a module, bypassing the import cache.

    Evicts the module from `sys.modules` before re-importing it, so on-disk
    changes to the module's source are picked up without restarting the
    interpreter. Packages and plain modules are both handled.

    Args:
        module: Module to re-import.

    Returns:
        A freshly imported module object, distinct from the original.

    Raises:
        AttributeError: If the module's `__file__` is `None`
            (e.g., built-in modules or namespace packages).
    """
    module_path = (
        package_dir_path(module) if is_package(module) else module_file_path(module)
    )
    del sys.modules[module.__name__]
    return import_module_with_file_fallback(module_path, name=module.__name__)


def import_module_with_file_fallback(path: Path, name: str) -> ModuleType:
    """Import a module by name, falling back to direct file import on failure.

    Attempts a standard import of `name`; if that fails for any reason,
    loads the module directly from `path`. This handles modules that are not
    on `sys.path` or not installed.

    Args:
        path: Path to the module file, used only when the standard import fails.
        name: Name under which to register the imported module.

    Returns:
        The imported module.

    Raises:
        FileNotFoundError: If the standard import fails and the file does not
            exist.
        ImportError: If the standard import fails and the module spec cannot be
            created.
    """
    module = safe_import_module(name, default=None)
    if module is not None:
        return module
    return import_module_from_file(path, name=name)


def import_module_from_file(path: Path, name: str) -> ModuleType:
    """Import a module directly from a `.py` file, bypassing `sys.path`.

    The module is registered in `sys.modules` under `name` before execution so
    that packages with internal imports can find themselves, and is removed
    again if execution fails, leaving no invalid cache entry behind.

    Args:
        path: Path to the source file or package directory; resolved to an
            absolute path. A directory is treated as a package, and
            `__init__.py` is appended to it.
        name: Name under which to register the imported module.

    Returns:
        The imported and executed module.

    Raises:
        ImportError: If the module spec cannot be created.
        FileNotFoundError: If the file does not exist.
    """
    path = path.resolve()
    path_name = path.name
    is_pkg = path.is_dir() or path_name == "__init__.py"
    if is_pkg and path_name != "__init__.py":
        path = path / "__init__.py"
    loader = SourceFileLoader(name, str(path))
    spec = spec_from_loader(name=name, loader=loader, is_package=is_pkg)
    if spec is None:
        msg = f"could not create spec for {path}"
        raise ImportError(msg)

    module = module_from_spec(spec)
    sys.modules[name] = module
    try:
        loader.exec_module(module)
    except Exception:
        del sys.modules[name]
        raise
    return module


def module_has_docstring(module: ModuleType) -> bool:
    """Return whether the module defines a docstring."""
    return module.__doc__ is not None
