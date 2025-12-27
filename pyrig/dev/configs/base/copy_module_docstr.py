"""Module docstring copying configuration management.

Provides CopyModuleOnlyDocstringConfigFile for copying only module docstrings,
allowing custom implementation.

Example:
    >>> from types import ModuleType
    >>> from pyrig.dev.configs.base.copy_module_docstr import (
    ...     CopyModuleOnlyDocstringConfigFile
    ... )
    >>> import pyrig.src.utils
    >>>
    >>> class UtilsDocstringCopy(CopyModuleOnlyDocstringConfigFile):
    ...     @classmethod
    ...     def get_src_module(cls) -> ModuleType:
    ...         return pyrig.src.utils
    >>>
    >>> UtilsDocstringCopy()  # Creates file with only docstring
"""

from pyrig.dev.configs.base.copy_module import CopyModuleConfigFile


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
    def get_content_str(cls) -> str:
        """Extract only the docstring from source module.

        Returns:
            Module docstring wrapped in triple quotes with newline.
        """
        content = super().get_content_str()
        parts = content.split('"""', 2)
        return '"""' + parts[1] + '"""\n'

    @classmethod
    def is_correct(cls) -> bool:
        """Check if file starts with triple quotes (has docstring).

        Returns:
            True if empty, exact match, or starts with triple quotes.
        """
        docstring = cls.get_file_content().strip()
        # is correct if file has """ or ''' in the first 5 characters
        first_5_chars = docstring[:5]
        triple_quotes_in_first_5_chars = any(
            quote in first_5_chars for quote in ('"""', "'''")
        )
        return super().is_correct() or triple_quotes_in_first_5_chars
