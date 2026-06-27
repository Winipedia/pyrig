"""Utilities for python modules."""

import sys
from collections.abc import Callable
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from pathlib import Path
from types import ModuleType
from typing import Any

from pyrig_runtime.core.introspection.modules import import_module_with_default

from pyrig.core.introspection.paths import module_file_path, package_dir_path
from pyrig.core.strings import read_text_utf8


def leaf_module_name(module: ModuleType) -> str:
    """Return the last segment of a module's dotted name."""
    return module.__name__.split(".")[-1]


def callable_obj_import_path(obj: Callable[..., Any]) -> str:
    """Return the fully qualified import path of a callable.

    Built by joining the object's module with its qualified name, so the result
    includes any enclosing class (e.g., `"package.module.ClassName.method"`).

    Args:
        obj: Callable (function, method, or class) to resolve.

    Returns:
        The dotted path identifying where the callable is defined.
    """
    return f"{obj.__module__}.{obj.__qualname__}"  # ty:ignore[unresolved-attribute]


def module_content(module: ModuleType) -> str:
    """Read the source code of a module as a string.

    Args:
        module: Module to read. Must have a `__file__` attribute pointing
            to a readable `.py` file.

    Returns:
        Complete source of the module, decoded as UTF-8.

    Raises:
        AttributeError: If the module's `__file__` is `None`
            (e.g., built-in modules or namespace packages).
        FileNotFoundError: If the source file does not exist.
    """
    path = module_file_path(module)
    return read_text_utf8(path)


def reimport_module(module: ModuleType, *, is_package: bool = False) -> ModuleType:
    """Re-import a module, bypassing the import cache.

    Evicts the module from `sys.modules` and re-imports it via
    `import_module_with_file_fallback`. Use this to pick up on-disk changes
    to a module's source without restarting the interpreter.

    Args:
        module: Module to re-import.
        is_package: Set to `True` when re-importing a package from its
            `__init__.py` so the spec is built with package semantics
            (e.g., relative imports). Defaults to `False` for regular modules.

    Returns:
        A freshly imported module object, distinct from the original.
    """
    module_path = package_dir_path(module) if is_package else module_file_path(module)
    # Remove from cache
    del sys.modules[module.__name__]
    return import_module_with_file_fallback(
        module_path, name=module.__name__, is_package=is_package
    )


def import_module_with_file_fallback(
    path: Path, name: str, *, is_package: bool = False
) -> ModuleType:
    """Import a module by name, falling back to direct file import on failure.

    First attempts a standard import of `name`; if that raises any exception,
    falls back to `import_module_from_file`, loading directly from `path`.
    The fallback handles modules that are not on `sys.path` or not installed.

    Args:
        path: Path to the module file, used only by the file-import fallback.
        name: Name under which to register the imported module.
        is_package: Set to `True` when importing a package from its
            `__init__.py` so the spec is built with package semantics
            (e.g., relative imports). Defaults to `False` for regular modules.

    Returns:
        The imported module.

    Raises:
        FileNotFoundError: If the standard import fails and the file does not
            exist.
        ImportError: If the standard import fails and the module spec cannot be
            created.
    """
    module = import_module_with_default(name)
    if isinstance(module, ModuleType):
        return module
    return import_module_from_file(path, name=name, is_package=is_package)


def import_module_from_file(
    path: Path, name: str, *, is_package: bool = False
) -> ModuleType:
    """Import a module directly from a `.py` file, bypassing `sys.path`.

    The module is registered in `sys.modules` under `name` before execution so
    that packages with internal imports can find themselves, and is removed
    again if execution fails, leaving no invalid cache entry behind.

    Args:
        path: Path to the source file; resolved to an absolute path. When
            `is_package` is `True` and the path is not already an `__init__.py`,
            `__init__.py` is appended to it.
        name: Name under which to register the imported module.
        is_package: Set to `True` when importing a package from its
            `__init__.py` so the spec is built with package semantics
            (e.g., relative imports). Defaults to `False` for regular modules.

    Returns:
        The imported and executed module.

    Raises:
        ImportError: If the module spec cannot be created.
        FileNotFoundError: If the file does not exist or cannot be read.
    """
    path = path.resolve()
    if is_package and path.name != "__init__.py":
        path = path / "__init__.py"
    loader = SourceFileLoader(name, str(path))
    spec = spec_from_loader(name=name, loader=loader, is_package=is_package)
    if spec is None:
        msg = f"Could not create spec for {path}"
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
    """Return whether the module defines a docstring (`__doc__` is not `None`)."""
    return module.__doc__ is not None
