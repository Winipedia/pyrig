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

        Uses PyYAML's safe_load() to securely parse the file. The safe_load
        method prevents arbitrary code execution and is suitable for untrusted
        input. If the file is empty or contains only whitespace, returns an
        empty dict.

        Returns:
            The parsed YAML content as a dict or list. Returns an empty dict
            if the file is empty or contains only whitespace.

        Example:
            Load a YAML file::

                # .pre-commit-config.yaml contains:
                # repos:
                #   - repo: https://github.com/pre-commit/pre-commit-hooks
                #     rev: v4.4.0

                config = MyYamlConfigFile.load()
                # Returns: {"repos": [{"repo": "...", "rev": "v4.4.0"}]}

            Empty file handling::

                # Empty file or whitespace-only file
                config = MyYamlConfigFile.load()
                # Returns: {}
        """
        return yaml.safe_load(cls.get_path().read_text(encoding="utf-8")) or {}

    @classmethod
    def dump(cls, config: dict[str, Any] | list[Any]) -> None:
        """Write configuration to the YAML file.

        Uses PyYAML's safe_dump() to write the configuration. The safe_dump
        method prevents Python object serialization and produces clean,
        portable YAML. Key order is preserved (sort_keys=False).

        Args:
            config: The configuration to write. Can be a dict or list. Nested
                structures are supported.

        Example:
            Write a YAML file::

                config = {
                    "repos": [
                        {
                            "repo": "https://github.com/pre-commit/pre-commit-hooks",
                            "rev": "v4.4.0",
                            "hooks": [
                                {"id": "trailing-whitespace"},
                                {"id": "end-of-file-fixer"}
                            ]
                        }
                    ]
                }
                MyYamlConfigFile.dump(config)

                # Creates .pre-commit-config.yaml:
                # repos:
                # - repo: https://github.com/pre-commit/pre-commit-hooks
                #   rev: v4.4.0
                #   hooks:
                #   - id: trailing-whitespace
                #   - id: end-of-file-fixer

        Note:
            Key order is preserved (sort_keys=False) to maintain readability
            and match user expectations.
        """
        with cls.get_path().open("w") as f:
            yaml.safe_dump(config, f, sort_keys=False)

    @classmethod
    def get_file_extension(cls) -> str:
        """Get the YAML file extension.

        Returns:
            The string "yaml" (without the leading dot).

        Example:
            For a class named PreCommitConfigFile::

                get_filename() -> "pre_commit_config"
                get_file_extension() -> "yaml"
                get_path() -> Path(".pre-commit-config.yaml")

        Note:
            For the "yml" extension variant, use YmlConfigFile instead.
        """
        return "yaml"
