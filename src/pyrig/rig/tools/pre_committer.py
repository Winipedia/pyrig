"""Pre-commit tool wrapper.

Wraps PreCommitter commands and information.
"""

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.tool import Tool, ToolGroup


class PreCommitter(Tool):
    """Wrapper for the prek pre-commit hook manager.

    Builds Args objects for the two primary prek operations: installing
    hooks into the local git repository and running hooks against files.

    Pre-commit hooks enforce code quality by running configured linters,
    formatters, and static checks before each commit is accepted.

    Example:
        Install hooks once during project setup:

        >>> PreCommitter.I.install_args().run()

        Run all hooks against the full project (e.g., in CI):

        >>> PreCommitter.I.run_all_files_args().run()
    """

    def name(self) -> str:
        """Return the prek command name.

        Returns:
            The string 'prek'.
        """
        return "prek"

    def group(self) -> str:
        """Return the tool group used for badge grouping.

        Returns:
            ToolGroup.CODE_QUALITY.
        """
        return ToolGroup.CODE_QUALITY

    def badge_urls(self) -> tuple[str, str]:
        """Return the prek badge image URL and project page URL.

        Returns:
            A tuple of (badge_image_url, project_page_url).
        """
        return (
            "https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/j178/prek/master/docs/assets/badge-v0.json",
            "https://github.com/j178/prek",
        )

    def install_args(self, *args: str) -> Args:
        """Construct arguments to install prek hooks into the local git repository.

        Runs ``prek install``, which writes hook scripts into ``.git/hooks/`` so
        that configured checks run automatically on each commit attempt.

        Args:
            *args: Additional arguments forwarded to ``prek install``.

        Returns:
            Args for 'prek install [args]'.
        """
        return self.args("install", *args)

    def run_all_files_args(self, *args: str) -> Args:
        """Construct arguments to run all prek hooks against every file in the project.

        Passes ``--all-files`` to ``prek run`` so hooks apply to the entire
        project rather than only staged files. Typically used in CI to
        validate all files regardless of staging state.

        Args:
            *args: Additional arguments forwarded to ``prek run``.

        Returns:
            Args for 'prek run --all-files [args]'.
        """
        return self.run_args("--all-files", *args)

    def run_args(self, *args: str) -> Args:
        """Construct base arguments to run prek hooks.

        By default, prek checks only staged files. Use ``run_all_files_args``
        to run hooks against the full project instead.

        Args:
            *args: Additional arguments forwarded to ``prek run``.

        Returns:
            Args for 'prek run [args]'.
        """
        return self.args("run", *args)
