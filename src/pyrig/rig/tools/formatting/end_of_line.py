"""Wrapper around the mixed-line-ending tool."""

from typing import Any

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.hooks import FormatHookTool
from pyrig.rig.tools.base.tool import Group
from pyrig.rig.tools.language.spelling import SpellChecker
from pyrig.rig.tools.packages.manager import PackageManager
from pyrig.rig.tools.version_control.hooks.manager import VersionControlHookManager


class EndOfLineFormatter(FormatHookTool):
    """Type-safe wrapper for the pre-commit-hooks mixed line ending fixer."""

    def group(self) -> str:
        """Return `Group.CODE_QUALITY`, the badge group this tool belongs to."""
        return Group.CODE_QUALITY

    def image_url(self) -> str:
        """Return the badge image URL for mixed-line-ending."""
        return f"https://img.shields.io/badge/EOL-{self.shield_name()}-orange"

    def link_url(self) -> str:
        """Return the URL of the pre-commit-hooks project page."""
        return "https://github.com/pre-commit/pre-commit-hooks"

    def name(self) -> str:
        """Return `"mixed-line-ending"`, this tool's CLI command name."""
        return "mixed-line-ending"

    def dev_dependencies(self) -> tuple[str, ...]:
        """Return the package providing `mixed-line-ending`."""
        return ("pre-commit-hooks",)

    def format_args(self, *args: str) -> Args:
        """Construct mixed-line-ending arguments.

        Unlike `trailing-whitespace-fixer`, this tool takes a `--fix` flag
        rather than always applying one fixed behavior.

        Args:
            *args: Additional arguments forwarded to `mixed-line-ending`,
                typically the file paths to fix.

        Returns:
            Args for `mixed-line-ending`.
        """
        return self.args(*args)

    def format_hook(self) -> dict[str, Any]:
        """Return the hook metadata for normalizing mixed line endings.

        Runs right after spelling is fixed and before the other formatting
        fixers, so `trailing-whitespace-fixer` and `end-of-file-fixer`
        always operate on a file with one consistent line ending rather
        than a mix of LF and CRLF. Forces `--fix=lf` rather than this
        tool's own `auto` (majority-wins) default, matching the LF policy
        `.gitattributes` already enforces.

        Returns:
            Hook metadata dict for `mixed-line-ending --fix=lf`.
        """
        return VersionControlHookManager.I.hook(
            self.fix_mixed_line_ending,
            priority=VersionControlHookManager.I.increase_priority(
                SpellChecker.I.check_hook(),
            ),
            types=["text"],
            args=["--fix=lf"],
        )

    def fix_mixed_line_ending(self) -> Args:
        """Return the `Args` this hook's entry runs.

        Returns:
            Args for `uv run mixed-line-ending --fix=lf`.
        """
        return PackageManager.I.run_args(*self.format_args())
