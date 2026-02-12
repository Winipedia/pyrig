"""Markdown badge file configuration management.

Provides BadgesMarkdownConfigFile for creating Markdown files with auto-generated
project badges from pyproject.toml and Git metadata.

Example:
    >>> from pathlib import Path
    >>> from pyrig.rig.configs.base.badges_md import BadgesMarkdownConfigFile
    >>>
    >>> class ReadmeFile(BadgesMarkdownConfigFile):
    ...     @classmethod
    ...     def parent_path(cls) -> Path:
    ...         return Path()
    ...
    ...     @classmethod
    ...     def filename(cls) -> str:
    ...         return "README"
    >>>
    >>> ReadmeFile()  # Creates README.md with badges
"""

import re

from pyrig.rig.configs.base.markdown import MarkdownConfigFile
from pyrig.rig.configs.license import LicenseConfigFile
from pyrig.rig.configs.pyproject import PyprojectConfigFile
from pyrig.rig.configs.workflows.health_check import HealthCheckWorkflow
from pyrig.rig.configs.workflows.release import ReleaseWorkflow
from pyrig.rig.tools.base.base import Tool, ToolGroup
from pyrig.rig.tools.docs_builder import DocsBuilder
from pyrig.rig.tools.remote_version_controller import RemoteVersionController
from pyrig.src.string_ import make_linked_badge_markdown


class BadgesMarkdownConfigFile(MarkdownConfigFile):
    """Base class for Markdown files with auto-generated project badges.

    Generates badges from pyproject.toml and Git metadata. Validates that file
    contains required badges, project name, and description.

    Subclasses must implement:
        - `parent_path`: Directory containing the Markdown file

    See Also:
        pyrig.rig.configs.base.markdown.MarkdownConfigFile: Parent class
        pyrig.rig.configs.pyproject.PyprojectConfigFile: Project metadata
        pyrig.src.git: Git repository utilities
    """

    @classmethod
    def is_correct(cls) -> bool:
        """Override to replace the description if it changed in pyproject.toml.

        Normally StringConfigFile.merge_configs prepends the expected lines to
        the actual lines. This leads to a stale description remaining in the file
        if it was changed in pyproject.toml. This override detects the old description
        block between ``---`` fences and replaces it with the current one before
        the normal merge runs.
        """
        if super().is_correct():
            return True
        file_content = cls.get_file_content()
        updated_content = cls.replace_description(file_content)
        # only dump if content changed
        if updated_content != file_content:
            cls.dump(updated_content.splitlines())
        # note dump clears the cache,
        # and this checks the real file again, which is the wanted behavior
        return super().is_correct()

    @classmethod
    def get_lines(cls) -> list[str]:
        """Generate Markdown with project name, categorized badges, and description.

        Returns:
            Formatted Markdown with H1 header, badge categories, and description.
        """
        project_name = PyprojectConfigFile.L.get_project_name()
        badges = cls.get_badges()
        badges_lines: list[str] = []
        for badge_category, badge_list in badges.items():
            badges_lines.append(f"<!-- {badge_category} -->")
            badges_lines.extend(badge_list)
        description = PyprojectConfigFile.L.get_project_description()
        return [
            f"# {project_name}",
            "",
            *badges_lines,
            "",
            "---",
            "",
            f"> {description}",
            "",
            "---",
            "",
        ]

    @classmethod
    def get_badges(cls) -> dict[str, list[str]]:
        """Get categorized badges from project metadata and Git info.

        Returns:
            Dict mapping category names (tooling, code-quality, package-info, ci/cd,
            documentation) to lists of badge Markdown strings.
        """
        python_versions = PyprojectConfigFile.L.get_supported_python_versions()
        joined_python_versions = "|".join(str(v) for v in python_versions)
        health_check_wf_name = HealthCheckWorkflow.filename()
        release_wf_name = ReleaseWorkflow.filename()
        badge_groups = Tool.grouped_badges()

        badge_groups[ToolGroup.PROJECT_INFO].extend(
            [
                make_linked_badge_markdown(
                    badge_url=f"https://img.shields.io/badge/python-{joined_python_versions}-blue.svg?logo=python&logoColor=white",
                    link_url="https://www.python.org",
                    alt_text="python",
                ),
                LicenseConfigFile.L.get_license_badge(),
            ]
        )
        badge_groups[ToolGroup.CI_CD].extend(
            [
                RemoteVersionController.L.get_cicd_badge(health_check_wf_name, "CI"),
                RemoteVersionController.L.get_cicd_badge(release_wf_name, "CD"),
            ]
        )

        badge_groups[DocsBuilder.L.group()].extend(
            [
                DocsBuilder.L.get_documentation_badge(),
            ]
        )
        return badge_groups

    @classmethod
    def replace_description(cls, content: str) -> str:
        """Replace the description between ``---`` fences with the current one."""
        expected_description = PyprojectConfigFile.L.get_project_description()
        pattern = r"---\s*\n(.*?)\n---"
        replacement = f"---\n\n> {expected_description}\n\n---"
        # only replace first occurence, as description is expected at the top
        return re.sub(pattern, replacement, content, count=1, flags=re.DOTALL)
