"""Module docstring copying configuration management.

Provides CopyModuleOnlyDocstringConfigFile for copying only module docstrings,
allowing custom implementation.

Example:
    >>> from types import ModuleType
    >>> from pyrig.dev.configs.base.copy_module_docstr import (
    ...     CopyModuleOnlyDocstringConfigFile
    ... )
    >>> import pyrig.src.string
    >>>
    >>> class StringDocstringCopy(CopyModuleOnlyDocstringConfigFile):
    ...     @classmethod
    ...     def get_src_module(cls) -> ModuleType:
    ...         return pyrig.src.string
    >>>
    >>> StringDocstringCopy()  # Creates file with only docstring
"""

from pyrig.dev.configs.base.copy_module import CopyModuleConfigFile
from pyrig.src.string import starts_with_docstring


class CopyModuleOnlyDocstringConfigFile(CopyModuleConfigFile):
    """Base class for copying only module docstrings.

    Extracts and copies only the module docstring, allowing custom implementation.
    Validates file starts with triple quotes.

    Subclasses must implement:
        - `get_src_module`: Return the source module to copy docstring from

    See Also:
        pyrig.dev.configs.base.copy_module.CopyModuleConfigFile: Parent class
        pyrig.dev.configs.base.init.InitConfigFile: For __init__.py docstrings
    """

    @classmethod
    def get_lines(cls) -> list[str]:
        """Extract only the docstring from source module.

        Returns:
            Module docstring wrapped in triple quotes with newline.
        """
        docstring = cls.get_src_module().__doc__
        if docstring is None:
            msg = f"Source module {cls.get_src_module()} has no docstring"
            raise ValueError(msg)
        return [*f'"""{docstring}"""'.splitlines(), ""]

    @classmethod
    def is_correct(cls) -> bool:
        """Check if file content is valid.

        Validates that the file either passes parent class validation (empty or
        exact match) or starts with a docstring (triple quotes).

        Returns:
            True if parent validation passes or content starts with triple quotes.
        """
        docstring = cls.get_file_content().strip()
        return super().is_correct() or starts_with_docstring(docstring)
