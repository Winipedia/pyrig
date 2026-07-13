"""Secrets scanner command construction and badge metadata."""

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.file import FileTool
from pyrig.rig.tools.base.tool import Group


class SecretsChecker(FileTool):
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

    def types(self) -> list[str]:
        """Return `['text']`, the file types `detect-secrets` can usefully scan.

        Confirmed by testing rather than assumed: a real secret embedded in
        genuinely binary content (undecodable as UTF-8, mixed with random
        noise) goes undetected regardless of extension, since
        `detect-secrets` requires the whole file to decode as text. So
        restricting to `text` costs no real coverage - those files were
        already unscannable - while letting a commit that touches no text
        files skip this hook entirely.
        """
        return ["text"]

    def check_args(self, *args: str) -> Args:
        """Construct `detect-secrets-hook` arguments for scanning for secrets.

        Args:
            *args: Additional arguments forwarded to `detect-secrets-hook`.

        Returns:
            Args for `detect-secrets-hook [args]`.
        """
        return Args("detect-secrets-hook", *args)
