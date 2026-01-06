r"""Markdown configuration file management.

Provides MarkdownConfigFile base class for .md files with required content.

Example:
    >>> from pathlib import Path
    >>> from pyrig.dev.configs.base.markdown import MarkdownConfigFile
    >>>
    >>> class ReadmeFile(MarkdownConfigFile):
    ...     @classmethod
    ...     def get_parent_path(cls) -> Path:
    ...         return Path()
    ...
    ...     @classmethod
    ...     def get_lines(cls) -> list[str]:
    ...         return ["# My Project", "", "Description here."]
"""

from pyrig.dev.configs.base.string_ import StringConfigFile


class MarkdownConfigFile(StringConfigFile):
    """Base class for Markdown (.md) files.

    Extends StringConfigFile with "md" extension. Inherits content-based validation.

    Subclasses must implement:
        - `get_parent_path`: Directory containing the .md file
        - `get_lines`: Required Markdown content as list of lines

    See Also:
        pyrig.dev.configs.base.string_.StringConfigFile: Parent class
        pyrig.dev.configs.base.badges_md.BadgesMarkdownConfigFile: For badge files
    """

    @classmethod
    def get_file_extension(cls) -> str:
        """Return "md"."""
        return "md"
