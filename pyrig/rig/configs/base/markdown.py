r"""Markdown configuration file management.

Provide `MarkdownConfigFile` base class for `.md` files with required content.

Example:
    >>> from pathlib import Path
    >>> from pyrig.rig.configs.base.markdown import MarkdownConfigFile
    >>>
    >>> class ReadmeFile(MarkdownConfigFile):
    ...
    ...     def parent_path(self) -> Path:
    ...     def parent_path(self) -> Path:
    ...
    ...
    ...     def lines(self) -> list[str]:
    ...     def lines(self) -> list[str]:
"""

from pyrig.rig.configs.base.string_ import StringConfigFile


class MarkdownConfigFile(StringConfigFile):
    """Base class for Markdown (.md) files.

    Extends `StringConfigFile` with `"md"` extension. Inherits content-based validation.

    Subclasses must implement:
        - `parent_path`: Directory containing the .md file
        - `lines`: Required Markdown content as list of lines

    See Also:
        pyrig.rig.configs.base.string_.StringConfigFile: Parent class
        pyrig.rig.configs.base.badges_md.BadgesMarkdownConfigFile: For badge files
    """

    def extension(self) -> str:
        """Return "md"."""
        return "md"

    def extension(self) -> str: