"""Zensical command construction and GitHub Pages documentation metadata."""

from pathlib import Path

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.tool import Group, Tool
from pyrig.rig.tools.packages.manager import PackageManager
from pyrig.rig.tools.version_control.controller import VersionController


class DocsBuilder(Tool):
    """Zensical command wrapper with GitHub Pages URL metadata.

    Configured via Zensical's native `zensical.toml` format. Also exposes
    the project's documentation source and built-site output directories,
    since those follow conventions this tool defines.
    """

    def dev_dependencies(self) -> tuple[str, ...]:
        """Return `zensical` plus the `mkdocstrings` package."""
        return (
            *super().dev_dependencies(),
            "mkdocstrings[python]",
        )

    def group(self) -> str:
        """Return `Group.PROJECT_INFO`."""
        return Group.PROJECT_INFO

    def image_url(self) -> str:
        """Return the badge image URL."""
        return f"https://img.shields.io/badge/Documentation-{self.shield_name()}-326CE5"

    def link_url(self) -> str:
        """Return the expected GitHub Pages URL for this project."""
        return self.documentation_url()

    def name(self) -> str:
        """Return `'zensical'`."""
        return "zensical"

    def version_control_ignore_patterns(self) -> tuple[str, ...]:
        """Return patterns the tool produces and should be version-control-ignored."""
        return (f"/{self.site_dir().as_posix()}", ".cache")

    def build_args(self, *args: str) -> Args:
        """Construct arguments for the `zensical build` command.

        Args:
            *args: Additional arguments appended after `build`.

        Returns:
            Args for `zensical build <args...>`.
        """
        return self.args("build", *args)

    def docs_dir(self) -> Path:
        """Return the documentation source directory, `Path('docs')`."""
        return Path("docs")

    def documentation_url(self) -> str:
        """Construct this project's GitHub Pages URL.

        Returns:
            URL in the form `https://{owner}.github.io/{repo}`.
        """
        owner, repo = (
            VersionController.I.repo_owner(),
            PackageManager.I.project_name(),
        )
        return f"https://{owner}.github.io/{repo}"

    def site_dir(self) -> Path:
        """Return the built site output directory, `Path('site')`."""
        return Path("site")
