"""Configuration management for README.md files.

Manages README.md with project name header and status badges (build, coverage,
version, license, Python version). Used on GitHub, PyPI, and in container images.

See Also:
    pyrig.dev.configs.base.badges_md.BadgesMarkdownConfigFile
"""

from pathlib import Path

from pyrig.dev.configs.base.badges_md import BadgesMarkdownConfigFile


class ReadmeConfigFile(BadgesMarkdownConfigFile):
    """README.md configuration manager.

    Generates README.md with project name header and status badges. Used on
    GitHub and PyPI. Always required (is_unwanted() returns False).

    Examples:
        Generate README.md::

            ReadmeConfigFile()

    See Also:
        pyrig.dev.configs.base.badges_md.BadgesMarkdownConfigFile
        pyrig.dev.configs.pyproject.PyprojectConfigFile
    """

    @classmethod
    def get_filename(cls) -> str:
        """Get the README filename.

        Returns:
            str: "README" (extension added by parent).
        """
        return "README"

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the parent directory for README.md.

        Returns:
            Path: Project root.
        """
        return Path()

    @classmethod
    def is_unwanted(cls) -> bool:
        """Check if README.md is unwanted.

        Returns:
            bool: Always False (README.md is always required).
        """
        return False
