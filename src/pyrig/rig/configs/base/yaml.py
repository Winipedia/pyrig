"""YAML configuration file management.

Provides YamlConfigFile base class for YAML files using PyYAML's safe_load and
safe_dump for secure parsing.

Example:
    >>> from pathlib import Path
    >>> from typing import Any
    >>> from pyrig.rig.configs.base.yaml import YamlConfigFile
    >>>
    >>> class MyWorkflowConfigFile(YamlConfigFile):
    ...
    ...     def parent_path(self) -> Path:
    ...         return Path(".github/workflows")
    ...
    ...
    ...     def _configs(self) -> ConfigDict:
    ...         return {"name": "My Workflow", "on": ["push", "pull_request"]}
"""

import yaml

from pyrig.rig.configs.base.base import ConfigFile, ConfigT


class YamlConfigFile(ConfigFile[ConfigT]):
    """Base class for YAML configuration files.

    Uses PyYAML's safe methods to prevent code execution. Preserves key order
    (sort_keys=False).

    Subclasses must implement:
        - `parent_path`: Directory containing the YAML file
        - `_configs`: Expected YAML configuration structure

    Example:
        >>> class MyConfigFile(YamlConfigFile):
        ...
        ...     def parent_path(self) -> Path:
        ...         return Path()
        ...
        ...
        ...     def _configs(self) -> ConfigDict:
        ...         return {"setting": "value"}
    """

    def _load(self) -> ConfigT:
        """Load and parse the YAML file using safe_load.

        Returns:
            Parsed YAML content as dict or list. Empty dict if file is empty.
        """
        return yaml.safe_load(self.path().read_text(encoding="utf-8"))

    def _dump(self, config: ConfigT) -> None:
        """Write configuration to YAML file using safe_dump.

        Args:
            config: Configuration dict or list to write.
        """
        with self.path().open("w") as f:
            yaml.safe_dump(config, f, sort_keys=False)

    def extension(self) -> str:
        """Return "yaml"."""
        return "yaml"
