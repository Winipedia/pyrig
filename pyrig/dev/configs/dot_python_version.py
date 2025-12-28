"""Manages .python-version files for pyenv/asdf.

Creates .python-version with minimum supported Python version from pyproject.toml.
Used by pyenv/asdf to auto-select Python version.

See Also:
    https://github.com/pyenv/pyenv
    pyrig.dev.configs.pyproject.PyprojectConfigFile
"""

from pathlib import Path
from typing import Any

from pyrig.dev.configs.base.base import ConfigFile
from pyrig.dev.configs.pyproject import PyprojectConfigFile


class DotPythonVersionConfigFile(ConfigFile):
    """Manages .python-version files for pyenv/asdf.

    Creates .python-version with minimum supported Python version from pyproject.toml.

    Attributes:
        VERSION_KEY: Dictionary key for version string ("version").

    See Also:
        pyrig.dev.configs.pyproject.PyprojectConfigFile.get_first_supported_python_version
    """

    VERSION_KEY = "version"

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
    def get_configs(cls) -> dict[str, Any]:
        """Get minimum supported Python version from pyproject.toml."""
        return {
            cls.VERSION_KEY: str(
                PyprojectConfigFile.get_first_supported_python_version()
            )
        }

    @classmethod
    def _load(cls) -> dict[str, Any]:
        """Load Python version from .python-version file."""
        return {cls.VERSION_KEY: cls.get_path().read_text(encoding="utf-8")}

    @classmethod
    def _dump(cls, config: dict[str, Any] | list[Any]) -> None:
        """Write Python version to .python-version file."""
        if not isinstance(config, dict):
            msg = f"Cannot dump {config} to .python-version file."
            raise TypeError(msg)
        cls.get_path().write_text(config[cls.VERSION_KEY], encoding="utf-8")
