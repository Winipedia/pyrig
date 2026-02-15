""".yml file configuration management.

Provides YmlConfigFile base class for .yml files. Functionally identical to
YamlConfigFile with "yml" extension instead of "yaml".

Example:
    >>> from pathlib import Path
    >>> from typing import Any
    >>> from pyrig.rig.configs.base.yml import YmlConfigFile
    >>>
    >>> class MkDocsConfigFile(YmlConfigFile):
    ...
    ...     def parent_path(self) -> Path:
    ...         return Path()
    ...
    ...
    ...     def _configs(self) -> dict[str, Any]:
    ...         return {"site_name": "My Project", "theme": {"name": "material"}}
"""

from pyrig.rig.configs.base.yaml import YamlConfigFile


class YmlConfigFile(YamlConfigFile):
    """Base class for .yml files.

    Extends YamlConfigFile with "yml" extension. All functionality inherited.

    Subclasses must implement:
        - `parent_path`: Directory containing the .yml file
        - `_configs`: Expected YAML configuration structure

    See Also:
        pyrig.rig.configs.base.yaml.YamlConfigFile: Parent class
    """

    def extension(self) -> str:
        """Return "yml"."""
        return "yml"
