"""Utilities for working with Python modules."""

from types import ModuleType

from pyrig.core.introspection.paths import module_file_path
from pyrig.core.strings import read_text_utf8


def leaf_module_name(module: ModuleType) -> str:
    """Return the final component of a module's dotted name."""
    return module.__name__.split(".")[-1]


def module_content(module: ModuleType) -> str:
    """Read UTF-8 text from the file recorded by a module.

    Args:
        module: Module whose file content to read.

    Returns:
        Complete contents of the module's file, decoded as UTF-8.
    """
    path = module_file_path(module)
    return read_text_utf8(path)
