"""Configuration management for YAML files.

This module provides the YamlConfigFile class for managing YAML configuration
files. It uses PyYAML's safe_load and safe_dump for secure parsing and writing.

YAML files are commonly used for:
- GitHub Actions workflows (.github/workflows/*.yaml)
- Pre-commit configuration (.pre-commit-config.yaml)
- MkDocs configuration (mkdocs.yml)
- CI/CD configuration files

Example:
    >>> from pathlib import Path
    >>> from typing import Any
    >>> from pyrig.dev.configs.base.yaml import YamlConfigFile
    >>>
    >>> class MyWorkflowFile(YamlConfigFile):
    ...     @classmethod
    ...     def get_parent_path(cls) -> Path:
    ...         return Path(".github/workflows")
    ...
    ...     @classmethod
    ...     def get_configs(cls) -> dict[str, Any]:
    ...         return {
    ...             "name": "My Workflow",
    ...             "on": ["push", "pull_request"]
    ...         }
"""

from typing import Any

import yaml

from pyrig.dev.configs.base.base import ConfigFile


class YamlConfigFile(ConfigFile):
    """Abstract base class for YAML configuration files.

    Provides YAML-specific load and dump implementations using PyYAML's
    safe methods. The safe methods prevent arbitrary code execution and
    are suitable for untrusted input.

    YAML files are written with:
    - Original key order preserved (sort_keys=False)
    - Proper indentation and formatting
    - Safe dumping (no Python object serialization)

    Subclasses must implement:
        - `get_parent_path`: Directory containing the YAML file
        - `get_configs`: Expected YAML configuration structure

    Example:
        >>> from pathlib import Path
        >>> from typing import Any
        >>> from pyrig.dev.configs.base.yaml import YamlConfigFile
        >>>
        >>> class MyConfigFile(YamlConfigFile):
        ...     @classmethod
        ...     def get_parent_path(cls) -> Path:
        ...         return Path()
        ...
        ...     @classmethod
        ...     def get_configs(cls) -> dict[str, Any]:
        ...         return {"setting": "value"}
    """

    @classmethod
    def load(cls) -> dict[str, Any] | list[Any]:
        """Load and parse the YAML configuration file.

        Returns:
            The parsed YAML content as a dict or list.
        """
        return yaml.safe_load(cls.get_path().read_text(encoding="utf-8")) or {}

    @classmethod
    def dump(cls, config: dict[str, Any] | list[Any]) -> None:
        """Write configuration to the YAML file.

        Args:
            config: The configuration to write.
        """
        with cls.get_path().open("w") as f:
            yaml.safe_dump(config, f, sort_keys=False)

    @classmethod
    def get_file_extension(cls) -> str:
        """Get the YAML file extension.

        Returns:
            The string "yaml".
        """
        return "yaml"
