"""Configuration management for README.md files.

This module provides the ReadmeConfigFile class for creating and managing the
project's README.md file, which serves as the primary documentation and landing
page for the project on GitHub and PyPI.

The generated README.md includes:
    - Project name as the main header (H1)
    - Status badges (build, coverage, version, license, Python version)
    - Placeholder content for users to customize
    - Proper Markdown formatting

The README.md is automatically included in:
    - GitHub repository landing page
    - PyPI package description
    - Container images (copied during build)

See Also:
    pyrig.dev.configs.base.badges_md.BadgesMarkdownConfigFile
        Base class that provides badge generation
"""

from pathlib import Path

from pyrig.dev.configs.base.badges_md import BadgesMarkdownConfigFile


class ReadmeConfigFile(BadgesMarkdownConfigFile):
    """Configuration file manager for README.md.

    Generates a README.md file in the project root with the project name as
    a header and status badges. The file serves as the primary documentation
    for the project on GitHub and PyPI.

    The generated README includes:
        - Project name header (H1)
        - Status badges (build, coverage, version, license, Python version)
        - Placeholder content for customization

    Examples:
        Generate README.md::

            from pyrig.dev.configs.markdown.readme import ReadmeConfigFile

            # Creates README.md in project root
            ReadmeConfigFile()

    Note:
        README.md is always required and cannot be marked as unwanted.
        The is_unwanted() method always returns False.

    See Also:
        pyrig.dev.configs.base.badges_md.BadgesMarkdownConfigFile
            Provides badge generation functionality
        pyrig.dev.configs.pyproject.PyprojectConfigFile
            Used to get project metadata for badges
    """

    @classmethod
    def get_filename(cls) -> str:
        """Get the README filename.

        Returns:
            str: The string "README" (extension .md is added by parent class).
        """
        return "README"

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the parent directory for README.md.

        Returns:
            Path: Empty Path() representing the project root directory.
        """
        return Path()

    @classmethod
    def is_unwanted(cls) -> bool:
        """Check if README.md is unwanted.

        README.md is always required for proper project documentation on
        GitHub and PyPI, so this method always returns False.

        Returns:
            bool: Always False, as README.md is never unwanted.
        """
        # README.md is never unwanted
        return False
