"""Static type checker command construction and badge metadata."""

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.file import FileTool
from pyrig.rig.tools.base.tool import Group
from pyrig.rig.tools.linting.python import PythonLinter


class TypeChecker(FileTool):
    """Type-safe wrapper for the `ty` static type checker."""

    def group(self) -> str:
        """Return `Group.CODE_QUALITY`."""
        return Group.CODE_QUALITY

    def image_url(self) -> str:
        """Return the badge image URL for `ty`."""
        return "https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ty/main/assets/badge/v0.json"

    def link_url(self) -> str:
        """Return the URL of the `ty` project page."""
        return "https://github.com/astral-sh/ty"

    def name(self) -> str:
        """Return `'ty'`."""
        return "ty"

    def types(self) -> list[str]:
        """Return the file types `ty` type-checks.

        Delegates to `PythonLinter` rather than repeating the same value:
        `ty` type-checks the same Python source `PythonLinter` (ruff)
        lints, so `PythonLinter` is the higher-authority definition of
        what counts as Python for this project's tooling. Only used to
        gate whether this hook runs at all - `ty` always type-checks the
        whole project once triggered, since a change to one file can
        break usages in another file that this commit never touched.
        """
        return PythonLinter.I.types()

    def check_args(self, *args: str) -> Args:
        """Build the command for running `ty check`.

        Args:
            *args: Additional arguments appended after `check`.

        Returns:
            Args for `ty check [args]`.
        """
        return self.args("check", *args)
