"""Module loading, path conversion, and cross-package discovery utilities.

Provides utilities for loading modules from files, converting between module names and
file paths, reading module source code, and executing functions within modules. Used
throughout pyrig for dynamic module loading with fallback strategies.
"""

import importlib.util
import logging
import sys
from collections.abc import Callable
from importlib import import_module
from pathlib import Path
from types import ModuleType
from typing import Any

from pyrig.src.modules.function import get_all_functions_from_module
from pyrig.src.modules.inspection import (
    get_module_of_obj,
    get_qualname_of_obj,
    get_unwrapped_obj,
)
from pyrig.src.modules.path import ModulePath, make_dir_with_init_file

logger = logging.getLogger(__name__)


def get_module_content_as_str(module: ModuleType) -> str:
    """Read the source code of a module as a string.

    Args:
        module: Module to read.

    Returns:
        Complete source code.
    """
    path = ModulePath.module_type_to_file_path(module)
    return path.read_text(encoding="utf-8")


def create_module(path: Path) -> ModuleType:
    """Create a module at the given path, or import if it exists.

    Args:
        path: Path to create module at.

    Returns:
        Created or imported module.

    Raises:
        ValueError: If path is the CWD.
    """
    if path == Path():
        msg = f"Cannot create module {path=} because it is the CWD"
        raise ValueError(msg)

    make_dir_with_init_file(path.parent)

    if not path.exists():
        logger.info("Creating module at: %s", path)
        path.write_text(get_default_module_content())
    return import_module_with_file_fallback(path)


def import_module_with_file_fallback(path: Path) -> ModuleType:
    """Import a module by name, falling back to direct file import.

    Args:
        path: Path to the module.

    Returns:
        Imported module.
    """
    module_name = ModulePath.absolute_path_to_module_name(path)
    module = import_module_with_default(module_name)
    if isinstance(module, ModuleType):
        return module
    return import_module_from_file(path)


def import_module_with_file_fallback_with_default(
    path: Path, default: Any = None
) -> ModuleType | Any:
    """Import a module from a path, returning default on failure.

    Args:
        path: Path to the module.
        default: Value to return if import fails.

    Returns:
        Imported module or default.
    """
    try:
        return import_module_with_file_fallback(path)
    except FileNotFoundError:
        return default


def import_module_from_file(path: Path) -> ModuleType:
    """Import a module directly from a .py file.

    Registers the module in `sys.modules` with a name derived from its path.

    Args:
        path: Path to the .py file.

    Returns:
        Imported module.

    Raises:
        ValueError: If module spec or loader cannot be created.
    """
    path = path.resolve()
    name = ModulePath.absolute_path_to_module_name(path)
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None:
        msg = f"Could not create spec for {path}"
        raise ValueError(msg)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    if spec.loader is None:
        msg = f"Could not create loader for {path}"
        raise ValueError(msg)
    try:
        spec.loader.exec_module(module)
    except FileNotFoundError:
        del sys.modules[name]
        raise
    return module


def make_obj_importpath(obj: Callable[..., Any] | type | ModuleType) -> str:
    """Create a fully qualified import path for an object.

    Args:
        obj: Module, class, or function.

    Returns:
        Fully qualified import path (e.g., "package.module.ClassName").
    """
    if isinstance(obj, ModuleType):
        return obj.__name__
    module: str | None = get_module_of_obj(obj).__name__
    obj_name = get_qualname_of_obj(obj)
    if not module:
        return obj_name
    return module + "." + obj_name


def import_obj_from_importpath(
    importpath: str,
) -> Callable[..., Any] | type | ModuleType:
    """Import an object from its fully qualified import path.

    Tries importing as a module first, then as a class/function attribute.

    Args:
        importpath: Fully qualified import path.

    Returns:
        Imported object.

    Raises:
        ImportError: If module cannot be imported.
        AttributeError: If object not found in module.
    """
    try:
        return import_module(importpath)
    except ImportError:
        # might be a class or function
        if "." not in importpath:
            raise
        module_name, obj_name = importpath.rsplit(".", 1)
        module = import_module(module_name)
        obj: Callable[..., Any] | type = getattr(module, obj_name)
        return obj


def get_isolated_obj_name(obj: Callable[..., Any] | type | ModuleType) -> str:
    """Extract the bare name of an object without module prefix.

    Args:
        obj: Module, class, or function.

    Returns:
        Object name without module path.
    """
    obj = get_unwrapped_obj(obj)
    if isinstance(obj, ModuleType):
        return obj.__name__.split(".")[-1]
    if isinstance(obj, type):
        return obj.__name__
    return get_qualname_of_obj(obj).split(".")[-1]


def execute_all_functions_from_module(module: ModuleType) -> list[Any]:
    """Execute all functions defined in a module with no arguments.

    Args:
        module: Module containing functions to execute.

    Returns:
        List of return values from all executed functions.

    Note:
        Only executes functions defined directly in the module.
        All functions must accept zero arguments.
    """
    return [f() for f in get_all_functions_from_module(module)]


def get_default_module_content() -> str:
    """Generate default content for a new Python module file.

    Returns:
        Module content with placeholder docstring.
    """
    return '''"""module."""
'''


def import_module_with_default(
    module_name: str, default: Any = None
) -> ModuleType | Any:
    """Import a module, returning default on failure.

    Args:
        module_name: Name of module to import.
        default: Value to return if import fails.

    Returns:
        Imported module or default.
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


def get_module_name_replacing_start_module(
    module: ModuleType, new_start_module_name: str
) -> str:
    """Replace the root module name in a module's qualified name.

    Args:
        module: Module whose name to transform.
        new_start_module_name: New root module name.

    Returns:
        Transformed module name.
    """
    module_current_start = module.__name__.split(".")[0]
    return module.__name__.replace(module_current_start, new_start_module_name, 1)
