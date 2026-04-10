"""Exceptions related to dumping to config files."""

from typing import TYPE_CHECKING

from pyrig.core.exceptions.base.config_file import ConfigFileError

if TYPE_CHECKING:
    from pyrig.rig.configs.base.config_file import ConfigFile


class ConfigFileDumpForbiddenError(ConfigFileError):
    """Exception raised when dumping to a config file is forbidden."""

    def __init__(self, config_file: "ConfigFile", reason: str) -> None:
        """Initialize the exception with a reason.

        Args:
            config_file: The config file that cannot be dumped to.
            reason: Explanation of why dumping is forbidden.
        """
        super().__init__(f"Dumping to {config_file} is forbidden because {reason}")
