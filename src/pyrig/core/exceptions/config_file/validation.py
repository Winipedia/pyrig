"""Exceptions related to config file validation."""

from typing import TYPE_CHECKING

from pyrig.core.exceptions.base.config_file import ConfigFileError

if TYPE_CHECKING:
    from pyrig.rig.configs.base.config_file import ConfigFile


class ConfigFileValidationError(ConfigFileError):
    """Raised when a config file fails validation."""

    def __init__(self, config_file: "ConfigFile") -> None:
        """Initialize the exception.

        Args:
            config_file: The config file that failed validation.
        """
        msg = f"Validation failed for {config_file}"
        super().__init__(msg)
