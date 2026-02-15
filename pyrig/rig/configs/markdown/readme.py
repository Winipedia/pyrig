"""Configuration management for README.md files.

Manages README.md with project name header and status badges (build, coverage,
version, license, Python version). Used on GitHub, PyPI, and in container images.

See Also:
    pyrig.rig.configs.base.badges_md.BadgesMarkdownConfigFile
"""

from pathlib import Path

from pyrig.rig.configs.base.badges_md import BadgesMarkdownConfigFile


class ReadmeConfigFile(BadgesMarkdownConfigFile):
    """README.md configuration manager.

    Generates README.md with project name header and status badges. Used on
    GitHub and PyPI. Always required (is_unwanted() returns False).

    Examples:
        Generate README.md::

            ReadmeConfigFile.I.validate()

    See Also:
        pyrig.rig.configs.base.badges_md.BadgesMarkdownConfigFile
        pyrig.rig.configs.pyproject.PyprojectConfigFile
    """

    def filename(self) -> str:
        """Get the README filename.

        Returns:
            str: "README" (extension added by parent).
        """
        return "README"

    def parent_path(self) -> Path:
        """Get the parent directory for README.md.

        Returns:
            Path: Project root.
        """
        return Path()

    def is_unwanted(self) -> bool:
        """Check if README.md is unwanted.

        Returns:
            bool: Always False (README.md is always required).
        """
        return False
