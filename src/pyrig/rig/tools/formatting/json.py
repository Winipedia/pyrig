"""Wrapper around the pretty-format-json JSON formatter tool."""

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.file import FileTool
from pyrig.rig.tools.base.tool import Group
from pyrig.rig.tools.linting.json import JSONLinter


class JSONFormatter(FileTool):
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

    def types(self) -> list[str]:
        """Return the list of file types that `pretty-format-json` can format."""
        return JSONLinter.I.types()

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
        return self.args(
            "--autofix",
            "--no-ensure-ascii",
            "--no-sort-keys",
            *args,
        )
