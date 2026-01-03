"""Manages .python-version files for pyenv/asdf.

Creates .python-version with minimum supported Python version from pyproject.toml.
Used by pyenv/asdf to auto-select Python version.

See Also:
    https://github.com/pyenv/pyenv
    pyrig.dev.configs.pyproject.PyprojectConfigFile
"""

from pathlib import Path

from pyrig.dev.configs.base.text import TextConfigFile
from pyrig.dev.configs.pyproject import PyprojectConfigFile


class DotPythonVersionConfigFile(TextConfigFile):
    """Manages .python-version files for pyenv/asdf.

    Creates .python-version with minimum supported Python version from pyproject.toml.

    Attributes:
        VERSION_KEY: Dictionary key for version string ("version").

    See Also:
        pyrig.dev.configs.pyproject.PyprojectConfigFile.get_first_supported_python_version
    """

    @classmethod
    def get_filename(cls) -> str:
        """Return empty string to produce '.python-version'."""
        return ""

    @classmethod
    def get_file_extension(cls) -> str:
        """Return 'python-version' extension."""
        return "python-version"

    @classmethod
    def get_parent_path(cls) -> Path:
        """Return project root."""
        return Path()

    @classmethod
    def get_content_str(cls) -> str:
        """Get minimum supported Python version from pyproject.toml."""
        return str(PyprojectConfigFile.get_first_supported_python_version())

    @classmethod
    def override_content(cls) -> bool:
        """Overriding content bc only one .python-version needed."""
        return True
