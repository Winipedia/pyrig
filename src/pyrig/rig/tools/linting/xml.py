"""Wrapper around the check-xml XML syntax linter tool."""

from typing import Any, override

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.hooks import CheckHookTool
from pyrig.rig.tools.base.tool import Group
from pyrig.rig.tools.security.secrets import SecretsChecker
from pyrig.rig.tools.version_control.hooks.manager import VersionControlHookManager


class XMLLinter(CheckHookTool):
    """Type-safe wrapper for prek's read-only XML syntax checker."""

    @override
    def check_args(self, *args: str) -> Args:
        """Construct check-xml arguments.

        Args:
            *args: File paths forwarded to `check-xml`.

        Returns:
            Args for `check-xml`.
        """
        return self.args(*args)

    @override
    def check_hook(self) -> dict[str, Any]:
        """Return hook metadata for checking XML alongside read-only checks."""
        return VersionControlHookManager.I.builtin_hook(
            self.check_xml,
            priority=VersionControlHookManager.I.hook_priority(
                SecretsChecker.I.check_hook(),
            ),
        )

    @override
    def dev_dependencies(self) -> tuple[str, ...]:
        """Return no package dependency; prek provides this built-in hook."""
        return ()

    @override
    def group(self) -> str:
        """Return `Group.CODE_QUALITY`, the badge group this tool belongs to."""
        return Group.CODE_QUALITY

    @override
    def image_url(self) -> str:
        """Return the badge image URL for check-xml."""
        return f"https://img.shields.io/badge/XML-{self.shield_name()}-blue"

    @override
    def link_url(self) -> str:
        """Return the documentation URL for this prek built-in hook."""
        return f"https://prek.j178.dev/reference/built-in-hooks/#{self.name()}"

    @override
    def name(self) -> str:
        """Return `'check-xml'`, the executable name for this tool's CLI command."""
        return "check-xml"

    def check_xml(self) -> Args:
        """Return arguments for the built-in hook."""
        return Args()
