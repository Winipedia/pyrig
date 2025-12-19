"""Module loading, path conversion, and cross-package discovery utilities.

This module provides comprehensive utilities for working with Python modules,
including bidirectional path/module name conversion, dynamic module creation,
object importing, and cross-package module discovery.
"""

import importlib.util
import inspect
import logging
import sys
from collections.abc import Callable
from importlib import import_module
from pathlib import Path
from types import ModuleType
from typing import Any

from pyrig.src.modules.function import get_all_functions_from_module
from pyrig.src.modules.inspection import (
    get_qualname_of_obj,
    get_unwrapped_obj,
)
from pyrig.src.modules.path import ModulePath, make_dir_with_init_file

logger = logging.getLogger(__name__)


def get_module_content_as_str(module: ModuleType) -> str:
    """Retrieve the complete source code of a module as a string.

    This function locates the physical file associated with the given module object
    and reads its entire content. It works for both regular modules and packages
    by determining the correct path using module_to_path.

    Args:
        module: The module object whose source code should be retrieved


    Returns:
        The complete source code of the module as a string

    """
    path = ModulePath.module_type_to_file_path(module)
    return path.read_text(encoding="utf-8")


def create_module(path: Path) -> ModuleType:
    """Create and return a module at the given path if it does not exist.

    If the path already exists, it is just imported and returned.

    Args:
        path (Path): The path to create the module at

    Raises:
        ValueError: If the path is the CWD

    Returns:
        ModuleType: The created or imported module
    """
    if path == Path():
        msg = f"Cannot create module {path=} because it is the CWD"
        raise ValueError(msg)

    make_dir_with_init_file(path.parent)

    if not path.exists():
        path.write_text(get_default_module_content())
    return import_module_with_file_fallback(path)


def import_module_with_file_fallback(path: Path) -> ModuleType:
    """Import a module from a path.

    First try to import the module from the path. If that fails, try to import
    from the path.

    Args:
        path (Path): The path to the module

    Returns:
        ModuleType: The imported module
    """
    module_name = ModulePath.absolute_path_to_module_name(path)
    module = import_module_with_default(module_name)
    if isinstance(module, ModuleType):
        return module
    return import_module_from_file(path)


def import_module_with_file_fallback_with_default(
    path: Path, default: Any = None
) -> ModuleType | Any:
    """Import a module from a path, returning a default on failure.

    Args:
        path: Filesystem path to the module.
        default: Value to return if the module cannot be imported.

    Returns:
        The imported module, or `default` if import fails.
    """
    try:
        return import_module_with_file_fallback(path)
    except FileNotFoundError:
        return default


def import_module_from_file(path: Path) -> ModuleType:
    """Import a module directly from a .py file.

    Uses `importlib.util` to create a module spec and load the module
    from the specified file. The module is registered in `sys.modules`
    with a name derived from its path relative to the current directory.

    Args:
        path: Path to the .py file to import.

    Returns:
        The imported module object.

    Raises:
        ValueError: If a module spec or loader cannot be created for the path.
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
    """Create a fully qualified import path string for a Python object.

    Generates the import path that would be used to import the given object.
    Handles different types of objects (modules, classes, functions) appropriately.

    Args:
        obj: The object (module, class, or function) to create an import path for

    Returns:
        A string representing the fully qualified import path for the object

    Examples:
        For a module: "package.subpackage.module"
        For a class: "package.module.ClassName"
        For a function: "package.module.function_name"
        For a method: "package.module.ClassName.method_name"

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
    """Import a Python object (module, class, or function) from its import path.

    Attempts to import the object specified by the given import path. First tries
    to import it as a module, and if that fails, attempts to import it as a class
    or function by splitting the path and using getattr.

    Args:
        importpath: The fully qualified import path of the object

    Returns:
        The imported object (module, class, or function)

    Raises:
        ImportError: If the module part of the path cannot be imported
        AttributeError: If the object is not found in the module

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
    """Extract the bare name of an object without its module prefix.

    Retrieves just the name part of an object, without any module path information.
    For modules, returns the last component of the module path.

    Args:
        obj: The object (module, class, or function) to get the name for

    Returns:
        The isolated name of the object without any module path

    Examples:
        For a module "package.subpackage.module": returns "module"
        For a class: returns the class name
        For a function: returns the function name

    """
    obj = get_unwrapped_obj(obj)
    if isinstance(obj, ModuleType):
        return obj.__name__.split(".")[-1]
    if isinstance(obj, type):
        return obj.__name__
    return get_qualname_of_obj(obj).split(".")[-1]


def execute_all_functions_from_module(module: ModuleType) -> list[Any]:
    """Execute all functions defined in a module with no arguments.

    Retrieves all functions defined in the module and calls each one with no arguments.
    Collects and returns the results of all function calls.

    Args:
        module: The module containing functions to execute

    Returns:
        A list containing the return values from all executed functions

    Note:
        Only executes functions defined directly in the module, not imported functions.
        All functions must accept being called with no arguments.

    """
    return [f() for f in get_all_functions_from_module(module)]


def get_default_module_content() -> str:
    """Generate standardized content for a Python module file.

    Creates a simple docstring for a module file based on its name,
    following the project's documentation conventions.

    Returns:
        A string containing a properly formatted docstring for the module file

    """
    return '''"""module."""
'''


def get_module_of_obj(obj: Any, default: ModuleType | None = None) -> ModuleType:
    """Return the module name where a method-like object is defined.

    Args:
        obj: Method-like object (funcs, method, property, staticmethod, classmethod...)
        default: Default module to return if the module cannot be determined

    Returns:
        The module name as a string, or None if module cannot be determined.

    """
    unwrapped = get_unwrapped_obj(obj)
    module = inspect.getmodule(unwrapped)
    if not module:
        msg = f"Could not determine module of {obj}"
        if default:
            return default
        raise ValueError(msg)
    return module


def import_module_with_default(
    module_name: str, default: Any = None
) -> ModuleType | Any:
    """Import a module, returning a default if the module cannot be imported.

    Args:
        module_name: Name of the module to import
        default: Default module to return if the module cannot be imported

    Returns:
        The imported module, or the default module if the module cannot be imported

    Raises:
        ValueError: If the module cannot be imported

    """
    try:
        return import_module(module_name)
    except ImportError:
        logger.debug("Could not import module %s", module_name)
        return default


def get_module_name_replacing_start_module(
    module: ModuleType, new_start_module_name: str
) -> str:
    """Replace the root module name in a module's fully qualified name.

    Args:
        module: The module whose name to transform.
        new_start_module_name: The new root module name.

    Returns:
        The transformed module name.
    """
    module_current_start = module.__name__.split(".")[0]
    return module.__name__.replace(module_current_start, new_start_module_name, 1)
