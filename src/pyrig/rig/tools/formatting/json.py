"""Wrapper around the pretty-format-json JSON formatter tool."""

from typing import Any

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.tool import Group, Tool
from pyrig.rig.tools.formatting.end_of_file import EndOfFileFormatter
from pyrig.rig.tools.version_control.hook_manager import VersionControlHookManager


class JSONFormatter(Tool):
    """Type-safe wrapper for the pretty-format-json JSON formatter."""

    def group(self) -> str:
        """Return `Group.CODE_QUALITY`, the badge group this tool belongs to."""
        return Group.CODE_QUALITY

    def image_url(self) -> str:
        """Return the badge image URL for pretty-format-json."""
        return f"https://img.shields.io/badge/JSON-{self.shield_name()}-orange"

    def link_url(self) -> str:
        """Return the URL of the pretty-format-json project page."""
        return "https://github.com/pre-commit/pre-commit-hooks"

    def name(self) -> str:
        """Return `the executable name for this tool's CLI command."""
        return "pretty-format-json"

    def dev_dependencies(self) -> tuple[str, ...]:
        """Return the package providing `pretty-format-json`."""
        return ("pre-commit-hooks",)

    def format_args(self, *args: str) -> Args:
        """Construct pretty-format-json formatting arguments at maximum strictness.

        Disables ASCII-escaping and key sorting, matching `JSONConfigFile`'s
        own `json.dump` call (`ensure_ascii=False`) so this formatter never
        fights the config writer over a file it just generated. Key order
        is left untouched rather than sorted for the same reason: it's
        meaningful (e.g. `name` before `version`), not incidental. Indent
        width isn't passed explicitly: `pretty-format-json`'s own default is
        already 2, matching `JSONConfigFile`. Also writes changes back to
        each file rather than only reporting a diff.

        Args:
            *args: Additional arguments forwarded to `pretty-format-json`,
                typically the file paths to format.

        Returns:
            Args for `pretty-format-json --autofix --no-ensure-ascii --no-sort-keys`.
        """
        return self.args(*args)

    def version_control_hooks(self) -> tuple[dict[str, Any], ...]:
        """Return the JSON formatting hook.

        Returns:
            `format_json_hook`, wrapped in a single-element tuple.
        """
        return (self.format_json_hook(),)

    def format_json_hook(self) -> dict[str, Any]:
        """Return the hook metadata for formatting JSON files.

        Runs after the sequential text-fixing chain, alongside the other
        file-type-specific fixers.

        Returns:
            Hook metadata dict for `pretty-format-json`.
        """
        return VersionControlHookManager.I.hook(
            self.format_json,
            priority=VersionControlHookManager.I.increase_priority(
                EndOfFileFormatter.I.format_end_of_file_hook(),
            ),
            types=["json"],
            args=["--autofix", "--no-ensure-ascii", "--no-sort-keys"],
        )

    def format_json(self) -> Args:
        """Return the `Args` this hook's entry runs.

        Returns:
            Args for `pretty-format-json`.
        """
        return self.format_args()
