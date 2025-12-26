"""Configuration management for copying module docstrings.

This module provides the CopyModuleOnlyDocstringConfigFile class for creating
files that contain only the docstring from a source module, not the entire
module content.

CopyModuleOnlyDocstringConfigFile is useful for:
- Creating stub files with documentation but custom implementation
- Preserving API documentation while allowing user customization
- Providing templates with clear documentation
- Maintaining consistency in docstring format

The key difference from CopyModuleConfigFile:
- Only copies the module docstring (first triple-quoted string)
- Allows users to provide their own implementation
- Validation checks for docstring presence, not exact content match

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
    >>> UtilsDocstringCopy()
    # Creates myproject/src/utils.py with only the docstring from
    # pyrig/src/utils.py, allowing users to add their own implementation
"""

from pyrig.dev.configs.base.copy_module import CopyModuleConfigFile


class CopyModuleOnlyDocstringConfigFile(CopyModuleConfigFile):
    """Config file that copies only the docstring from a module.

    Extends CopyModuleConfigFile to extract and copy only the module docstring,
    not the entire module content. This creates stub files that preserve
    documentation but allow users to provide their own implementation.

    The docstring extraction:
        1. Gets the full module content via super().get_content_str()
        2. Splits on triple quotes to isolate the docstring
        3. Returns only the docstring wrapped in triple quotes

    Validation behavior:
        - Checks if the file starts with triple quotes
        - Allows users to add implementation after the docstring
        - More lenient than exact content matching

    Subclasses must implement:
        - `get_src_module`: Return the source module to copy docstring from

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

    See Also:
        pyrig.dev.configs.base.copy_module.CopyModuleConfigFile: Parent class
        pyrig.dev.configs.base.init.InitConfigFile: For __init__.py docstrings
    """

    @classmethod
    def get_content_str(cls) -> str:
        r'''Extract only the docstring from the source module.

        Parses the source module content to extract just the module docstring
        (the first triple-quoted string). This allows users to add their own
        implementation while preserving the documentation.

        The extraction process:
            1. Get the full module content via super().get_content_str()
            2. Split on triple quotes (""") to find the docstring
            3. Take the first quoted section (index 1 after split)
            4. Wrap it back in triple quotes and add a newline

        Returns:
            The module docstring wrapped in triple quotes, followed by a newline.
            Format: """docstring content"""\n

        Example:
            Extract docstring from a source module::

                # Source module contains:
                # """This is the module docstring."""
                # import sys
                # def foo(): pass

                content = cls.get_content_str()
                # Returns: """This is the module docstring."""\n

        Note:
            This assumes the source module has a docstring as the first
            element. If the module has no docstring, the behavior is undefined.
        '''
        content = super().get_content_str()
        parts = content.split('"""', 2)
        return '"""' + parts[1] + '"""\n'

    @classmethod
    def is_correct(cls) -> bool:
        '''Check if the file contains a docstring.

        Overrides the parent validation to check if the file starts with
        triple quotes ("""), indicating a docstring is present. This is more
        lenient than checking for exact content match.

        The validation accepts:
            - Empty file (user opted out)
            - File with exact docstring match (parent validation)
            - File starting with triple quotes (has a docstring)

        Returns:
            True if the file is empty, has exact match, or starts with triple
            quotes.

        Example:
            Valid files::

                ""  # Empty (opted out)
                """Exact docstring."""  # Exact match
                """Any docstring."""
                import sys  # Has docstring + code

            Invalid files::

                import sys  # No docstring
                # Comment  # No docstring

        Note:
            The validation checks if the content starts with triple quotes ("""),
            not if it matches the source docstring exactly. This allows users
            to modify the docstring.
        '''
        docstring = cls.get_content_str().strip()
        # is correct if file start with """
        return super().is_correct() or docstring.startswith('"""')
