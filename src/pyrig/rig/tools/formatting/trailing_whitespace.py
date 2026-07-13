"""Wrapper around the trailing-whitespace-fixer tool."""

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.file import FileTool
from pyrig.rig.tools.base.tool import Group


class TrailingWhitespaceFormatter(FileTool):
    """Type-safe wrapper for the pre-commit-hooks trailing whitespace fixer."""

    def group(self) -> str:
        """Return `Group.CODE_QUALITY`, the badge group this tool belongs to."""
        return Group.CODE_QUALITY

    def image_url(self) -> str:
        """Return the badge image URL for trailing-whitespace-fixer."""
        return f"https://img.shields.io/badge/whitespace-{self.shield_name()}-orange"

    def link_url(self) -> str:
        """Return the URL of the pre-commit-hooks project page."""
        return "https://github.com/pre-commit/pre-commit-hooks"

    def name(self) -> str:
        """Return `"trailing-whitespace-fixer"`, this tool's CLI command name."""
        return "trailing-whitespace-fixer"

    def dev_dependencies(self) -> tuple[str, ...]:
        """Return the package providing `trailing-whitespace-fixer`."""
        return ("pre-commit-hooks",)

    def types(self) -> list[str]:
        """Return `["text"]`, matching every text file this tool can strip.

        Same broad scope as `SpellChecker`/`SecretsChecker`: trailing
        whitespace is a property of text in general, not of any single
        language, so it isn't restricted to a single file type.
        """
        return ["text"]

    def format_args(self, *args: str) -> Args:
        """Construct trailing-whitespace-fixer arguments.

        Unlike `pretty-format-json`, this tool has no separate autofix
        flag: it always rewrites a file's trailing whitespace in place and
        reports via its exit code whether anything changed.

        Args:
            *args: Additional arguments forwarded to
                `trailing-whitespace-fixer`, typically the file paths to fix.

        Returns:
            Args for `trailing-whitespace-fixer`.
        """
        return self.args(*args)
