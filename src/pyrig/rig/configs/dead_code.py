"""Management of the project-root Vulture whitelist file."""

from pathlib import Path

from pyrig.rig.configs.base.python import PythonConfigFile
from pyrig.rig.tools.linting.dead_code import DeadCodeChecker


class DeadCodeCheckerConfigFile(PythonConfigFile):
    """Config file manager for `vulture_whitelist.py`.

    Its required content is a single module docstring line. User-added
    whitelist references are preserved across validation runs.
    """

    def content(self) -> str:
        """Return a one-line module docstring followed by a trailing newline."""
        return '"""Explicit references for reviewed dead code false positives."""\n'

    def parent_path(self) -> Path:
        """Return the project root as the parent directory."""
        return Path()

    def stem(self) -> str:
        """Return `"vulture_whitelist"`."""
        return f"{DeadCodeChecker.I.config_name()}_whitelist"
