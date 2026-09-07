"""CI/CD security checker tool wrapper."""

import re
from typing import Any

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.hooks import CheckHookTool
from pyrig.rig.tools.base.tool import Group
from pyrig.rig.tools.packages.manager import PackageManager
from pyrig.rig.tools.typing.checker import TypeChecker
from pyrig.rig.tools.version_control.hooks.manager import VersionControlHookManager
from pyrig.rig.tools.version_control.remote.controller import RemoteVersionController


class CICDSecurityChecker(CheckHookTool):
    """Wrapper class for the CI/CD security checker tool.

    This tool is used to check the security of CI/CD configuration files.
    It implements zizmor and wraps around it.
    """

    def group(self) -> str:
        """Return the group this tool belongs to."""
        return Group.CODE_QUALITY

    def image_url(self) -> str:
        """Return the URL of the shield image."""
        return (
            f"https://img.shields.io/badge/CI/CD--security-{self.shield_name()}-yellow"
        )

    def link_url(self) -> str:
        """Return the URL of the tool's homepage or repository."""
        return "https://github.com/zizmorcore/zizmor"

    def name(self) -> str:
        """Return the name of the tool."""
        return "zizmor"

    def check_args(self, *args: str) -> Args:
        """Return the arguments for the CI/CD security checker."""
        return self.args(*args)

    def check_hook(self) -> dict[str, Any]:
        """Return the configuration for the CI/CD security checker hook."""
        return VersionControlHookManager.I.hook(
            self.check_ci_cd,
            priority=VersionControlHookManager.I.hook_priority(
                TypeChecker.I.check_hook(),
            ),
            types=["yaml"],
            files=self.ci_cd_files_pattern(),
            args=Args("--fix", "--persona=auditor", "--strict-collection"),
        )

    def check_ci_cd(self) -> Args:
        """Return the args for running the CI/CD security checker in the hook."""
        return PackageManager.I.run_args(*self.check_args())

    def ci_cd_files_pattern(self) -> str:
        """Return the regex to filter for files the tool can check."""
        ci_cd_dir = RemoteVersionController.I.ci_cd_dir().as_posix()
        dep_bot_config = (
            RemoteVersionController.I.dependency_bot_path().with_suffix("").as_posix()
            + "."
        )
        action_file = (
            RemoteVersionController.I.action_path().with_suffix("").as_posix() + "."
        )
        patterns = (
            rf"^{re.escape(ci_cd_dir)}/",
            rf"^{re.escape(dep_bot_config)}",
            rf"/{re.escape(action_file)}",
        )
        return "|".join(patterns)
