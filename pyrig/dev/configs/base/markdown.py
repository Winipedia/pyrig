"""Configuration management for Markdown files.

This module provides the MarkdownConfigFile class for managing Markdown files
(.md files) that require specific content but allow user extensions.

MarkdownConfigFile is commonly used for:
- README.md files with required project header
- Documentation files with required structure
- Changelog files with required format
- Contributing guidelines

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
    ...         return '''# My Project
    ...
    ... Project description goes here.
    ... '''
"""

from pyrig.dev.configs.base.text import TextConfigFile


class MarkdownConfigFile(TextConfigFile):
    r"""Abstract base class for Markdown configuration files.

    Extends TextConfigFile to use the "md" file extension. All functionality
    is inherited from TextConfigFile - only the extension differs.

    This class is useful for creating Markdown files with required content
    (headers, badges, sections) while allowing users to add their own content.

    Subclasses must implement:
        - `get_parent_path`: Directory containing the .md file
        - `get_content_str`: Required Markdown content that must be present

    Example:
        >>> from pathlib import Path
        >>> from pyrig.dev.configs.base.markdown import MarkdownConfigFile
        >>>
        >>> class MyMarkdownFile(MarkdownConfigFile):
        ...     @classmethod
        ...     def get_parent_path(cls) -> Path:
        ...         return Path("docs")
        ...
        ...     @classmethod
        ...     def get_content_str(cls) -> str:
        ...         return "# Documentation\n\n"

    See Also:
        pyrig.dev.configs.base.text.TextConfigFile: Parent class with full docs
        pyrig.dev.configs.base.badges_md.BadgesMarkdownConfigFile: For badge files
    """

    @classmethod
    def get_file_extension(cls) -> str:
        """Get the Markdown file extension.

        Returns:
            The string "md" (without the leading dot).

        Example:
            For a class named ReadmeConfigFile::

                get_filename() -> "readme"
                get_file_extension() -> "md"
                get_path() -> Path("README.md")
        """
        return "md"
