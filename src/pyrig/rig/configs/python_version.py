"""Configuration management for `.python-version` files.

Sets the minimum supported Python version so that pyenv and asdf can
automatically select the correct interpreter for the project.
"""

from pathlib import Path

from pyrig.rig.configs.base.string_ import StringConfigFile
from pyrig.rig.configs.pyproject import PyprojectConfigFile


class PythonVersionConfigFile(StringConfigFile):
    """Management of the `.python-version` file at the project root.

    Ensures the minimum supported Python version, derived from the
    `requires-python` constraint in `pyproject.toml`, is present in the file.
    """

    def extension(self) -> str:
        """Return an empty string; `.python-version` has no file extension."""
        return ""

    def extension_separator(self) -> str:
        """Return an empty string, overriding the default `.` separator.

        Prevents a trailing dot from being appended when the extension is
        empty, so the path remains `.python-version` instead of
        `.python-version.`.

        Returns:
            Always an empty string.
        """
        return ""

    def content(self) -> str:
        """Return the minimum supported Python version, with a trailing newline.

        Returns:
            The minimum supported Python version string (e.g., `"3.8"`),
            derived from the `requires-python` constraint in
            `pyproject.toml`, followed by a trailing newline.
        """
        return f"{PyprojectConfigFile.I.first_supported_python_version()}\n"

    def parent_path(self) -> Path:
        """Return the project root as the parent directory."""
        return Path()

    def stem(self) -> str:
        """Return `.python-version` as the filename stem."""
        return ".python-version"
