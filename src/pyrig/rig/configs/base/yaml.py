"""Base class for managing YAML configuration files."""

from typing import Any

from ruamel.yaml import YAML
from ruamel.yaml.nodes import ScalarNode
from ruamel.yaml.representer import RoundTripRepresenter
from ruamel.yaml.scalarstring import DoubleQuotedScalarString, LiteralScalarString

from pyrig.core.strings import is_multiline, open_path_with_utf8, read_text_utf8
from pyrig.rig.configs.base.config_file import ConfigFile


def _represent_str(representer: RoundTripRepresenter, data: str) -> ScalarNode:
    """Represent a string in YAML.

    Represents multi-line strings as literal block scalars and single-line
    strings as double-quoted scalars.

    Args:
        representer: The YAML representer.
        data: The string to represent.

    Returns:
        The YAML representation of the string
    """
    if is_multiline(data):
        return representer.represent_literal_scalarstring(LiteralScalarString(data))
    return representer.represent_double_quoted_scalarstring(
        DoubleQuotedScalarString(data),
    )


_YAML = YAML()
_YAML.indent(mapping=2, sequence=4, offset=2)
_YAML.explicit_start = True
_YAML.explicit_end = True
_YAML.compact_seq_map = False
_YAML.representer.add_representer(str, _represent_str)


class YAMLConfigFile[ConfigT: dict[str, Any] | list[Any]](ConfigFile[ConfigT]):
    """Base class for YAML configuration files.

    Parses and serializes YAML content using `ruamel.yaml`, which refuses to
    construct or represent arbitrary Python objects (only ruamel.yaml's
    separate, deprecated "unsafe" mode does that). Sequences are indented
    under their parent key, and a mapping inside a sequence item starts on
    its own line below the `-` rather than sharing its line.

    Every plain `str` is double-quoted automatically (e.g. GitHub Actions'
    `on:` key needs no special handling), and any string containing a
    newline is written as a literal block scalar automatically (e.g. a
    multi-line shell script), so subclasses never need to reach for
    `ruamel.yaml.scalarstring` themselves. Long single-line strings are
    wrapped across multiple physical lines by the dumper at ruamel's
    default 80-character width for readability; the wrapped lines are
    folded back into the original single-line value on load.

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

        Args:
            configs: Configuration dict or list to serialize and write.
        """
        with open_path_with_utf8(self.path(), mode="w") as f:
            _YAML.dump(configs, f)

    def _load(self) -> ConfigT:
        """Read and parse the YAML file from disk, returning a dict or list."""
        return _YAML.load(read_text_utf8(self.path()))

    def extension(self) -> str:
        """Return `"yaml"`, the fixed extension for YAML files."""
        return "yaml"


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
