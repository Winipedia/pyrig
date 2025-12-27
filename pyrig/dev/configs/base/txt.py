r""".txt file configuration management.

Provides TxtConfigFile base class for .txt files with required content.

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
    ...         return "# Project Notes\n"
"""

from pyrig.dev.configs.base.text import TextConfigFile


class TxtConfigFile(TextConfigFile):
    """Base class for .txt files.

    Extends TextConfigFile with "txt" extension. Inherits content-based validation.

    Subclasses must implement:
        - `get_parent_path`: Directory containing the .txt file
        - `get_content_str`: Required content

    See Also:
        pyrig.dev.configs.base.text.TextConfigFile: Parent class
    """

    @classmethod
    def get_file_extension(cls) -> str:
        """Return "txt"."""
        return "txt"
