"""CI/CD linter tool wrapper."""

import re
from typing import Any

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.hooks import CheckHookTool
from pyrig.rig.tools.base.tool import Group
from pyrig.rig.tools.linting.shell import ShellLinter
from pyrig.rig.tools.packages.manager import PackageManager
from pyrig.rig.tools.typing.checker import TypeChecker
from pyrig.rig.tools.version_control.hooks.manager import VersionControlHookManager
from pyrig.rig.tools.version_control.remote.controller import RemoteVersionController


class CICDLinter(CheckHookTool):
    """Wrapper class for the CI/CD linter tool.

    This tool is used to lint CI/CD configuration files.
    It implements actionlint and wraps around it.
    """

    def group(self) -> str:
        """Return the group this tool belongs to."""
        return Group.CODE_QUALITY

    def image_url(self) -> str:
        """Return the URL of the shield image."""
        return f"https://img.shields.io/badge/CI/CD-{self.shield_name()}-blue"

    def link_url(self) -> str:
        """Return the URL of the tool's homepage or repository."""
        return "https://github.com/rhysd/actionlint"

    def name(self) -> str:
        """Return the name of the tool."""
        return "actionlint"

    def check_args(self, *args: str) -> Args:
        """Return the arguments for the CI/CD linter."""
        return self.args(*args)

    def check_hook(self) -> dict[str, Any]:
        """Return the configuration for the CI/CD linter hook."""
        shell_linter_hook = ShellLinter.I.check_hook()
        shell_linter_entry: str = shell_linter_hook["entry"]
        shell_linter_args: list[str] = shell_linter_hook["args"]
        return VersionControlHookManager.I.hook(
            self.lint_ci_cd,
            priority=VersionControlHookManager.I.hook_priority(
                TypeChecker.I.check_hook(),
            ),
            types=["yaml"],
            files=self.ci_cd_files_pattern(),
            args=Args(
                r'--ignore=reusable workflow call "\$/.*" at "uses" is not following the format',  # noqa: E501
                "--pyflakes=pyflakes",
                f"--shellcheck={shell_linter_entry} {Args(*shell_linter_args)}",
            ),
        )

    def dev_dependencies(self) -> tuple[str, ...]:
        """Return the development dependencies required for the CI/CD linter."""
        return ("actionlint-py", "pyflakes", "shellcheck-py")

    def lint_ci_cd(self) -> Args:
        """Return the args for running the CI/CD linter in the hook."""
        return PackageManager.I.run_args(*self.check_args())

    def ci_cd_files_pattern(self) -> str:
        """Return the regex to filter for files the tool can check."""
        return rf"^{re.escape(RemoteVersionController.I.ci_cd_dir().as_posix())}/"
