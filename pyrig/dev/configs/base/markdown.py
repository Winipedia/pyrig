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
    ...     def get_content_str(cls) -> str:
    ...         return "# My Project\n\nDescription here."
"""

from pyrig.dev.configs.base.text import TextConfigFile


class MarkdownConfigFile(TextConfigFile):
    """Base class for Markdown (.md) files.

    Extends TextConfigFile with "md" extension. Inherits content-based validation.

    Subclasses must implement:
        - `get_parent_path`: Directory containing the .md file
        - `get_content_str`: Required Markdown content

    See Also:
        pyrig.dev.configs.base.text.TextConfigFile: Parent class
        pyrig.dev.configs.base.badges_md.BadgesMarkdownConfigFile: For badge files
    """

    @classmethod
    def get_file_extension(cls) -> str:
        """Return "md"."""
        return "md"
