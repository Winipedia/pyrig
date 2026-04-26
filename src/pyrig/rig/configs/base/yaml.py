"""YAML configuration file management.

Provides a base class for managing YAML configuration files. Uses PyYAML's
safe_load and safe_dump for secure parsing and serialization.

Example:
    >>> from pathlib import Path
    >>> from pyrig.rig.configs.base.yaml import YamlConfigFile
    >>>
    >>> class MyWorkflowConfigFile(YamlConfigFile):
    ...
    ...     def parent_path(self) -> Path:
    ...         return Path(".github/workflows")
    ...
    ...
    ...     def _configs(self) -> dict:
    ...         return {"name": "My Workflow", "on": ["push", "pull_request"]}
"""

import yaml

from pyrig.core.strings import read_text_utf8
from pyrig.rig.configs.base.config_file import ConfigData, ConfigFile


class YamlConfigFile[ConfigT: ConfigData](ConfigFile[ConfigT]):
    """Base class for YAML configuration files.

    Implements YAML-specific load and dump operations for the ConfigFile
    framework. Uses PyYAML's safe_load and safe_dump to prevent arbitrary
    code execution during parsing. Key insertion order is preserved in output
    (sort_keys=False).

    Subclasses must implement:
        - `parent_path`: Directory containing the YAML file
        - `_configs`: Expected YAML configuration structure
    """

    def _load(self) -> ConfigT:
        """Load and parse the YAML file using safe_load.

        Returns:
            Parsed YAML content as a dict or list.
        """
        return yaml.safe_load(read_text_utf8(self.path()))

    def _dump(self, configs: ConfigT) -> None:
        """Write configuration to the YAML file using safe_dump.

        Key insertion order is preserved (sort_keys=False).

        Args:
            configs: Configuration dict or list to write.
        """
        with self.path().open("w") as f:
            yaml.safe_dump(configs, f, sort_keys=False)

    def extension(self) -> str:
        """Return "yaml"."""
        return "yaml"
