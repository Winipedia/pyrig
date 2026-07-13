"""Security scanner command construction and badge metadata."""

from pathlib import Path

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.file import FileTool
from pyrig.rig.tools.base.tool import Group
from pyrig.rig.tools.linting.python import PythonLinter


class SecurityLinter(FileTool):
    """Wrapper for the `bandit` security checker.

    Constructs `bandit` command-line arguments for scanning source code for
    common security vulnerabilities.
    """

    def group(self) -> str:
        """Return `Group.CODE_QUALITY`."""
        return Group.CODE_QUALITY

    def image_url(self) -> str:
        """Return the badge image URL for `bandit`."""
        return f"https://img.shields.io/badge/security-{self.shield_name()}-yellow.svg"

    def link_url(self) -> str:
        """Return the URL of the `bandit` project page."""
        return "https://github.com/PyCQA/bandit"

    def name(self) -> str:
        """Return `'bandit'`."""
        return "bandit"

    def types(self) -> list[str]:
        """Return the list of file types that `bandit` can scan."""
        return PythonLinter.I.types()

    def check_config_args(self, path: Path, *args: str) -> Args:
        """Construct `bandit` arguments with a specific configuration file.

        Args:
            path: Path to the configuration file.
            *args: Additional `bandit` arguments.

        Returns:
            Args for `bandit -c [path] [args]`.
        """
        return self.args("-c", path.as_posix(), *args)

    def check_args(self, *args: str) -> Args:
        """Construct `bandit` arguments.

        No target path is baked in: bandit silently skips a file it can't
        parse as Python rather than erroring, but still logs a warning and
        wastes a whole-tree walk doing so, so callers are expected to
        supply the specific files to check.

        Args:
            *args: Additional `bandit` arguments, typically the file paths
                to check.

        Returns:
            Args for `bandit [args]`.
        """
        return self.args(*args)
