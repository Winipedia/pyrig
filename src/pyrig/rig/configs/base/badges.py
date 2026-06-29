"""Badge-augmented Markdown configuration base class."""

import re
from typing import Any

from pyrig.rig.configs.base.markdown import MarkdownConfigFile
from pyrig.rig.configs.license import LicenseConfigFile
from pyrig.rig.configs.pyproject import PyprojectConfigFile
from pyrig.rig.configs.version_control.remote.workflows.deploy import (
    DeployWorkflowConfigFile,
)
from pyrig.rig.configs.version_control.remote.workflows.health_check import (
    HealthCheckWorkflowConfigFile,
)
from pyrig.rig.tools.base.tool import Group, Tool
from pyrig.rig.tools.package_manager import PackageManager
from pyrig.rig.tools.version_control.remote import (
    RemoteVersionController,
)


class BadgesConfigFile(MarkdownConfigFile):
    """Base class for Markdown configuration files with auto-generated project badges.

    Generated files include a project name header, badges grouped by category,
    and a project description sourced from pyproject.toml. When updating an
    existing file, stale badges and descriptions are replaced in-place where
    possible, preserving any user additions.
    """

    def merge_configs(self) -> list[Any]:
        """Return merged file content with current badge URLs and project description.

        Prefers an in-place update of the existing content to preserve any user
        additions. Falls back to prepending all required content before the
        existing file content when the in-place update is insufficient.

        Returns:
            Merged lines with current badge URLs and project description. User
            additions are preserved when the in-place update is sufficient.
        """
        updated_content = self.replace_description(self.read_content())
        updated_content = self.replace_badges(updated_content)
        if self.all_lines_in_content(lines=self.configs(), content=updated_content):
            return self.split_lines(updated_content)

        return super().merge_configs()

    def lines(self) -> list[str]:
        """Return the project header: title, grouped badge rows, and description.

        Badge rows are grouped under HTML comment category labels; the project
        description is formatted as a blockquote.

        Returns:
            Markdown lines forming the project header section.
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

    def replace_description(self, content: str) -> str:
        """Replace the description block with the current one from pyproject.toml.

        Locates the first description block (text between the first two `---`
        dividers) and replaces its content with the current project description.
        Only the first occurrence is replaced.

        Args:
            content: Full Markdown file content to update.

        Returns:
            Updated content with the current description in place of the old one.
            If no `---` divider pattern is found, the content is returned unchanged.
        """
        pattern = r"---\s*\n(.*?)\n---"
        replacement = f"---\n\n> {PyprojectConfigFile.I.project_description()}\n\n---"
        # only replace first occurrence, as description is expected at the top
        return re.sub(pattern, lambda _: replacement, content, count=1, flags=re.DOTALL)

    def replace_badges(self, content: str) -> str:
        """Replace stale badge URLs in the badge section with current ones.

        Badge lines are only matched in the content preceding the description
        blockquote; the description and everything after it are left unchanged.

        Args:
            content: Full Markdown file content to update.

        Returns:
            Updated content with current badge URLs in place of stale ones.
        """
        expected_badges = (badge for group in self.badges().values() for badge in group)

        # only consider content before description
        old_badges_content = content.split("\n---\n\n>", 1)[0]
        badges_content = old_badges_content
        for badge in expected_badges:
            # extract the alt text from the badge markdown — used as stable identifier
            alt_text_match = re.search(r"\[!\[(.*?)\]", badge)
            if not alt_text_match:
                continue
            alt_text = alt_text_match.group(1)
            # find and replace the line containing the badge with the same alt text
            pattern = rf".*\[!\[{re.escape(alt_text)}\].*"
            badges_content = re.sub(
                pattern, lambda _, badge=badge: badge, badges_content
            )
        # replace the old badges content with the updated one
        return content.replace(old_badges_content, badges_content, 1)

    def badges(self) -> dict[str, list[str]]:
        """Return all project badges grouped by category.

        The result includes badges for each registered tool, a license badge in
        the `"project-info"` group, and CI/CD workflow status badges for the
        health check and deploy workflows in the `"ci/cd"` group.

        Returns:
            Category name to list of badge Markdown strings, with keys `"ci/cd"`,
            `"testing"`, `"code-quality"`, `"tooling"`, and `"project-info"`.
        """
        badge_groups = Tool.grouped_badges()

        badge_groups[Group.PROJECT_INFO].extend(
            [
                LicenseConfigFile.I.license_badge(),
            ]
        )
        badge_groups[Group.CI_CD].extend(
            [
                RemoteVersionController.I.cicd_badge(
                    HealthCheckWorkflowConfigFile.I.stem(), "CI"
                ),
                RemoteVersionController.I.cicd_badge(
                    DeployWorkflowConfigFile.I.stem(), "CD"
                ),
            ]
        )

        return badge_groups
