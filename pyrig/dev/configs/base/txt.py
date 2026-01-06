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
    ...     def get_lines(cls) -> list[str]:
    ...         return ["# Project Notes"]
"""

from pyrig.dev.configs.base.string_ import StringConfigFile


class TxtConfigFile(StringConfigFile):
    """Base class for .txt files.

    Extends StringConfigFile with "txt" extension. Inherits content-based validation.

    Subclasses must implement:
        - `get_parent_path`: Directory containing the .txt file
        - `get_lines`: Required content as list of lines

    See Also:
        pyrig.dev.configs.base.string_.StringConfigFile: Parent class
    """

    @classmethod
    def get_file_extension(cls) -> str:
        """Return "txt"."""
        return "txt"
