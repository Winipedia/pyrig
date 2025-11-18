"""Module utilities for introspection and manipulation.

This module provides comprehensive utility functions for working with Python modules,
including path conversions, module creation, object importing, and content extraction.
It handles the complexities of Python's module system by providing a consistent API
for module operations across different contexts (packages vs. standalone modules).

The utilities support both runtime module manipulation and static analysis,
making them suitable for code generation, testing frameworks, and dynamic imports.
"""

import importlib.util
import inspect
import logging
import os
import sys
from collections.abc import Callable, Sequence
from importlib import import_module
from pathlib import Path
from types import ModuleType
from typing import Any

from pyrig.src.modules.class_ import (
    get_all_cls_from_module,
    get_all_methods_from_cls,
)
from pyrig.src.modules.function import get_all_functions_from_module
from pyrig.src.modules.inspection import (
    get_qualname_of_obj,
    get_unwrapped_obj,
)
from pyrig.src.modules.package import (
    get_modules_and_packages_from_package,
    import_pkg_from_path,
    module_is_package,
)

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
    path = to_path(module, is_package=False)
    return path.read_text(encoding="utf-8")


def to_module_name(path: str | Path | ModuleType) -> str:
    """Convert a filesystem path to a Python module import name.

    Transforms a file or directory path into the corresponding Python module name
    by making it relative to the current directory, removing the file extension,
    and replacing directory separators with dots.

    Args:
        path: a str that represents a path or a Path object or a ModuleType object
                or a str that represents a module name

    Returns:
        The Python module name corresponding to the path

    Example:
        path_to_module_name("src/package/module.py") -> "src.package.module"

    """
    if isinstance(path, ModuleType):
        return path.__name__
    if isinstance(path, Path):
        cwd = (
            Path.cwd()
            if not getattr(sys, "frozen", False)
            else Path(getattr(sys, "_MEIPASS", ""))
        )
        if path.is_absolute():
            path = path.relative_to(cwd)
        if path.suffix:
            path = path.with_suffix("")
        # return joined on . parts
        return ".".join(path.parts)
    if path in (".", "./", ""):
        return ""
    # we get a str that can either be a dotted module name or a path
    # e.g. package/module.py or package/module or
    # package.module or just package/package2
    # or just package with nothing
    path = path.removesuffix(".py")
    if "." in path:
        # already a module name
        return path
    return to_module_name(Path(path))


def to_path(module_name: str | ModuleType | Path, *, is_package: bool) -> Path:
    """Convert a Python module import name to its filesystem path.

    Transforms a Python module name into the corresponding file path by replacing
    dots with directory separators and adding the .py extension. Uses the
    package_name_to_path function for the directory structure.

    Args:
        module_name: A Python module name to convert or Path or ModuleType
        is_package: Whether to return the path to the package directory
            without the .py extension

    Returns:
        A Path object representing the filesystem path to the module
        if is_package is True, returns the path to the package directory
        without the .py extension

    Example:
        module_name_to_path("src.package.module") -> Path("src/package/module.py")

    """
    if isinstance(module_name, ModuleType) and hasattr(module_name, "__file__"):
        file_str = module_name.__file__
        if file_str is not None:
            file_path = Path(file_str)
            if is_package:
                # this way if you want __init__ in the path then package=False
                file_path = file_path.parent
            return file_path
    module_name = to_module_name(module_name)
    path = Path(module_name.replace(".", os.sep))
    # for smth like pyinstaller we support frozen path
    if getattr(sys, "frozen", False):
        path = Path(getattr(sys, "_MEIPASS", "")) / path
    # if path is cwd or "."
    if path in (Path.cwd(), Path()):
        return Path()
    # if path without with.py exists
    with_py = path.with_suffix(".py")
    if with_py.exists():
        return with_py
    not_with_py = path.with_suffix("")
    if not_with_py.exists():
        return not_with_py
    if is_package:
        return path
    return path.with_suffix(".py")


