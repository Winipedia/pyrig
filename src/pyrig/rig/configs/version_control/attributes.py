"""Configuration management for `.gitattributes` files."""

from pathlib import Path
from typing import override

from pyrig.rig.configs.base.string_ import StringConfigFile
from pyrig.rig.tools.formatting.shell import ShellFormatter
from pyrig.rig.tools.version_control.controller import VersionController


class VersionControllerAttributesConfigFile(StringConfigFile):
    """Config file manager for `.gitattributes`.

    Declares the git attributes that apply to any project regardless of what
    it does: line-ending normalization and language-aware diff drivers for
    Markdown, Python, and shell files.
    """

    @override
    def content(self) -> str:
        """Return the required `.gitattributes` content.

        Returns:
            The baseline attribute rules for line endings and diff drivers.
        """
        return f"""* text=auto eol={VersionController.I.end_of_line()}

*.md diff=markdown
*.py diff=python
*.sh diff={ShellFormatter.I.dialect()}
"""

    @override
    def extension(self) -> str:
        """Return an empty string, since `.gitattributes` has no extension."""
        return ""

    @override
    def extension_separator(self) -> str:
        """Return an empty string, so `.gitattributes` has no trailing dot."""
        return ""

    @override
    def parent_path(self) -> Path:
        """Return the project root as the parent directory."""
        return Path()

    @override
    def stem(self) -> str:
        """Return `'.gitattributes'`, the filename with no extension to split off."""
        return ".gitattributes"
