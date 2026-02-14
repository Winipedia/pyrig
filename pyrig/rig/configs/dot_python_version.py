"""Manages .python-version files for pyenv/asdf.

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
    """Manages .python-version files for pyenv/asdf.

    Creates .python-version with minimum supported Python version from pyproject.toml.

    See Also:
        pyrig.rig.configs.pyproject.PyprojectConfigFile.I.first_supported_python_version
    """

    @classmethod
    def filename(cls) -> str:
        """Return empty string to produce '.python-version'."""
        return ""

    @classmethod
    def extension(cls) -> str:
        """Return 'python-version' extension."""
        return "python-version"

    @classmethod
    def parent_path(cls) -> Path:
        """Return project root."""
        return Path()

    @classmethod
    def lines(cls) -> list[str]:
        """Get minimum supported Python version from pyproject.toml."""
        return [str(PyprojectConfigFile.I.first_supported_python_version())]

    @classmethod
    def should_override_content(cls) -> bool:
        """Override content; only one .python-version is needed."""
        return True
