""".yml file configuration management.

Provides YmlConfigFile base class for .yml files. Functionally identical to
YamlConfigFile with "yml" extension instead of "yaml".

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
    ...     def _get_configs(cls) -> dict[str, Any]:
    ...         return {"site_name": "My Project", "theme": {"name": "material"}}
"""

from pyrig.dev.configs.base.yaml import YamlConfigFile


class YmlConfigFile(YamlConfigFile):
    """Base class for .yml files.

    Extends YamlConfigFile with "yml" extension. All functionality inherited.

    Subclasses must implement:
        - `get_parent_path`: Directory containing the .yml file
        - `_get_configs`: Expected YAML configuration structure

    See Also:
        pyrig.dev.configs.base.yaml.YamlConfigFile: Parent class
    """

    @classmethod
    def get_file_extension(cls) -> str:
        """Return "yml"."""
        return "yml"
