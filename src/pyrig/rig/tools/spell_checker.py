"""Spell checker tool wrapper.

Wraps SpellChecker commands and information.
"""

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.tool import Group, Tool


class SpellChecker(Tool):
    """Type-safe wrapper for the typos spell checker.

    Constructs typos command-line arguments for detecting and fixing spelling
    mistakes in source code, comments, and documentation.
    """

    def name(self) -> str:
        """Get the tool command name.

        Returns:
            'typos'
        """
        return "typos"

    def group(self) -> str:
        """Return the badge group this tool belongs to.

        Returns:
            ``Group.CODE_QUALITY``
        """
        return Group.CODE_QUALITY

    def image_url(self) -> str:
        """Return the badge image URL for typos.

        Returns:
            The URL of the badge image as a string.
        """
        return "https://img.shields.io/badge/spell--check-typos-blue"

    def link_url(self) -> str:
        """Return the project link URL for typos.

        Returns:
            The URL of the typos project page as a string.
        """
        return "https://github.com/crate-ci/typos"

    def check_fix_args(self, *args: str) -> Args:
        """Construct typos arguments with auto-fix enabled.

        Args:
            *args: Additional arguments forwarded to typos.

        Returns:
            Args for ``typos --write-changes [args]``.
        """
        return self.check_args("--write-changes", *args)

    def check_args(self, *args: str) -> Args:
        """Construct typos check arguments.

        Args:
            *args: Additional arguments forwarded to typos.

        Returns:
            Args for ``typos [args]``.
        """
        return self.args(*args)
