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
    ...         return Path()
    ...
    ...
    ...     def filename(self) -> str:
    ...         return "README"
    >>>
    >>> ReadmeFile()  # Creates README.md with badges
"""

import re

from pyrig.rig.configs.base.config_file import ConfigList
from pyrig.rig.configs.base.markdown import MarkdownConfigFile
from pyrig.rig.configs.license import LicenseConfigFile
from pyrig.rig.configs.pyproject import PyprojectConfigFile
from pyrig.rig.configs.remote_version_control.workflows.health_check import (
    HealthCheckWorkflowConfigFile,
)
from pyrig.rig.configs.remote_version_control.workflows.release import (
    ReleaseWorkflowConfigFile,
)
from pyrig.rig.tools.base.tool import Tool, ToolGroup
from pyrig.rig.tools.docs_builder import DocsBuilder
from pyrig.rig.tools.package_manager import PackageManager
from pyrig.rig.tools.remote_version_controller import RemoteVersionController


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

    def merge_configs(self) -> ConfigList:
        """Check correctness, replacing a stale description if needed.

        Normally `StringConfigFile.I.merge_configs` prepends the expected lines to
        the actual lines. This leads to a stale description remaining in the file
        if it was changed in pyproject.toml. This override detects the old description
        block between `---` fences and replaces it with the current one before
        the normal merge runs.

        Returns:
            True if the file contains all expected content.
        """
        updated_content = self.replace_description(self.file_content())
        updated_content = self.replace_badges(updated_content)
        if self.all_lines_in_content(lines=self.configs(), content=updated_content):
            return self.split_lines(updated_content)

        return super().merge_configs()

    def lines(self) -> list[str]:
        """Generate Markdown with project name, categorized badges, and description.

        Returns:
            Formatted Markdown with H1 header, badge categories, and description.
        """
        project_name = PackageManager.I.project_name()
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
        badge_groups = Tool.grouped_badges()

        badge_groups[ToolGroup.PROJECT_INFO].extend(
            [
                LicenseConfigFile.I.license_badge(),
            ]
        )
        badge_groups[ToolGroup.CI_CD].extend(
            [
                RemoteVersionController.I.cicd_badge(
                    HealthCheckWorkflowConfigFile.I.stem(), "CI"
                ),
                RemoteVersionController.I.cicd_badge(
                    ReleaseWorkflowConfigFile.I.stem(), "CD"
                ),
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

    def replace_badges(self, content: str) -> str:
        """Replace existing badges with the current ones.

        Each badge is in the format:
            [![ToolClsName](badge-url)](linked-url)
        The tool cls name is the constant identifier for the badge,
        so if one the urls for a cls name chnaged we replace it.

        Args:
            content: Markdown file content to update.

        Returns:
            Updated content with current badges.
        """
        expected_badges = (badge for group in self.badges().values() for badge in group)

        # only consider content before description
        badges_content = content.split("---", 1)[0]
        for badge in expected_badges:
            # extract the alt text (tool cls name) from the badge markdown
            alt_text_match = re.search(r"\[!\[(.*?)\]", badge)
            if not alt_text_match:
                continue
            alt_text = alt_text_match.group(1)
            # extract the line containing the badge with the same alt text
            pattern = rf".*\[!\[{re.escape(alt_text)}\].*"
            badges_content = re.sub(pattern, badge, badges_content)
        # replace the old badges content with the updated one
        return content.replace(content.split("---", 1)[0], badges_content)
