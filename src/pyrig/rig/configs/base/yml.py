"""Base classes for ``.yml`` configuration files.

Extends the YAML configuration base with the ``.yml`` file extension, for use
in projects or tooling that prefer ``.yml`` over ``.yaml``.
"""

from pyrig.rig.configs.base.config_file import ConfigData, ConfigDict
from pyrig.rig.configs.base.yaml import YAMLConfigFile


class YMLConfigFile[ConfigT: ConfigData](YAMLConfigFile[ConfigT]):
    """Base class for ``.yml`` configuration files.

    Overrides the file extension to ``"yml"``, inheriting all YAML load and dump
    behavior from ``YAMLConfigFile``. Use this class when the configuration
    structure may be a dict or a list. For dict-only configurations, prefer
    ``YMLDictConfigFile``.

    Subclasses must implement:
        - ``parent_path``: The directory that contains the ``.yml`` file.
        - ``stem``: The filename without its extension.
        - ``_configs``: The expected configuration structure.
    """

    def extension(self) -> str:
        """Return ``"yml"``."""
        return "yml"


class YMLDictConfigFile(YMLConfigFile[ConfigDict]):
    """Base class for ``.yml`` configuration files with a dict structure.

    Locks the generic type parameter to ``ConfigDict``, providing dict-specific
    type safety while inheriting all YAML functionality from ``YMLConfigFile``.
    This is the standard base class for all dict-based ``.yml`` configurations
    in this project.

    Subclasses must implement:
        - ``parent_path``: The directory that contains the ``.yml`` file.
        - ``stem``: The filename without its extension.
        - ``_configs``: The expected configuration as a ``ConfigDict``.

    Example:
        >>> from pathlib import Path
        >>> from pyrig.rig.configs.base.yml import YMLDictConfigFile
        >>>
        >>> class DocsBuilderConfigFile(YMLDictConfigFile):
        ...
        ...     def parent_path(self) -> Path:
        ...         return Path()
        ...
        ...     def stem(self) -> str:
        ...         return "mkdocs"
        ...
        ...
        ...     def _configs(self) -> ConfigDict:
        ...         return {"site_name": "My Project", "theme": {"name": "material"}}
    """
