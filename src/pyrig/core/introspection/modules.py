"""Utilities for dynamically importing, introspecting, and traversing Python modules.

Covers importing by name or file path with fallback strategies, reading module
source, resolving callable import paths, and iterating direct package children.
Includes support for modules not discoverable via standard import mechanisms,
such as those absent from `sys.path` or not installed as distributions.
"""

import logging
import sys
from collections.abc import Callable, Iterable, Iterator
from importlib import import_module
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from pathlib import Path
from pkgutil import iter_modules as pkgutil_iter_modules
from types import ModuleType
from typing import Any

from pyrig.core.introspection.paths import module_file_path, package_dir_path
from pyrig.core.strings import read_text_utf8

logger = logging.getLogger(__name__)


def leaf_module_name(module: ModuleType) -> str:
    """Return the last segment of a module's dotted name."""
    return module.__name__.split(".")[-1]


def root_module(module: ModuleType) -> ModuleType:
    """Import and return the top-level package of the given module.

    For a module named `"package.subpackage.module"`, the module corresponding
    to `"package"` is returned. For a top-level module with no dots in its name,
    the module for that same name is returned.

    Args:
        module: Module to resolve the root package for.

    Returns:
        The module corresponding to the first segment of the dotted name.
    """
    return import_module(module.__name__.split(".")[0])


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


def import_module_with_default(
    module_name: str, default: Any = None
) -> ModuleType | Any:
    """Import a module by name, returning a default value if import fails.

    Catches every exception, not just `ImportError`, and logs a debug message
    including the caught exception before falling back to the default.

    Args:
        module_name: Dotted module name (e.g., `"package.subpackage.module"`).
        default: Value to return if the import raises. Defaults to `None`.

    Returns:
        The imported module, or `default` if any exception is raised.
    """
    try:
        return import_module(module_name)
    except Exception as e:  # noqa: BLE001
        logger.debug(
            "Could not import module %s, returning default value %s. Exception: %s",
            module_name,
            default,
            e,
        )
        return default


def module_name_replacing_start_module(
    module: ModuleType, new_start_module_name: str
) -> str:
    """Replace the root package segment in a module's fully qualified name.

    Only the first segment is replaced; later segments are left untouched even
    if they happen to share the old root's name. Useful for mapping modules
    between parallel package hierarchies (e.g., source modules to their test
    equivalents).

    Args:
        module: Module whose name to transform.
        new_start_module_name: Root package name to substitute in.

    Returns:
        The module name with its first dotted segment replaced.

    Example:
        >>> from types import ModuleType
        >>> mod = ModuleType("pyrig.rig.configs.base")
        >>> module_name_replacing_start_module(mod, "my_project")
        'my_project.rig.configs.base'
    """
    module_current_start = module.__name__.split(".")[0]
    return module.__name__.replace(module_current_start, new_start_module_name, 1)


def module_has_docstring(module: ModuleType) -> bool:
    """Return whether the module defines a docstring (`__doc__` is not `None`)."""
    return module.__doc__ is not None


def import_modules(module_names: Iterable[str]) -> Iterator[ModuleType]:
    """Import multiple modules by name, lazily.

    Modules are imported on demand as the result is iterated, not eagerly.

    Args:
        module_names: Dotted module names to import.

    Yields:
        Each imported module, in the order the names are iterated.
    """
    return (import_module(name) for name in module_names)


def iter_modules(package: ModuleType) -> Iterator[tuple[ModuleType, bool]]:
    """Import and yield each direct child of a package, in discovery order.

    Only the immediate children are visited; nested sub-packages are not
    recursed into.

    Note:
        Importing each child is a deliberate side effect — it causes subclasses
        defined in those modules to register with the interpreter, enabling
        class-discovery mechanisms that rely on `__subclasses__()`.

    Args:
        package: Package to iterate. Must have a `__path__` attribute
            (i.e., must be a package, not a plain module).

    Yields:
        `(module, is_package)` pairs where `module` is the imported child and
        `is_package` is `True` when the child is itself a sub-package.
    """
    for _finder, name, is_package in pkgutil_iter_modules(
        package.__path__, prefix=package.__name__ + "."
    ):
        mod = import_module(name)
        yield mod, is_package
