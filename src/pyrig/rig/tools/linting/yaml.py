"""Wrapper around the ryl YAML linter tool."""

from typing import Any

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.tool import Group, Tool
from pyrig.rig.tools.formatting.end_of_file import EndOfFileFormatter
from pyrig.rig.tools.version_control.hooks.manager import VersionControlHookManager


class YAMLLinter(Tool):
    """Type-safe wrapper for the ryl YAML linter.

    Constructs ryl command-line arguments for linting and auto-fixing YAML
    files.
    """

    def group(self) -> str:
        """Return `Group.CODE_QUALITY`, the badge group this tool belongs to."""
        return Group.CODE_QUALITY

    def image_url(self) -> str:
        """Return the badge image URL for ryl."""
        return f"https://img.shields.io/badge/YAML-{self.shield_name()}-red"

    def link_url(self) -> str:
        """Return the URL of the ryl project page."""
        return "https://github.com/owenlamont/ryl"

    def name(self) -> str:
        """Return `'ryl'`, the executable name for this tool's CLI command."""
        return "ryl"

    def check_args(self, *args: str) -> Args:
        """Construct ryl lint arguments.

        No custom rule configuration or target path is baked in here; the
        hook's own `args=` supplies `--config-data`, and callers are
        otherwise expected to supply the specific files to check, since ryl
        errors on a file it doesn't recognize (e.g. a non-YAML file).

        Args:
            *args: Additional arguments forwarded to `ryl check`, typically
                the file paths to check.

        Returns:
            Args for `ryl check`.
        """
        return self.args("check", *args)

    def version_control_hooks(self) -> tuple[dict[str, Any], ...]:
        """Return the YAML linting hook.

        Returns:
            `check_hook`, wrapped in a single-element tuple.
        """
        return (self.check_hook(),)

    def check_hook(self) -> dict[str, Any]:
        """Return the hook metadata for linting and auto-fixing YAML files.

        Runs after the sequential text-fixing chain, alongside the other
        file-type-specific fixers.

        Returns:
            Hook metadata dict for `ryl check --fix`.
        """
        return VersionControlHookManager.I.hook(
            self.lint_yaml,
            priority=VersionControlHookManager.I.increase_priority(
                EndOfFileFormatter.I.format_hook(),
            ),
            types=["yaml"],
            args=[
                "--fix",
                "--config-data=extends: default",
            ],
        )

    def lint_yaml(self) -> Args:
        """Return the `Args` this hook's entry runs.

        Returns:
            Args for `ryl check`.
        """
        return self.check_args()
