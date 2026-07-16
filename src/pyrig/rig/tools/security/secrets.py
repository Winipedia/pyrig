"""Secrets scanner command construction and badge metadata."""

from typing import Any

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.tool import Group, Tool
from pyrig.rig.tools.typing.checker import TypeChecker
from pyrig.rig.tools.version_control.hooks.manager import VersionControlHookManager


class SecretsChecker(Tool):
    """Wrapper for the `detect-secrets` secrets scanner.

    Constructs `detect-secrets-hook` command-line arguments for scanning the
    project's source code for accidentally committed credentials and other
    secrets.
    """

    def group(self) -> str:
        """Return `Group.CODE_QUALITY`."""
        return Group.CODE_QUALITY

    def image_url(self) -> str:
        """Return the Shields.io badge URL advertising `detect-secrets`."""
        return f"https://img.shields.io/badge/secrets-{self.shield_name()}-blue"

    def link_url(self) -> str:
        """Return the URL of the `detect-secrets` project page."""
        return "https://github.com/Yelp/detect-secrets"

    def name(self) -> str:
        """Return `'detect-secrets'`."""
        return "detect-secrets"

    def check_args(self, *args: str) -> Args:
        """Construct `detect-secrets-hook` arguments for scanning for secrets.

        Args:
            *args: Additional arguments forwarded to `detect-secrets-hook`.

        Returns:
            Args for `detect-secrets-hook [args]`.
        """
        return Args("detect-secrets-hook", *args)

    def version_control_hooks(self) -> tuple[dict[str, Any], ...]:
        """Return the secrets scanning hook.

        Returns:
            `check_hook`, wrapped in a single-element tuple.
        """
        return (self.check_hook(),)

    def check_hook(self) -> dict[str, Any]:
        """Return the hook metadata for scanning for committed secrets.

        Ties its priority to `TypeChecker.check_hook` so it runs
        alongside the rest of the checks tier rather than after it.

        Returns:
            Hook metadata dict for `detect-secrets-hook`.
        """
        return VersionControlHookManager.I.hook(
            self.check_secrets,
            priority=VersionControlHookManager.I.hook_priority(
                TypeChecker.I.check_hook(),
            ),
            types=["text"],
        )

    def check_secrets(self) -> Args:
        """Return the `Args` this hook's entry runs.

        Returns:
            Args for `detect-secrets-hook`.
        """
        return self.check_args()
