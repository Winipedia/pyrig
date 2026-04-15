"""Module loading, creation, and import path resolution utilities.

Provides utilities for importing modules with fallback strategies, creating new
module files, reading module source code, constructing and resolving fully qualified
import paths for objects, and executing functions within modules. Used throughout
pyrig for dynamic module loading when standard import mechanisms may not suffice.
"""

import importlib.util
import logging
import sys
from collections.abc import Callable, Generator, Iterable
from importlib import import_module
from pathlib import Path
from types import ModuleType
from typing import Any

from pyrig.core.introspection.paths import module_file_path
from pyrig.core.strings import read_text_utf8

logger = logging.getLogger(__name__)


def leaf_module_name(module: ModuleType) -> str:
    """Get the leaf name of a module (the last part of its dotted name).

    Args:
        module: Module to get the leaf name from.

    Returns:
        The leaf name of the module.
    """
    return module.__name__.split(".")[-1]


def callable_obj_import_path(obj: Callable[..., Any]) -> str:
    """Get the fully qualified import path for a callable object.

    Args:
        obj: Callable object (function, method, class, etc.) to get the import path for.

    Returns:
        The fully qualified import path for the object
        (e.g., "package.module.ClassName.method").
    """
    return f"{obj.__module__}.{obj.__qualname__}"  # ty:ignore[unresolved-attribute]


def module_content(module: ModuleType) -> str:
    """Read the source code of a module as a string.

    Args:
        module: Module to read. Must have a ``__file__`` attribute pointing
            to a readable ``.py`` file.

    Returns:
        Complete source code of the module as a UTF-8 encoded string.

    Raises:
        ValueError: If the module has no ``__file__`` attribute.
        FileNotFoundError: If the source file does not exist.
    """
    path = module_file_path(module)
    return read_text_utf8(path)


def import_module_with_file_fallback(path: Path, name: str) -> ModuleType:
    """Import a module, trying standard import first then direct file import.

    First attempts to import the module using Python's standard import mechanism
    (via ``importlib.import_module``). If that fails, falls back to importing
    directly from the file path using ``importlib.util``. This fallback is useful
    for modules that aren't on ``sys.path`` or haven't been installed.

    Args:
        path: Path to the module file (absolute or relative).
        name: The name to use for the imported module.

    Returns:
        The imported module.

    Raises:
        FileNotFoundError: If the file does not exist and standard import fails.
        ImportError: If the module spec cannot be created.
    """
    module = import_module_with_default(name)
    if isinstance(module, ModuleType):
        return module
    return import_module_from_file(path, name=name)


def import_module_from_file(path: Path, name: str) -> ModuleType:
    """Import a module directly from a ``.py`` file using ``importlib.util``.

    Registers the module in ``sys.modules`` with a name derived from its path
    (relative to the current working directory). If a ``FileNotFoundError``
    occurs during module execution, the module is removed from ``sys.modules``
    before re-raising the exception to avoid leaving invalid module entries.

    Args:
        path: Path to the ``.py`` file (will be resolved to absolute path).
        name: The name to use for the imported module.

    Returns:
        The imported and executed module.

    Raises:
        ImportError: If the module spec or loader cannot be created.
        FileNotFoundError: If the file does not exist or cannot be read.
    """
    path = path.resolve()
    spec = importlib.util.spec_from_file_location(name, location=path)
    if spec is None:
        msg = f"Could not create spec for {path}"
        raise ImportError(msg)
    module = importlib.util.module_from_spec(spec)
    if spec.loader is None:
        msg = f"Could not create loader for {path}"
        raise ImportError(msg)
    spec.loader.exec_module(module)
    sys.modules[name] = module
    return module


def import_module_with_default(
    module_name: str, default: Any = None
) -> ModuleType | Any:
    """Import a module by name, returning a default value if import fails.

    Logs a debug message when falling back to the default. Only catches
    ``ImportError``; other exceptions are not handled.

    Args:
        module_name: Dotted module name (e.g., ``"package.subpackage.module"``).
        default: Value to return if the module cannot be imported.

    Returns:
        The imported module, or ``default`` if ``ImportError`` is raised.
    """
    try:
        return import_module(module_name)
    except ImportError:
        logger.debug(
            "Could not import module %s, returning default value %s",
            module_name,
            default,
        )
        return default


def module_name_replacing_start_module(
    module: ModuleType, new_start_module_name: str
) -> str:
    """Replace the root package name in a module's fully qualified name.

    Useful for mapping modules between parallel package hierarchies (e.g.,
    mapping source modules to their test module equivalents).

    Args:
        module: Module whose name to transform.
        new_start_module_name: New root package name to substitute.

    Returns:
        The module name with the root package replaced.

    Example:
        >>> # If module.__name__ is "pyrig.src.modules.module"
        >>> module_name_replacing_start_module(module, "tests")
        'tests.src.modules.module'
    """
    module_current_start = module.__name__.split(".")[0]
    return module.__name__.replace(module_current_start, new_start_module_name, 1)


def module_has_docstring(module: ModuleType) -> bool:
    """Check if a module has a docstring.

    Args:
        module: Module to check.

    Returns:
        True if module has a docstring, False otherwise.
    """
    return module.__doc__ is not None


def import_modules(module_names: Iterable[str]) -> Generator[ModuleType, None, None]:
    """Import multiple modules by name.

    Args:
        module_names: List of dotted module names to import.

    Returns:
        Generator of imported module objects corresponding to the input names.
    """
    return (import_module(name) for name in module_names)


def reimport_module(module: ModuleType) -> ModuleType:
    """Re-import a module by name, bypassing the import cache.

    This function removes the specified module from ``sys.modules`` and then
    imports it again using the file fallback method. This is useful for refreshing
    a module's content after it has been modified on disk, ensuring that the latest
    version is loaded.

    Args:
        module: Module to reimport
    """
    module_path = module_file_path(module)
    # Remove from cache
    sys.modules.pop(module.__name__)
    return import_module_with_file_fallback(module_path, name=module.__name__)
