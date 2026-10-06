"""Wrapper around the ryl YAML linter tool."""

from typing import Any

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

        Args:
            *args: Additional arguments forwarded to `ryl check`, typically
                the file paths to check.

        Returns:
            Args for `ryl check`.
        """
        return self.args("check", *args)

    def check_hook(self) -> dict[str, Any]:
        """Return the hook metadata for linting and auto-fixing YAML files.

        Returns:
            Hook metadata dict for `ryl check --fix --strict`.
        """
        return VersionControlHookManager.I.local_hook(
            self.lint_yaml,
            priority=VersionControlHookManager.I.deprioritize(
                SecretsChecker.I.check_hook(),
            ),
            types=["yaml"],
            args=Args(
                "--fix",
                "--strict",
            ),
        )

    def lint_yaml(self) -> Args:
        """Return the `Args` this hook's entry runs.

        Returns:
            Args for `uv run ryl check --fix --strict`.
        """
        return PackageManager.I.run_args(*self.check_args())

    def disable_line_line_length(self) -> str:
        """Return a comment string to disable the `line-length` rule for this line."""
        return self.disable_line("line-length")

    def disable_line(self, rule: str) -> str:
        """Return a comment string to disable a specific rule for this line.

        Args:
            rule: Name of the ryl rule to disable (e.g. `"line-length"`).

        Returns:
            The `disable-line` directive comment for `rule`.
        """
        return self.directive(f"disable-line rule:{rule}")

    def directive(self, directive: str) -> str:
        """Return an inline directive comment for this tool.

        Args:
            directive: Directive text (e.g. `"disable-line rule:colons"`).

        Returns:
            The comment `# ryl <directive>`.
        """
        return f"# {self.name()} {directive}"
