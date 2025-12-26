"""Configuration management for .yml files.

This module provides the YmlConfigFile class for managing .yml configuration files.
This is a variant of YamlConfigFile that uses the "yml" extension instead of "yaml".

The .yml extension is commonly used for:
- MkDocs configuration (mkdocs.yml)
- Docker Compose files (docker-compose.yml)
- Some CI/CD configurations

Functionally identical to YamlConfigFile, only the file extension differs.

Example:
    >>> from pathlib import Path
    >>> from typing import Any
    >>> from pyrig.dev.configs.base.yml import YmlConfigFile
    >>>
    >>> class MkDocsConfigFile(YmlConfigFile):
    ...     @classmethod
    ...     def get_parent_path(cls) -> Path:
    ...         return Path()
    ...
    ...     @classmethod
    ...     def get_configs(cls) -> dict[str, Any]:
    ...         return {
    ...             "site_name": "My Project",
    ...             "theme": {"name": "material"}
    ...         }
"""

from pyrig.dev.configs.base.yaml import YamlConfigFile


class YmlConfigFile(YamlConfigFile):
    """Abstract base class for .yml configuration files.

    Extends YamlConfigFile to use the "yml" file extension instead of "yaml".
    All functionality is inherited from YamlConfigFile - only the extension
    differs.

    This class is useful for files that conventionally use the .yml extension,
    such as mkdocs.yml or docker-compose.yml.

    Subclasses must implement:
        - `get_parent_path`: Directory containing the .yml file
        - `get_configs`: Expected YAML configuration structure

    Example:
        >>> from pathlib import Path
        >>> from typing import Any
        >>> from pyrig.dev.configs.base.yml import YmlConfigFile
        >>>
        >>> class MyConfigFile(YmlConfigFile):
        ...     @classmethod
        ...     def get_parent_path(cls) -> Path:
        ...         return Path()
        ...
        ...     @classmethod
        ...     def get_configs(cls) -> dict[str, Any]:
        ...         return {"setting": "value"}

    See Also:
        pyrig.dev.configs.base.yaml.YamlConfigFile: Parent class with full docs
    """

    @classmethod
    def get_file_extension(cls) -> str:
        """Get the .yml file extension.

        Returns:
            The string "yml" (without the leading dot).

        Example:
            For a class named MkDocsConfigFile::

                get_filename() -> "mkdocs"
                get_file_extension() -> "yml"
                get_path() -> Path("mkdocs.yml")

        Note:
            For the "yaml" extension variant, use YamlConfigFile instead.
        """
        return "yml"
