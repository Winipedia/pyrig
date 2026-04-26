"""Configuration manager for the API reference documentation page."""

from pathlib import Path

from pyrig.rig.configs.base.markdown import MarkdownConfigFile
from pyrig.rig.tools.docs_builder import DocsBuilder
from pyrig.rig.tools.package_manager import PackageManager


class ApiConfigFile(MarkdownConfigFile):
    """Manages the ``docs/api.md`` API reference page.

    Generates a Markdown file that uses the mkdocstrings ``:::`` directive to
    render full API documentation from the project's Python docstrings. The
    page contains an ``# API Reference`` heading and a single ``:::`` directive
    targeting the root package name, which mkdocstrings expands recursively
    into all public members, their signatures, docstrings, and source links.

    Example:
        Generate or update ``docs/api.md``::

            ApiConfigFile.I.validate()

        Resulting file content::

            # API Reference

            ::: pyrig
    """

    def parent_path(self) -> Path:
        """Return the ``docs/`` directory as the parent path for ``api.md``.

        Returns:
            Path: The project's MkDocs documentation source directory.
        """
        return DocsBuilder.I.docs_dir()

    def stem(self) -> str:
        """Return the filename stem ``"api"``."""
        return "api"

    def lines(self) -> list[str]:
        """Build the ``api.md`` file content.

        Produces an ``# API Reference`` heading followed by a single
        mkdocstrings ``:::`` directive that targets the project's root
        package. mkdocstrings resolves this directive at build time and
        recursively renders all public members into the final HTML page.

        Returns:
            list[str]: Lines comprising the ``# API Reference`` heading and
                the ``:::`` directive for the project's root package name.
        """
        project_name = PackageManager.I.project_name()
        return ["# API Reference", "", f"::: {project_name}", ""]
