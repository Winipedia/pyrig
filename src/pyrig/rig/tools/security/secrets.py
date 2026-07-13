"""Secrets scanner command construction and badge metadata."""

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.tool import Group, Tool


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
        return "https://img.shields.io/badge/secrets-detect--secrets-blue"

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
