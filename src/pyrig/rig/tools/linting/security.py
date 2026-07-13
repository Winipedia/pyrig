"""Security scanner command construction and badge metadata."""

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.file import FileTool
from pyrig.rig.tools.base.tool import Group
from pyrig.rig.tools.linting.python import PythonLinter
from pyrig.rig.tools.package_manager import PackageManager


class SecurityLinter(FileTool):
    """Wrapper for the `bandit` security checker.

    Constructs `bandit` command-line arguments for scanning source code for
    common security vulnerabilities.
    """

    def group(self) -> str:
        """Return `Group.CODE_QUALITY`."""
        return Group.CODE_QUALITY

    def image_url(self) -> str:
        """Return the badge image URL for `bandit`."""
        return "https://img.shields.io/badge/security-bandit-yellow.svg"

    def link_url(self) -> str:
        """Return the URL of the `bandit` project page."""
        return "https://github.com/PyCQA/bandit"

    def name(self) -> str:
        """Return `'bandit'`."""
        return "bandit"

    def extension(self) -> str:
        """Return the Python source file extension.

        Delegates to `PythonLinter` rather than repeating the same value:
        whether a file *is* Python is a language-identity question, and
        `PythonLinter` (ruff) is the higher-authority definition of what
        counts as Python for this project's tooling. `regex()` is
        overridden separately, since it also has to scope matches to the
        package root, not just the extension.
        """
        return PythonLinter.I.extension()

    def regex(self) -> str:
        """Return a regex matching Python files under the package root.

        Scoped to the package root rather than every `.py` file: bandit
        has no notion of test code, so it flags things like assert
        statements (`B101`) that `pyproject.toml` already tells Ruff to
        ignore under `tests/`.
        """
        return rf"^{PackageManager.I.package_root().as_posix()}/.*\.pyi?$"

    def check_args(self, *args: str) -> Args:
        """Construct `bandit` arguments.

        No target path is baked in: bandit silently skips a file it can't
        parse as Python rather than erroring, but still logs a warning and
        wastes a whole-tree walk doing so, so callers are expected to
        supply the specific files to check.

        Args:
            *args: Additional `bandit` arguments, typically the file paths
                to check.

        Returns:
            Args for `bandit [args]`.
        """
        return self.args(*args)