def make_dir_with_init_file(path: Path) -> None:
    """Create a directory and add __init__.py files to make it a package.

    Args:
        path: The directory path to create and initialize as a package

    """
    path.mkdir(parents=True, exist_ok=True)
    make_init_modules_for_package(path)


def create_module(
    module_name: str | Path | ModuleType, *, is_package: bool
) -> ModuleType:
    """Create a new Python module file and import it.

    Creates a new module file at the location specified by the module name,
    ensuring all necessary parent directories and __init__.py files exist.
    Optionally writes content to the module file and parent __init__.py files.
    Finally imports and returns the newly created module.

    Args:
        module_name: The fully qualified name of the module to create
        is_package: Whether to create a package instead of a module

    Returns:
        The imported module object representing the newly created module

    Note:
        Includes a small delay (0.1s) before importing to ensure filesystem operations
        are complete, preventing race conditions.

    """
    path = to_path(module_name, is_package=is_package)
    if path == Path():
        msg = f"Cannot create module {module_name=} because it is the CWD"
        logger.error(msg)
        raise ValueError(msg)

    make_dir_with_init_file(path if is_package else path.parent)

    # use spec and importlib to import the module
    if is_package:
        return import_pkg_from_path(path)

    if not path.exists():
        path.write_text(get_default_module_content())
    return import_module_from_file(path)


def import_module_from_path(path: Path | str) -> ModuleType:
    """Import a module from a path."""
    module_name = to_module_name(path)
    path = to_path(module_name, is_package=False)
    module = import_module_with_default(module_name)
    if module is not None:
        return module
    if path.is_dir():
        return import_pkg_from_path(path)
    return import_module_from_file(path)


def import_module_from_path_with_default(
    path: Path, default: Any = None
) -> ModuleType | Any:
    """Import a module from a path."""
    try:
        return import_module_from_path(path)
    except FileNotFoundError:
        return default


def import_module_from_file(path: Path) -> ModuleType:
    """Import a module from a path."""
    # name is dotted path relative to cwd
    name = to_module_name(path.resolve().relative_to(Path.cwd()))
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None:
        msg = f"Could not create spec for {path}"
        raise ValueError(msg)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    if spec.loader is None:
        msg = f"Could not create loader for {path}"
        raise ValueError(msg)
    spec.loader.exec_module(module)
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
        obj: Callable[..., Any] | type | ModuleType = getattr(module, obj_name)
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


def get_objs_from_obj(
    obj: Callable[..., Any] | type | ModuleType,
) -> Sequence[Callable[..., Any] | type | ModuleType]:
    """Extract all contained objects from a container object.

    Retrieves all relevant objects contained within the given object, with behavior
    depending on the type of the container:
    - For modules: returns all functions and classes defined in the module
    - For packages: returns all submodules in the package
    - For classes: returns all methods defined directly in the class
    - For other objects: returns an empty list

    Args:
        obj: The container object to extract contained objects from

    Returns:
        A sequence of objects contained within the given container object

    """
    if isinstance(obj, ModuleType):
        if module_is_package(obj):
            return get_modules_and_packages_from_package(obj)[1]
        objs: list[Callable[..., Any] | type] = []
        objs.extend(get_all_functions_from_module(obj))
        objs.extend(get_all_cls_from_module(obj))
        return objs
    if isinstance(obj, type):
        return get_all_methods_from_cls(obj, exclude_parent_methods=True)
    return []


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


def get_executing_module() -> ModuleType:
    """Get the module where execution has started.

    The executing module is the module that contains the __main__ attribute as __name__
    E.g. if you run `python -m pyrig.setup` from the command line,
    then the executing module is pyrigmodules.setup

    Returns:
        The module where execution has started

    Raises:
        ValueError: If no __main__ module is found or if the executing module
                    cannot be determined

    """
    main = sys.modules.get("__main__")
    if main is None:
        msg = "No __main__ module found"
        raise ValueError(msg)
    return main


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
        return default


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
