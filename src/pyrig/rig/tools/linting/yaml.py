"""Wrapper around the ryl YAML linter tool."""

from typing import Any, override

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.hooks import CheckHookTool
from pyrig.rig.tools.base.tool import Group
from pyrig.rig.tools.packages.manager import PackageManager
from pyrig.rig.tools.security.secrets import SecretsChecker
from pyrig.rig.tools.version_control.hooks.manager import VersionControlHookManager


class YAMLLinter(CheckHookTool):
    """Type-safe wrapper for the ryl YAML linter.

    Constructs ryl command-line arguments for linting and auto-fixing YAML
    files, and builds ryl inline directive comments.
    """

    @override
    def check_hook(self) -> dict[str, Any]:
        """Return the hook metadata for linting and auto-fixing YAML files.

        Returns:
            Hook metadata dict for `ryl check --fix`.
        """
        return VersionControlHookManager.I.local_hook(
            self.lint_yaml,
            priority=VersionControlHookManager.I.deprioritize(
                SecretsChecker.I.check_hook(),
            ),
            types=["yaml"],
            args=Args("--fix"),
        )

    @override
    def group(self) -> str:
        """Return `Group.CODE_QUALITY`, the badge group this tool belongs to."""
        return Group.CODE_QUALITY

    @override
    def image_url(self) -> str:
        """Return the badge image URL for ryl."""
        return f"https://img.shields.io/badge/YAML-{self.shield_name()}-red"

    @override
    def link_url(self) -> str:
        """Return the URL of the ryl project page."""
        return "https://github.com/owenlamont/ryl"

    @override
    def version_control_ignore_patterns(self) -> tuple[str, ...]:
        """Return ryl's cache directory as a path to ignore."""
        return (*super().version_control_ignore_patterns(), ".ryl_cache/")

    @override
    def check_args(self, *args: str) -> Args:
        """Construct ryl lint arguments.

        Args:
            *args: Additional arguments forwarded to `ryl check`, typically
                the file paths to check.

        Returns:
            Args for `ryl check`.
        """
        return self.args("check", *args)

    @override
    def name(self) -> str:
        """Return `'ryl'`, the executable name for this tool's CLI command."""
        return "ryl"

    def disable_line_length(self, *, line: bool = True, comment: bool = False) -> str:
        """Return directive text to disable the `line-length` rule.

        Args:
            line: Whether to disable the rule only for the current line.
            comment: Whether to prefix the directive with `# `.

        Returns:
            Directive text, optionally prefixed as a YAML comment.
        """
        return self.disable("line-length", line=line, comment=comment)

    def disable(self, rule: str, *, line: bool = True, comment: bool = False) -> str:
        """Return directive text to disable a rule for a line or file.

        Args:
            rule: Name of the ryl rule to disable (e.g. `"line-length"`).
            line: Whether to disable the rule only for the current line.
            comment: Whether to prefix the directive with `# `.

        Returns:
            Directive text, optionally prefixed as a YAML comment.
        """
        scope = f"disable{'-line' if line else ''}"
        return self.directive(f"{scope} rule:{rule}", comment=comment)

    def lint_yaml(self) -> Args:
        """Return the `Args` this hook's entry runs.

        Returns:
            Args for `uv run ryl check`.
        """
        return PackageManager.I.run_args(*self.check_args())

    def directive(self, directive: str, *, comment: bool = False) -> str:
        """Return directive text, optionally prefixed as a YAML comment.

        Args:
            directive: Directive text (e.g. `"disable-line rule:colons"`).
            comment: Whether to prefix the text with `# `.

        Returns:
            The directive text, optionally prefixed with `# `.
        """
        prefix = "# " if comment else ""
        return f"{prefix}{self.name()} {directive}"
