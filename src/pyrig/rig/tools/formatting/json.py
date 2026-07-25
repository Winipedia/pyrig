"""Wrapper around the pretty-format-json JSON formatter tool."""

from typing import Any

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.hooks import FormatHookTool
from pyrig.rig.tools.base.tool import Group
from pyrig.rig.tools.formatting.end_of_file import EndOfFileFormatter
from pyrig.rig.tools.packages.manager import PackageManager
from pyrig.rig.tools.version_control.hooks.manager import VersionControlHookManager


class JSONFormatter(FormatHookTool):
    """Type-safe wrapper for the pretty-format-json JSON formatter."""

    def group(self) -> str:
        """Return `Group.CODE_QUALITY`, the badge group this tool belongs to."""
        return Group.CODE_QUALITY

    def image_url(self) -> str:
        """Return the badge image URL for pretty-format-json."""
        return f"https://img.shields.io/badge/JSON-{self.shield_name()}-orange"

    def link_url(self) -> str:
        """Return the URL of the pre-commit-hooks project page."""
        return "https://github.com/pre-commit/pre-commit-hooks"

    def name(self) -> str:
        """Return `"pretty-format-json"`, this tool's CLI command name."""
        return "pretty-format-json"

    def dev_dependencies(self) -> tuple[str, ...]:
        """Return the package providing `pretty-format-json`."""
        return ("pre-commit-hooks",)

    def format_args(self, *args: str) -> Args:
        """Construct pretty-format-json arguments.

        Unlike `trailing-whitespace-fixer`, `pretty-format-json` needs an
        explicit `--autofix` flag to write changes back instead of only
        reporting a diff.

        Args:
            *args: Additional arguments forwarded to `pretty-format-json`,
                typically the file paths to format.

        Returns:
            Args for `pretty-format-json`.
        """
        return self.args(*args)

    def format_hook(self) -> dict[str, Any]:
        """Return the hook metadata for formatting JSON files.

        Runs after the sequential text-fixing chain, alongside the other
        file-type-specific fixers. Passes `--autofix` so changes are
        written back rather than only reported as a diff. Disables
        ASCII-escaping and key sorting, matching `JSONConfigFile`'s own
        `json.dump` call (`ensure_ascii=False`) so this formatter never
        fights the config writer over a file it just generated; key
        order is left untouched for the same reason, since it's
        meaningful (e.g. `name` before `version`), not incidental. Indent
        width isn't passed explicitly: `pretty-format-json`'s own default
        is already 2, matching `JSONConfigFile`.

        Returns:
            Hook metadata dict for `pretty-format-json` with
            `--autofix --no-ensure-ascii --no-sort-keys`.
        """
        return VersionControlHookManager.I.hook(
            self.format_json,
            priority=VersionControlHookManager.I.increase_priority(
                EndOfFileFormatter.I.format_hook(),
            ),
            types=["json"],
            args=["--autofix", "--no-ensure-ascii", "--no-sort-keys"],
        )

    def format_json(self) -> Args:
        """Return the `Args` this hook's entry runs.

        Returns:
            Args for `uv run pretty-format-json`.
        """
        return PackageManager.I.run_args(*self.format_args())
