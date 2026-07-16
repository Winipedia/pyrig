"""Configuration manager for the API reference documentation page."""

from pathlib import Path

from pyrig.rig.configs.base.markdown import MarkdownConfigFile
from pyrig.rig.tools.docs.builder import DocsBuilder
from pyrig.rig.tools.packages.manager import PackageManager


class APIDocsConfigFile(MarkdownConfigFile):
    """Configuration manager for the MkDocs API reference page (`docs/api.md`).

    Generates a Markdown file that uses the mkdocstrings `:::` directive to
    render full API documentation from the project's Python docstrings. The
    page contains an `# API` heading and a single `:::` directive targeting
    the project's package, which mkdocstrings expands recursively into all
    public members, their signatures, docstrings, and source links.
    """

    def content(self) -> str:
        """Build the API reference page content.

        Returns:
            The `# API` heading and the mkdocstrings `:::` directive for the
            project's package.
        """
        return f"""# API

::: {PackageManager.I.package_name()}
"""

    def parent_path(self) -> Path:
        """Return the MkDocs documentation source directory."""
        return DocsBuilder.I.docs_dir()

    def stem(self) -> str:
        """Return the filename stem `"api"`."""
        return "api"
