"""MkDocs command construction and GitHub Pages documentation metadata."""

from pathlib import Path

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.tool import Group, Tool
from pyrig.rig.tools.package_manager import PackageManager
from pyrig.rig.tools.version_control.version_controller import VersionController


class DocsBuilder(Tool):
    """MkDocs command wrapper with GitHub Pages URL metadata."""

    def name(self) -> str:
        """Return `'mkdocs'`."""
        return "mkdocs"

    def group(self) -> str:
        """Return `Group.PROJECT_INFO`."""
        return Group.PROJECT_INFO

    def image_url(self) -> str:
        """Return the badge image URL."""
        return "https://img.shields.io/badge/MkDocs-Documentation-326CE5?logo=mkdocs&logoColor=white"

    def link_url(self) -> str:
        """Return the expected GitHub Pages URL for this project."""
        return self.documentation_url()

    def version_control_ignore_paths(self) -> tuple[str, ...]:
        """Return the built site output directory, `'/site'`."""
        return ("/site",)

    def dev_dependencies(self) -> tuple[str, ...]:
        """Return `mkdocs` plus the Material, Mermaid, and mkdocstrings packages."""
        return (
            *super().dev_dependencies(),
            "mkdocs-material",
            "mkdocs-mermaid2-plugin",
            "mkdocstrings[python]",
        )

    def docs_dir(self) -> Path:
        """Return the documentation source directory, `Path('docs')`."""
        return Path("docs")

    def build_args(self, *args: str) -> Args:
        """Construct arguments for the `mkdocs build` command.

        Args:
            *args: Additional arguments appended after `build`.

        Returns:
            Args for `mkdocs build <args...>`.
        """
        return self.args("build", *args)

    def documentation_url(self) -> str:
        """Construct the expected GitHub Pages URL for this project.

        The owner comes from `VersionController` and the repository name
        from `PackageManager`. Does not verify that the remote is configured
        or that GitHub Pages is enabled.

        Returns:
            URL in the form `https://{owner}.github.io/{repo}`.
        """
        owner, repo = (
            VersionController.I.repo_owner(),
            PackageManager.I.project_name(),
        )
        return f"https://{owner}.github.io/{repo}"
