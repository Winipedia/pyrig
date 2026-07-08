"""Argument construction for the prek pre-commit hook manager CLI."""

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.tool import Group, Tool


class VersionControlHookManager(Tool):
    """Wrapper for the prek pre-commit hook manager.

    Builds `Args` for the two primary prek operations: installing hooks into
    the local git repository and running hooks against files.
    """

    def group(self) -> str:
        """Return the badge group this tool belongs to.

        Returns:
            `Group.CODE_QUALITY`.
        """
        return Group.CODE_QUALITY

    def image_url(self) -> str:
        """Return the badge image URL for prek.

        Returns:
            The URL of the badge image as a string.
        """
        return "https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/j178/prek/master/docs/assets/badge-v0.json"

    def link_url(self) -> str:
        """Return the link URL for prek.

        Returns:
            The URL of the prek project page as a string.
        """
        return "https://github.com/j178/prek"

    def name(self) -> str:
        """Return the tool's command name.

        Returns:
            `'prek'`.
        """
        return "prek"

    def install_args(self, *args: str) -> Args:
        """Build arguments for `prek install`.

        Args:
            *args: Additional arguments appended to the command.

        Returns:
            Args for `prek install [args]`.
        """
        return self.args("install", *args)

    def run_all_files_stage_pre_commit_args(self, *args: str) -> Args:
        """Build arguments to run pre-commit-stage hooks against every file.

        Args:
            *args: Additional arguments appended to the command.

        Returns:
            Args for `prek run --all-files --hook-stage pre-commit [args]`.
        """
        return self.run_all_files_stage_args(*args, stage="pre-commit")

    def run_all_files_stage_args(self, *args: str, stage: str) -> Args:
        """Build arguments to run hooks of a given stage against every file.

        Args:
            *args: Additional arguments appended to the command.
            stage: The hook stage to run (e.g. `"pre-commit"`).

        Returns:
            Args for `prek run --all-files --hook-stage <stage> [args]`.
        """
        return self.run_all_files_args("--hook-stage", stage, *args)

    def run_all_files_args(self, *args: str) -> Args:
        """Build arguments to run hooks against every file in the project.

        Args:
            *args: Additional arguments appended to the command.

        Returns:
            Args for `prek run --all-files [args]`.
        """
        return self.run_args("--all-files", *args)

    def run_args(self, *args: str) -> Args:
        """Build base arguments for `prek run`.

        Args:
            *args: Additional arguments appended to the command.

        Returns:
            Args for `prek run [args]`.
        """
        return self.args("run", *args)
