r""".txt file configuration management.

Provides TxtConfigFile base class for .txt files with required content.

Example:
    >>> from pathlib import Path
    >>> from pyrig.rig.configs.base.txt import TxtConfigFile
    >>>
    >>> class NotesFile(TxtConfigFile):
    ...     @classmethod
    ...     def parent_path(cls) -> Path:
    ...         return Path("docs")
    ...
    ...     @classmethod
    ...     def lines(cls) -> list[str]:
    ...         return ["# Project Notes"]
"""

from pyrig.rig.configs.base.string_ import StringConfigFile


class TxtConfigFile(StringConfigFile):
    """Base class for .txt files.

    Extends StringConfigFile with "txt" extension. Inherits content-based validation.

    Subclasses must implement:
        - `parent_path`: Directory containing the .txt file
        - `lines`: Required content as list of lines

    See Also:
        pyrig.rig.configs.base.string_.StringConfigFile: Parent class
    """

    @classmethod
    def extension(cls) -> str:
        """Return "txt"."""
        return "txt"
