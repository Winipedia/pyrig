"""YAML configuration file management.

Provides YamlConfigFile base class for YAML files using PyYAML's safe_load and
safe_dump for secure parsing.

Example:
    >>> from pathlib import Path
    >>> from typing import Any
    >>> from pyrig.rig.configs.base.yaml import YamlConfigFile
    >>>
    >>> class MyWorkflowFile(YamlConfigFile):
    ...     @classmethod
    ...     def parent_path(cls) -> Path:
    ...         return Path(".github/workflows")
    ...
    ...     @classmethod
    ...     def _configs(cls) -> dict[str, Any]:
    ...         return {"name": "My Workflow", "on": ["push", "pull_request"]}
"""

from typing import Any

import yaml

from pyrig.rig.configs.base.base import ConfigFile


class YamlConfigFile(ConfigFile[dict[str, Any] | list[Any]]):
    """Base class for YAML configuration files.

    Uses PyYAML's safe methods to prevent code execution. Preserves key order
    (sort_keys=False).

    Subclasses must implement:
        - `parent_path`: Directory containing the YAML file
        - `_configs`: Expected YAML configuration structure

    Example:
        >>> class MyConfigFile(YamlConfigFile):
        ...     @classmethod
        ...     def parent_path(cls) -> Path:
        ...         return Path()
        ...
        ...     @classmethod
        ...     def _configs(cls) -> dict[str, Any]:
        ...         return {"setting": "value"}
    """

    @classmethod
    def _load(cls) -> dict[str, Any] | list[Any]:
        """Load and parse the YAML file using safe_load.

        Returns:
            Parsed YAML content as dict or list. Empty dict if file is empty.
        """
        return yaml.safe_load(cls.path().read_text(encoding="utf-8")) or {}

    @classmethod
    def _dump(cls, config: dict[str, Any] | list[Any]) -> None:
        """Write configuration to YAML file using safe_dump.

        Args:
            config: Configuration dict or list to write.
        """
        with cls.path().open("w") as f:
            yaml.safe_dump(config, f, sort_keys=False)

    @classmethod
    def extension(cls) -> str:
        """Return "yaml"."""
        return "yaml"
