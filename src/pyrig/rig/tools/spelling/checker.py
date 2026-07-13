"""CLI tool wrapper for spell checking source code and documentation."""

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.file import FileTool
from pyrig.rig.tools.base.tool import Group


class SpellChecker(FileTool):
    """Wrapper for the `typos` spell checker.

    Constructs `typos` command-line arguments for detecting and fixing
    spelling mistakes in source code, comments, and documentation.
    """

    def group(self) -> str:
        """Return `Group.CODE_QUALITY`."""
        return Group.CODE_QUALITY

    def image_url(self) -> str:
        """Return the badge image URL for `typos`."""
        return f"https://img.shields.io/badge/spell--check-{self.shield_name()}-blue"

    def link_url(self) -> str:
        """Return the URL of the `typos` project page."""
        return "https://github.com/crate-ci/typos"

    def name(self) -> str:
        """Return `'typos'`."""
        return "typos"

    def types(self) -> list[str]:
        """Return the list of file types that `typos` can check."""
        return ["text"]

    def check_fix_args(self, *args: str) -> Args:
        """Construct `typos` arguments with auto-fix enabled.

        Args:
            *args: Additional arguments forwarded to `typos`.

        Returns:
            Args for `typos --write-changes [args]`.
        """
        return self.check_args("--write-changes", *args)

    def check_args(self, *args: str) -> Args:
        """Construct `typos` arguments for checking without fixing.

        Args:
            *args: Additional arguments forwarded to `typos`.

        Returns:
            Args for `typos [args]`.
        """
        return self.args(*args)
