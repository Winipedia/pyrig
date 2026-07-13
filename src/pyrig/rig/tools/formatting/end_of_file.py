"""Wrapper around the end-of-file-fixer tool."""

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.file import FileTool
from pyrig.rig.tools.base.tool import Group


class EndOfFileFormatter(FileTool):
    """Type-safe wrapper for the pre-commit-hooks end-of-file fixer."""

    def group(self) -> str:
        """Return `Group.CODE_QUALITY`, the badge group this tool belongs to."""
        return Group.CODE_QUALITY

    def image_url(self) -> str:
        """Return the badge image URL for end-of-file-fixer."""
        return f"https://img.shields.io/badge/EOF-{self.shield_name()}-orange"

    def link_url(self) -> str:
        """Return the URL of the pre-commit-hooks project page."""
        return "https://github.com/pre-commit/pre-commit-hooks"

    def name(self) -> str:
        """Return `"end-of-file-fixer"`, this tool's CLI command name."""
        return "end-of-file-fixer"

    def dev_dependencies(self) -> tuple[str, ...]:
        """Return the package providing `end-of-file-fixer`."""
        return ("pre-commit-hooks",)

    def types(self) -> list[str]:
        """Return `["text"]`, matching every text file this tool can normalize.

        Same broad scope as `SpellChecker`/`SecretsChecker`: a trailing
        newline is a property of text in general, not of any single
        language, so it isn't restricted to a single file type.
        """
        return ["text"]

    def format_args(self, *args: str) -> Args:
        """Construct end-of-file-fixer arguments.

        Like `trailing-whitespace-fixer`, this tool has no separate
        autofix flag: it always rewrites a file to end with exactly one
        trailing newline and reports via its exit code whether anything
        changed.

        Args:
            *args: Additional arguments forwarded to `end-of-file-fixer`,
                typically the file paths to fix.

        Returns:
            Args for `end-of-file-fixer`.
        """
        return self.args(*args)
