"""Wrapper around the ShellCheck shell script linter tool."""

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.file import FileTool
from pyrig.rig.tools.base.tool import Group


class ShellLinter(FileTool):
    """Type-safe wrapper for the ShellCheck shell script linter."""

    def group(self) -> str:
        """Return `Group.CODE_QUALITY`, the badge group this tool belongs to."""
        return Group.CODE_QUALITY

    def image_url(self) -> str:
        """Return the badge image URL for ShellCheck."""
        return "https://img.shields.io/badge/shell-shellcheck-blue"

    def link_url(self) -> str:
        """Return the URL of the ShellCheck project page."""
        return "https://github.com/koalaman/shellcheck"

    def name(self) -> str:
        """Return `'shellcheck'`, the executable name for this tool's CLI command."""
        return "shellcheck"

    def dev_dependencies(self) -> tuple[str, ...]:
        """Return `('shellcheck-py',)`, the PyPI package providing `shellcheck`."""
        return ("shellcheck-py",)

    def types(self) -> list[str]:
        """Return the list of file types that `shellcheck` can lint."""
        return ["shell"]

    def check_args(self, *args: str) -> Args:
        """Construct ShellCheck check arguments at maximum strictness.

        Enables every optional check on top of the default set, surfaces
        every severity level down to style, and pins the dialect to `bash`
        rather than relying on shebang detection, since every script this
        project generates (`ShellConfigFile`) commits to `bash` explicitly.

        Args:
            *args: Additional arguments forwarded to `shellcheck`, typically
                the file paths to check.

        Returns:
            Args for `shellcheck --severity=style --enable=all --shell=bash`.
        """
        return self.args(
            "--severity=style",
            "--enable=all",
            "--shell=bash",
            *args,
        )
