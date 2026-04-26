"""Configuration management for .python-version files.

Sets the minimum supported Python version so that pyenv and asdf can
automatically select the correct interpreter for the project.
"""

from pathlib import Path

from pyrig.rig.configs.base.string_ import StringConfigFile
from pyrig.rig.configs.pyproject import PyprojectConfigFile


class DotPythonVersionConfigFile(StringConfigFile):
    """Manages the .python-version file at the project root.

    Writes the minimum supported Python version derived from the
    ``requires-python`` constraint in pyproject.toml. When updated, the file
    content is always replaced rather than appended to, ensuring it contains
    exactly one version string.
    """

    def stem(self) -> str:
        """Return '.python-version' as the filename stem."""
        return ".python-version"

    def extension_separator(self) -> str:
        """Return an empty string, overriding the default '.' separator.

        Prevents a trailing dot from being appended when the extension is
        empty, so the path remains '.python-version' instead of
        '.python-version.'.

        Returns:
            str: Always an empty string.
        """
        return ""

    def extension(self) -> str:
        """Return an empty string; .python-version has no file extension."""
        return ""

    def parent_path(self) -> Path:
        """Return the project root as the parent directory."""
        return Path()

    def lines(self) -> list[str]:
        """Return the file content as a list of lines.

        Returns:
            list[str]: A two-element list containing the minimum supported
                Python version string (e.g., ``"3.8"``) followed by an empty
                string that produces a trailing newline when the lines are
                joined.
        """
        return [str(PyprojectConfigFile.I.first_supported_python_version()), ""]

    def should_override_content(self) -> bool:
        """Return ``True`` to replace the entire file content on every update.

        The .python-version file must contain exactly one version string.
        Overriding rather than appending prevents stale versions from
        accumulating in the file.

        Returns:
            bool: Always ``True``.
        """
        return True
