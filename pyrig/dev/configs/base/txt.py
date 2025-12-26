r"""Configuration management for .txt files.

This module provides the TxtConfigFile class for managing .txt text files.
This is a convenience subclass of TextConfigFile that sets the extension to "txt".

Example:
    >>> from pathlib import Path
    >>> from pyrig.dev.configs.base.txt import TxtConfigFile
    >>>
    >>> class NotesFile(TxtConfigFile):
    ...     @classmethod
    ...     def get_parent_path(cls) -> Path:
    ...         return Path("docs")
    ...
    ...     @classmethod
    ...     def get_content_str(cls) -> str:
    ...         return "# Project Notes\n\n"
"""

from pyrig.dev.configs.base.text import TextConfigFile


class TxtConfigFile(TextConfigFile):
    r"""Abstract base class for .txt text files.

    Extends TextConfigFile to use the "txt" file extension. All functionality
    is inherited from TextConfigFile - only the extension differs.

    Subclasses must implement:
        - `get_parent_path`: Directory containing the .txt file
        - `get_content_str`: Required content that must be present

    Example:
        >>> from pathlib import Path
        >>> from pyrig.dev.configs.base.txt import TxtConfigFile
        >>>
        >>> class MyTextFile(TxtConfigFile):
        ...     @classmethod
        ...     def get_parent_path(cls) -> Path:
        ...         return Path()
        ...
        ...     @classmethod
        ...     def get_content_str(cls) -> str:
        ...         return "Required content\n"

    See Also:
        pyrig.dev.configs.base.text.TextConfigFile: Parent class with full docs
    """

    @classmethod
    def get_file_extension(cls) -> str:
        """Get the .txt file extension.

        Returns:
            The string "txt" (without the leading dot).

        Example:
            For a class named NotesConfigFile::

                get_filename() -> "notes"
                get_file_extension() -> "txt"
                get_path() -> Path("notes.txt")
        """
        return "txt"
