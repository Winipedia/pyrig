r"""Markdown configuration file management.

Provides a base class for creating and managing Markdown (``.md``) configuration
files with validated content.
"""

from pyrig.rig.configs.base.string_ import StringConfigFile


class MarkdownConfigFile(StringConfigFile):
    """Base class for Markdown (``.md``) configuration files.

    Extends ``StringConfigFile`` with the ``"md"`` file extension. Subclasses define
    their directory path and required content; the parent class handles reading,
    writing, and content-based validation.

    Subclasses must implement:
        - ``parent_path``: Directory containing the ``.md`` file.
        - ``stem``: Filename without its extension.
        - ``lines``: Required Markdown content as a list of lines.

    Example:
        >>> from pathlib import Path
        >>> from pyrig.rig.configs.base.markdown import MarkdownConfigFile
        >>>
        >>> class ReadmeFile(MarkdownConfigFile):
        ...
        ...     def parent_path(self) -> Path:
        ...         return Path()
        ...
        ...
        ...     def stem(self) -> str:
        ...         return "README"
        ...
        ...
        ...     def lines(self) -> list[str]:
        ...         return ["# My Project", "", "Description here."]
    """

    def extension(self) -> str:
        """Return the file extension ``"md"``."""
        return "md"
