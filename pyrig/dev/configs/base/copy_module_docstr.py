"""Module docstring copying configuration management.

Provides CopyModuleOnlyDocstringConfigFile for copying only module docstrings,
allowing custom implementation.

Example:
    >>> from types import ModuleType
    >>> from pyrig.dev.configs.base.copy_module_docstr import (
    ...     CopyModuleOnlyDocstringConfigFile
    ... )
    >>> import pyrig.src.string_
    >>>
    >>> class StringDocstringCopy(CopyModuleOnlyDocstringConfigFile):
    ...     @classmethod
    ...     def get_src_module(cls) -> ModuleType:
    ...         return pyrig.src.string_
    >>>
    >>> StringDocstringCopy()  # Creates file with only docstring
"""

from pyrig.dev.configs.base.copy_module import CopyModuleConfigFile
from pyrig.src.modules.module import module_has_docstring


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

        Validates that the file passes parent class validation (empty or expected
        content present) or that the source module has a docstring (allowing custom
        implementation in the target file).

        Returns:
            True if parent validation passes or source module has a docstring.
        """
        return super().is_correct() or module_has_docstring(cls.get_src_module())
