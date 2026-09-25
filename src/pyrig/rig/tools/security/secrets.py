"""Secrets scanner command construction and badge metadata."""

from typing import Any

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.hooks import CheckHookTool
from pyrig.rig.tools.base.tool import Group
from pyrig.rig.tools.formatting.end_of_file import EndOfFileFormatter
from pyrig.rig.tools.packages.manager import PackageManager
from pyrig.rig.tools.version_control.hooks.manager import VersionControlHookManager


class SecretsChecker(CheckHookTool):
    """Wrapper for the `detect-secrets` secrets scanner.

    Constructs `detect-secrets-hook` command-line arguments for scanning the
    project's files for accidentally committed credentials and other
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

    def check_hook(self) -> dict[str, Any]:
        """Return the hook metadata for scanning for committed secrets.

        Runs after the general text-fixing chain, before file-specific
        formatters modify the normalized contents.

        Returns:
            Hook metadata dict for `detect-secrets-hook`.
        """
        return VersionControlHookManager.I.local_hook(
            self.check_secrets,
            priority=VersionControlHookManager.I.deprioritize(
                EndOfFileFormatter.I.format_hook(),
            ),
            types=["text"],
        )

    def check_secrets(self) -> Args:
        """Return the `Args` this hook's entry runs.

        Returns:
            Args for `uv run detect-secrets-hook`.
        """
        return PackageManager.I.run_args(*self.check_args())
