"""Wrapper around the check-merge-conflict tool."""

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.file import FileTool
from pyrig.rig.tools.base.tool import Group


class MergeConflictChecker(FileTool):
    """Type-safe wrapper for the pre-commit-hooks merge conflict marker checker."""

    def group(self) -> str:
        """Return `Group.CODE_QUALITY`, the badge group this tool belongs to."""
        return Group.CODE_QUALITY

    def image_url(self) -> str:
        """Return the badge image URL for check-merge-conflict."""
        return f"https://img.shields.io/badge/merge--conflict-{self.shield_name()}-blue"

    def link_url(self) -> str:
        """Return the URL of the pre-commit-hooks project page."""
        return "https://github.com/pre-commit/pre-commit-hooks"

    def name(self) -> str:
        """Return `"check-merge-conflict"`, this tool's CLI command name."""
        return "check-merge-conflict"

    def dev_dependencies(self) -> tuple[str, ...]:
        """Return the package providing `check-merge-conflict`."""
        return ("pre-commit-hooks",)

    def types(self) -> list[str]:
        """Return `["text"]`, matching every text file this tool can scan.

        Same broad scope as `SpellChecker`/`SecretsChecker`: a leftover
        merge conflict marker is a property of text in general, not of any
        single language, so it isn't restricted to a single file type.
        """
        return ["text"]

    def check_args(self, *args: str) -> Args:
        """Construct check-merge-conflict arguments.

        Unlike `SpellChecker`, this tool has no autofix mode: a leftover
        conflict marker means the merge itself was never actually resolved,
        so there's no safe automatic fix, only a report.

        Args:
            *args: Additional arguments forwarded to `check-merge-conflict`,
                typically the file paths to check.

        Returns:
            Args for `check-merge-conflict`.
        """
        return self.args(*args)
