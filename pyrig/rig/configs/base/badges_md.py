"""Markdown badge file configuration management.

Provides BadgesMarkdownConfigFile for creating Markdown files with auto-generated
project badges from pyproject.toml and Git metadata.

Example:
    >>> from pathlib import Path
    >>> from pyrig.rig.configs.base.badges_md import BadgesMarkdownConfigFile
    >>>
    >>> class ReadmeFile(BadgesMarkdownConfigFile):
    ...
    ...     def parent_path(self) -> Path:
    ...     def parent_path(self) -> Path:
    ...
    ...
    ...     def filename(self) -> str:
    ...     def filename(self) -> str:
    >>>
    >>> ReadmeFile()  # Creates README.md with badges
"""

import re

from pyrig.rig.configs.base.markdown import MarkdownConfigFile
from pyrig.rig.configs.license import LicenseConfigFile
from pyrig.rig.configs.pyproject import PyprojectConfigFile
from pyrig.rig.configs.workflows.health_check import HealthCheckWorkflowConfigFile
from pyrig.rig.configs.workflows.release import ReleaseWorkflowConfigFile
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
        pyrig.rig.tools.remote_version_controller.RemoteVersionController:
            Repository related badges and more
    """

    def is_correct(self) -> bool:
        """Check correctness, replacing a stale description if needed.

        Normally `StringConfigFile.I.merge_configs` prepends the expected lines to
        the actual lines. This leads to a stale description remaining in the file
        if it was changed in pyproject.toml. This override detects the old description
        block between `---` fences and replaces it with the current one before
        the normal merge runs.

        Returns:
            True if the file contains all expected content.
    def is_correct(self) -> bool:
        if super().is_correct():
            return True
        file_content = self.file_content()
        updated_content = self.replace_description(file_content)
        # only dump if content changed
        if updated_content != file_content:
            self.dump(updated_content.splitlines())
        # note dump clears the cache,
        # and this checks the real file again, which is the wanted behavior
        return super().is_correct()

    def lines(self) -> list[str]:
        """Generate Markdown with project name, categorized badges, and description.

        Returns:
            Formatted Markdown with H1 header, badge categories, and description.
    def lines(self) -> list[str]:
        project_name = PyprojectConfigFile.I.project_name()
        badges = self.badges()
        badges_lines: list[str] = []
        for badge_category, badge_list in badges.items():
            badges_lines.append(f"<!-- {badge_category} -->")
            badges_lines.extend(badge_list)
        description = PyprojectConfigFile.I.project_description()
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

    def badges(self) -> dict[str, list[str]]:
        """Return categorized badges from project metadata and CI/CD configurations.

        Returns:
            Dict mapping category names (tooling, code-quality, package-info, ci/cd,
            documentation) to lists of badge Markdown strings.
        """
        python_versions = PyprojectConfigFile.I.supported_python_versions()
        joined_python_versions = "|".join(str(v) for v in python_versions)
        health_check_wf_name = HealthCheckWorkflowConfigFile.I.filename()
        release_wf_name = ReleaseWorkflowConfigFile.I.filename()
        badge_groups = Tool.grouped_badges()

        badge_groups[ToolGroup.PROJECT_INFO].extend(
            [
                make_linked_badge_markdown(
                    badge_url=f"https://img.shields.io/badge/python-{joined_python_versions}-blue.svg?logo=python&logoColor=white",
                    link_url="https://www.python.org",
                    alt_text="python",
                ),
                LicenseConfigFile.I.license_badge(),
            ]
        )
        badge_groups[ToolGroup.CI_CD].extend(
            [
                RemoteVersionController.I.cicd_badge(health_check_wf_name, "CI"),
                RemoteVersionController.I.cicd_badge(release_wf_name, "CD"),
            ]
        )

        badge_groups[DocsBuilder.I.group()].extend(
            [
                DocsBuilder.I.documentation_badge(),
            ]
        )
        return badge_groups

    def replace_description(self, content: str) -> str:
        """Replace the description between `---` fences with the current one.

        Args:
            content: Markdown file content to update.

        Returns:
            Updated content with the current description from pyproject.toml.
        """
        expected_description = PyprojectConfigFile.I.project_description()
        pattern = r"---\s*\n(.*?)\n---"
        replacement = f"---\n\n> {expected_description}\n\n---"
        # only replace first occurence, as description is expected at the top
        return re.sub(pattern, replacement, content, count=1, flags=re.DOTALL)
