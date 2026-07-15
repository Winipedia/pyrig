"""Abstract base class for GitHub issue template configuration files."""

from pathlib import Path

from pyrig.rig.configs.base.yaml import YMLDictConfigFile
from pyrig.rig.tools.version_control.remote.controller import (
    RemoteVersionController,
)


class IssueTemplateConfigFile(YMLDictConfigFile):
    """Abstract base class for files in `.github/ISSUE_TEMPLATE/`.

    Fixes `parent_path()` to the GitHub issue template directory, so
    subclasses only need to implement `stem()` and `_configs()`.

    Example:
        >>> from typing import Any
        >>> from pyrig.rig.configs.base.issue_template import (
        ...     IssueTemplateConfigFile,
        ... )
        >>>
        >>> class MyIssueTemplateConfigFile(IssueTemplateConfigFile):
        ...     def stem(self) -> str:
        ...         return "my_template"
        ...
        ...     def _configs(self) -> dict[str, Any]:
        ...         return {"name": "My Template", "description": "..."}
    """

    def parent_path(self) -> Path:
        """Return the GitHub issue template directory."""
        return RemoteVersionController.I.config_dir() / "ISSUE_TEMPLATE"
