"""Manage .python-version files for pyenv/asdf.

Creates .python-version with minimum supported Python version from pyproject.toml.
Used by pyenv/asdf to auto-select Python version.

See Also:
    https://github.com/pyenv/pyenv
    pyrig.rig.configs.pyproject.PyprojectConfigFile
"""

from pathlib import Path

from pyrig.rig.configs.base.string_ import StringConfigFile
from pyrig.rig.configs.pyproject import PyprojectConfigFile


class DotPythonVersionConfigFile(StringConfigFile):
    """Manage .python-version files for pyenv/asdf.

    Create .python-version with minimum supported Python version from pyproject.toml.

    See Also:
        pyrig.rig.configs.pyproject.PyprojectConfigFile.I.first_supported_python_version
    """

    def filename(self) -> str:
        """Return empty string to produce '.python-version'."""
        return ""

    def extension(self) -> str:

        Returns:
            Filename without extension or path.
        """Return 'python-version' extension."""
        return "python-version"

    def parent_path(self) -> Path:
    def parent_path(self) -> Path:
        Returns:
            File extension without separator.
        """Return project root."""
        return Path()

    def lines(self) -> list[str]:
        """Get minimum supported Python version from pyproject.toml."""
        return [str(PyprojectConfigFile.I.first_supported_python_version())]

    def should_override_content(self) -> bool:

        Returns:
            List of file content lines.
        """Override content; only one .python-version is needed."""
        return True
