"""Wrapper around the name-tests-test tool."""

from typing import Any

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.hooks import CheckHookTool
from pyrig.rig.tools.base.tool import Group
from pyrig.rig.tools.testing.project import ProjectTester
from pyrig.rig.tools.typing.checker import TypeChecker
from pyrig.rig.tools.version_control.hooks.manager import VersionControlHookManager


class ModuleTestNamingChecker(CheckHookTool):
    """Type-safe wrapper for the pre-commit-hooks test file naming checker."""

    def group(self) -> str:
        """Return `Group.CODE_QUALITY`, the badge group this tool belongs to."""
        return Group.CODE_QUALITY

    def image_url(self) -> str:
        """Return the badge image URL for name-tests-test."""
        return f"https://img.shields.io/badge/test--naming-{self.shield_name()}-blue"

    def link_url(self) -> str:
        """Return the URL of the pre-commit-hooks project page."""
        return "https://github.com/pre-commit/pre-commit-hooks"

    def name(self) -> str:
        """Return `"name-tests-test"`, this tool's CLI command name."""
        return "name-tests-test"

    def dev_dependencies(self) -> tuple[str, ...]:
        """Return the package providing `name-tests-test`."""
        return ("pre-commit-hooks",)

    def check_args(self, *args: str) -> Args:
        """Construct name-tests-test arguments.

        Like `check-merge-conflict`, this tool has no autofix mode: a
        misnamed test file has no safe automatic rename, only a report.

        Args:
            *args: Additional arguments forwarded to `name-tests-test`,
                typically the file paths to check.

        Returns:
            Args for `name-tests-test`.
        """
        return self.args(*args)

    def check_hook(self) -> dict[str, Any]:
        """Return the hook metadata for checking test file naming conventions.

        Restricted to `ProjectTester.package_root()` via `files`, since
        `name-tests-test` has no path filter of its own and would otherwise
        also inspect ordinary source modules. Enforces the `test_*.py`
        pattern via `--pytest-test-first`, matching this project's own test
        naming convention. Ties its priority to `TypeChecker.check_hook`
        so it runs alongside the rest of the checks tier rather than after it.

        Returns:
            Hook metadata dict for `name-tests-test --pytest-test-first`.
        """
        return VersionControlHookManager.I.hook(
            self.check_test_naming,
            priority=VersionControlHookManager.I.hook_priority(
                TypeChecker.I.check_hook(),
            ),
            types=["python"],
            files=f"^{ProjectTester.I.package_root().as_posix()}/",
            args=["--pytest-test-first"],
        )

    def check_test_naming(self) -> Args:
        """Return the `Args` this hook's entry runs.

        Returns:
            Args for `name-tests-test`.
        """
        return self.check_args()
