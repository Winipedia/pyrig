"""README.md configuration file generator.

Provides a concrete configuration file class for the project's README.md,
placing it at the project root with a fixed filename and no opt-out support.
"""

from pathlib import Path

from pyrig.rig.configs.base.badges_md import BadgesMarkdownConfigFile


class ReadmeConfigFile(BadgesMarkdownConfigFile):
    """Concrete configuration manager for the project's README.md.

    Inherits badge generation, description management, and merge logic from
    ``BadgesMarkdownConfigFile``. Places README.md at the project root, fixes
    the filename stem to ``"README"``, and overrides ``is_unwanted()`` to ensure
    README.md is always managed — users cannot opt out via an empty file.

    Examples:
        Validate or generate README.md::

            ReadmeConfigFile.I.validate()
    """

    def stem(self) -> str:
        """Return the filename stem ``"README"``.

        Returns:
            str: Always ``"README"``.
        """
        return "README"

    def parent_path(self) -> Path:
        """Return the project root as the parent directory.

        Places README.md at the top level of the project, where it is
        discoverable by GitHub, PyPI, and other tooling.

        Returns:
            Path: ``Path()``, resolving to the current working directory
            (the project root).
        """
        return Path()
