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
        module: Module to read. Must have a ``__file__`` attribute pointing
            to a readable ``.py`` file.

    Returns:
        Complete source code of the module as a UTF-8 encoded string.

    Raises:
        ValueError: If the module has no ``__file__`` attribute.
        FileNotFoundError: If the source file does not exist.
    """
    path = ModulePath.module_type_to_file_path(module)
    return path.read_text(encoding="utf-8")


def create_module(path: Path) -> ModuleType:
    """Create a new module file at the given path, or import if it already exists.

    Creates parent directories as Python packages (with ``__init__.py`` files)
    if they don't exist. If the target file doesn't exist, writes a new file
    with default module content (a minimal docstring).

    Args:
        path: Path to the ``.py`` file to create or import.

    Returns:
        The newly created or existing imported module.

    Raises:
        ValueError: If path is an empty Path (current working directory).
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
    """Import a module, trying standard import first then direct file import.

    First attempts to import the module using Python's standard import mechanism
    (via ``importlib.import_module``). If that fails, falls back to importing
    directly from the file path using ``importlib.util``. This fallback is useful
    for modules that aren't on ``sys.path`` or haven't been installed.

    Args:
        path: Path to the module file (absolute or relative).

    Returns:
        The imported module.

    Raises:
        FileNotFoundError: If the file does not exist and standard import fails.
        ValueError: If the module spec cannot be created.
    """
    module_name = ModulePath.absolute_path_to_module_name(path)
    module = import_module_with_default(module_name)
    if isinstance(module, ModuleType):
        return module
    return import_module_from_file(path)


def import_module_with_file_fallback_with_default(
    path: Path, default: Any = None
) -> ModuleType | Any:
    """Import a module from a path, returning a default value on failure.

    Wraps ``import_module_with_file_fallback`` with error handling. Returns the
    default value only when a ``FileNotFoundError`` occurs (other exceptions
    are not caught).

    Args:
        path: Path to the module file.
        default: Value to return if the file is not found.

    Returns:
        The imported module, or ``default`` if the file does not exist.
    """
    try:
        return import_module_with_file_fallback(path)
    except FileNotFoundError:
        return default


def import_module_from_file(path: Path) -> ModuleType:
    """Import a module directly from a ``.py`` file using ``importlib.util``.

    Registers the module in ``sys.modules`` with a name derived from its path
    (relative to the current working directory). If a ``FileNotFoundError``
    occurs during module execution, the module is removed from ``sys.modules``
    before re-raising the exception to avoid leaving invalid module entries.

    Args:
        path: Path to the ``.py`` file (will be resolved to absolute path).

    Returns:
        The imported and executed module.

    Raises:
        ValueError: If the module spec or loader cannot be created.
        FileNotFoundError: If the file does not exist or cannot be read.
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
    """Create a fully qualified import path string for an object.

    Constructs a dotted path that can be used with ``import_obj_from_importpath``
    to re-import the object. For modules, returns the module name directly.
    For classes and functions, combines the module name with the qualified name.

    Args:
        obj: Module, class, or function to create an import path for.

    Returns:
        Fully qualified import path (e.g., ``"package.module.ClassName"`` or
        ``"package.module.func_name"``).

    Example:
        >>> make_obj_importpath(Path)
        'pathlib.Path'
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

    Inverse of ``make_obj_importpath``. First attempts to import the path as a
    module. If that fails with ``ImportError`` and the path contains dots, splits
    off the last component and imports it as an attribute of the parent module.

    Args:
        importpath: Fully qualified import path (e.g., ``"package.module.MyClass"``).

    Returns:
        The imported module, class, or function.

    Raises:
        ImportError: If the module portion cannot be imported.
        AttributeError: If the object is not found in the module.

    Example:
        >>> cls = import_obj_from_importpath("pathlib.Path")
        >>> cls is Path
        True
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
    """Extract the bare name of an object without its module or class prefix.

    For modules, returns the last component of the dotted name. For classes,
    returns ``__name__``. For functions (including nested or methods), returns
    the last component of ``__qualname__``.

    Args:
        obj: Module, class, or function (may be wrapped by decorators).

    Returns:
        The bare object name (e.g., ``"MyClass"`` not ``"package.module.MyClass"``).

    Example:
        >>> get_isolated_obj_name(Path)
        'Path'
    """
    obj = get_unwrapped_obj(obj)
    if isinstance(obj, ModuleType):
        return obj.__name__.split(".")[-1]
    if isinstance(obj, type):
        return obj.__name__
    return get_qualname_of_obj(obj).split(".")[-1]


def execute_all_functions_from_module(module: ModuleType) -> list[Any]:
    """Execute all functions defined in a module and collect their return values.

    Useful for running setup/initialization functions or test fixtures defined
    in a module. Functions are executed in definition order.

    Args:
        module: Module containing zero-argument functions to execute.

    Returns:
        List of return values from all executed functions, in definition order.

    Note:
        Only executes functions defined directly in the module (not imported).
        All functions must accept zero arguments or have default values for all
        parameters. Raises ``TypeError`` if a function requires arguments.
    """
    return [f() for f in get_all_functions_from_module(module)]


def get_default_module_content() -> str:
    """Generate default content for a new Python module file.

    Used by ``create_module`` when creating new module files. The content is a
    minimal valid Python module containing only a placeholder docstring with
    the text "module.".

    Returns:
        A string containing a single-line docstring and a trailing newline.
    """
    return '''"""module."""
'''


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


def get_module_name_replacing_start_module(
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
        >>> get_module_name_replacing_start_module(module, "tests")
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
