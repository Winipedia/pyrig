"""Configuration manager for the API reference documentation page."""

from pathlib import Path

from pyrig.rig.configs.base.markdown import MarkdownConfigFile
from pyrig.rig.tools.docs_builder import DocsBuilder
from pyrig.rig.tools.package_manager import PackageManager


class APIDocsConfigFile(MarkdownConfigFile):
    """Configuration manager for the MkDocs API reference page (`docs/api.md`).

    Generates a Markdown file that uses the mkdocstrings `:::` directive to
    render full API documentation from the project's Python docstrings. The
    page contains an `# API Reference` heading and a single `:::` directive
    targeting the project's package, which mkdocstrings expands recursively
    into all public members, their signatures, docstrings, and source links.

    Example:
        Generated `docs/api.md` content for a package named `project_package_name`:
        ```
        # API Reference

        ::: project_package_name
        ```
    """

    def lines(self) -> list[str]:
        """Build the API reference page content.

        Returns:
            Lines comprising the `# API Reference` heading and the
            mkdocstrings `:::` directive for the project's package.
        """
        return ["# API Reference", "", f"::: {PackageManager.I.package_name()}", ""]

    def parent_path(self) -> Path:
        """Return the MkDocs documentation source directory."""
        return DocsBuilder.I.docs_dir()

    def stem(self) -> str:
        """Return the filename stem `"api"`."""
        return "api"
