"""Security scanner command construction and badge metadata."""

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.tool import Group, Tool
from pyrig.rig.tools.package_manager import PackageManager


class SecurityChecker(Tool):
    """Wrapper for the `bandit` security checker.

    Constructs `bandit` command-line arguments for scanning the project's
    source code for common security vulnerabilities.
    """

    def group(self) -> str:
        """Return `Group.CODE_QUALITY`."""
        return Group.CODE_QUALITY

    def image_url(self) -> str:
        """Return the badge image URL for `bandit`."""
        return "https://img.shields.io/badge/security-bandit-yellow.svg"

    def link_url(self) -> str:
        """Return the URL of the `bandit` project page."""
        return "https://github.com/PyCQA/bandit"

    def name(self) -> str:
        """Return `'bandit'`."""
        return "bandit"

    def check_args(self, *args: str) -> Args:
        """Construct `bandit` arguments for a recursive scan of the source package.

        Args:
            *args: Additional `bandit` arguments placed before the recursive
                flag and target path.

        Returns:
            Args for `bandit [args] -r <source package root>`.
        """
        return self.args(
            *args,
            "-r",
            PackageManager.I.package_root().as_posix(),
        )
