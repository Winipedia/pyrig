"""Base class for managing YAML configuration files."""

from typing import Any

import yaml

from pyrig.core.strings import open_path_with_utf8, read_text_utf8
from pyrig.rig.configs.base.config_file import ConfigFile


class YAMLConfigFile[ConfigT: dict[str, Any] | list[Any]](ConfigFile[ConfigT]):
    """Base class for YAML configuration files.

    Parses and serializes YAML content using PyYAML's safe-mode functions,
    which refuse to construct or represent arbitrary Python objects.

    Subclasses must implement `parent_path()`, `stem()`, and `_configs()`.

    Example:
        >>> from pathlib import Path
        >>> from pyrig.rig.configs.base.yaml import YAMLConfigFile
        >>>
        >>> class MyWorkflowConfigFile(YAMLConfigFile):
        ...     def parent_path(self) -> Path:
        ...         return Path(".github/workflows")
        ...
        ...     def stem(self) -> str:
        ...         return "my_workflow"
        ...
        ...     def _configs(self) -> dict:
        ...         return {"name": "My Workflow", "on": ["push", "pull_request"]}
    """

    def _dump(self, configs: ConfigT) -> None:
        """Write configuration to the YAML file, preserving key order.

        Non-ASCII characters are written literally rather than escaped.

        Args:
            configs: Configuration dict or list to serialize and write.
        """
        with open_path_with_utf8(self.path(), mode="w") as f:
            yaml.safe_dump(configs, f, sort_keys=False, allow_unicode=True)

    def _load(self) -> ConfigT:
        """Read and parse the YAML file from disk, returning a dict or list."""
        return yaml.safe_load(read_text_utf8(self.path()))

    def extension(self) -> str:
        """Return `"yaml"`, the fixed extension for YAML files."""
        return "yaml"
