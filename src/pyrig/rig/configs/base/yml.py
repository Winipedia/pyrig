"""Base classes for `.yml` configuration files.

Extends the YAML configuration base with the `.yml` file extension, for use
in projects or tooling that prefer `.yml` over `.yaml`.
"""

from typing import Any

from pyrig.rig.configs.base.yaml import YAMLConfigFile


class YMLConfigFile[ConfigT: dict[str, Any] | list[Any]](YAMLConfigFile[ConfigT]):
    """Base class for `.yml` configuration files.

    Uses `.yml` as the file extension instead of `.yaml`. Use this class when
    the configuration structure may be a dict or a list. For dict-only
    configurations, prefer `YMLDictConfigFile`.

    Subclasses must implement `parent_path()`, `stem()`, and `_configs()`.
    """

    def extension(self) -> str:
        """Return `"yml"`."""
        return "yml"


class YMLDictConfigFile(YMLConfigFile[dict[str, Any]]):
    """Base class for `.yml` configuration files with a dict structure.

    Fixes the `ConfigT` type parameter to `dict[str, Any]`, so subclasses get
    properly typed `load()`, `dump()`, and `configs()` for `.yml` files
    structured as an object at the root level.

    Example:
        >>> from pathlib import Path
        >>> from pyrig.rig.configs.base.yml import YMLDictConfigFile
        >>>
        >>> class MySiteConfigFile(YMLDictConfigFile):
        ...     def parent_path(self) -> Path:
        ...         return Path()
        ...
        ...     def stem(self) -> str:
        ...         return "mysite"
        ...
        ...     def _configs(self) -> dict[str, Any]:
        ...         return {"site_name": "My Project", "theme": {"name": "material"}}
    """
