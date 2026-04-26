"""Badge-augmented Markdown configuration base class.

Extends Markdown file management with auto-generated project badges assembled
from pyproject.toml, CI/CD workflow metadata, and registered tool definitions.
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

    Generates a Markdown header section consisting of the project name, grouped
    badge rows (tooling, code quality, CI/CD, documentation, etc.), and a fenced
    project description block read from pyproject.toml.

    The ``merge_configs`` override handles stale files intelligently: when the
    file already exists but has an outdated description or badge URLs, it updates
    only those parts in-place before falling back to the standard prepend merge.

    Subclasses must implement:
        - ``parent_path``: Directory that will contain the Markdown file
    """

    def merge_configs(self) -> ConfigList:
        """Merge file content, updating stale badges and description in-place.

        Overrides the standard merge to attempt a targeted in-place update before
        resorting to a full prepend. The existing file content is first patched
        using ``replace_description`` and ``replace_badges``. If all required lines
        are present after patching, the patched content is returned directly,
        preserving any user additions. If the patched content is still missing
        required lines, the standard merge runs, prepending all expected lines
        before the existing content.

        Returns:
            Merged list of lines with description and badge URLs updated in-place,
            or the full expected content prepended to existing content if an
            in-place update was insufficient.
        """
        updated_content = self.replace_description(self.read_content())
        updated_content = self.replace_badges(updated_content)
        if self.all_lines_in_content(lines=self.configs(), content=updated_content):
            return self.split_lines(updated_content)

        return super().merge_configs()

    def lines(self) -> list[str]:
        """Generate the initial Markdown content with badges and description.

        Produces an H1 header with the project name, followed by badge rows grouped
        under HTML comment category labels, then the project description in a fenced
        blockquote block.

        Returns:
            List of Markdown lines: H1 header, grouped badge rows, and a fenced
            description block.
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

        Locates the first fenced description block (text between the first two
        ``---`` dividers) and replaces its content with the current project
        description. Only the first occurrence is replaced, since the description
        is always at the top of the file.

        Args:
            content: Full Markdown file content to update.

        Returns:
            Updated content with the current description in place of the old one.
            If no ``---`` fence pattern is found, the content is returned unchanged.
        """
        expected_description = PyprojectConfigFile.I.project_description()
        pattern = r"---\s*\n(.*?)\n---"
        replacement = f"---\n\n> {expected_description}\n\n---"
        # only replace first occurrence, as description is expected at the top
        return re.sub(pattern, replacement, content, count=1, flags=re.DOTALL)

    def replace_badges(self, content: str) -> str:
        """Replace stale badge URLs in the badge section with current ones.

        For each expected badge, the alt text acts as a stable identifier to
        locate the matching badge line in the existing content. If a match is
        found, the old line is replaced with the current badge, including any
        updated URLs. Only the content before the first ``---`` divider is
        treated as the badge section.

        Args:
            content: Full Markdown file content to update.

        Returns:
            Updated content with current badge URLs in place of stale ones.
        """
        expected_badges = (badge for group in self.badges().values() for badge in group)

        # only consider content before description
        badges_content = content.split("---", 1)[0]
        for badge in expected_badges:
            # extract the alt text from the badge markdown — used as stable identifier
            alt_text_match = re.search(r"\[!\[(.*?)\]", badge)
            if not alt_text_match:
                continue
            alt_text = alt_text_match.group(1)
            # find and replace the line containing the badge with the same alt text
            pattern = rf".*\[!\[{re.escape(alt_text)}\].*"
            badges_content = re.sub(pattern, badge, badges_content)
        # replace the old badges content with the updated one
        return content.replace(content.split("---", 1)[0], badges_content)

    def badges(self) -> dict[str, list[str]]:
        """Collect all project badges grouped by category.

        Builds on ``Tool.grouped_badges()``, which gathers badges from all
        registered ``Tool`` subclasses, then appends the license badge, CI/CD
        workflow status badges, and the documentation badge to their respective
        groups.

        Returns:
            Dict mapping category names (e.g., ``"tooling"``, ``"code-quality"``,
            ``"project-info"``, ``"ci/cd"``, ``"documentation"``) to lists of
            badge Markdown strings.
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
