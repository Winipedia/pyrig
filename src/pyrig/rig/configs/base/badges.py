"""Badge-augmented Markdown configuration base class."""

import re
from abc import abstractmethod
from collections import defaultdict
from typing import Any

from pyrig.rig.configs.base.markdown import MarkdownConfigFile
from pyrig.rig.configs.community.license import LicenseConfigFile
from pyrig.rig.configs.pyproject import PyprojectConfigFile
from pyrig.rig.configs.version_control.remote.workflows.health_check import (
    HealthCheckWorkflowConfigFile,
)
from pyrig.rig.configs.version_control.remote.workflows.release import (
    ReleaseWorkflowConfigFile,
)
from pyrig.rig.tools.base.tool import Group, Tool
from pyrig.rig.tools.version_control.remote.controller import (
    RemoteVersionController,
)


class BadgesConfigFile(MarkdownConfigFile):
    """Base class for Markdown configuration files with auto-generated project badges.

    Generated files include a heading, badges grouped by category, and a
    project description sourced from pyproject.toml. When updating an
    existing file, stale badges and descriptions are replaced in-place where
    possible, preserving any user additions.

    Subclasses must implement:
        - `heading`: Return the heading text for the generated file.
        - `parent_path`: Directory containing the file.
        - `stem`: Filename without its extension.
    """

    @abstractmethod
    def heading(self) -> str:
        """Return the heading text for the generated file.

        Returns:
            Heading text to use in the Markdown file.
        """

    def content(self) -> str:
        """Return the project header: title, grouped badge rows, and description.

        Badge rows are grouped under HTML comment category labels; the project
        description is formatted as a blockquote.

        Returns:
            Markdown content forming the project header section.
        """
        return f"""# {self.heading()}

{self.badges_content()}

---

> {PyprojectConfigFile.I.project_description()}

---
"""

    def badges_content(self) -> str:
        """Return the Markdown content for all badge groups."""
        return self.join_lines(
            line
            for category, badge_list in self.badges().items()
            for line in (f"<!-- {category} -->", *badge_list)
        )

    def merge_configs(self) -> list[Any]:
        """Return merged file content with current badge URLs and project description.

        Prefers an in-place update of the existing content to preserve any user
        additions, falling back to the default merge strategy when the in-place
        update does not yield all required content.

        Returns:
            Merged lines with current badge URLs and project description. User
            additions are preserved when the in-place update is sufficient.
        """
        updated_content = self.replace_description(self.read_content())
        updated_content = self.replace_badges(updated_content)
        updated_lines = self.split_lines(updated_content)
        if self.configs_is_subset(updated_lines):
            return updated_lines

        return super().merge_configs()

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

        old_badges_content = content.split("\n---\n\n>", 1)[0]
        badges_content = old_badges_content
        for badge in expected_badges:
            alt_text_match = re.search(r"\[!\[(.*?)\]", badge)
            if not alt_text_match:
                continue
            alt_text = alt_text_match.group(1)
            pattern = rf".*\[!\[{re.escape(alt_text)}\].*"
            badges_content = re.sub(
                pattern,
                lambda _, badge=badge: badge,
                badges_content,
            )
        return content.replace(old_badges_content, badges_content, 1)

    def badges(self) -> dict[str, list[str]]:
        """Return all project badges grouped by category.

        The result includes badges for each registered tool and the badges
        defined by `additional_badges()`. By default, the license badge is
        appended to `"project-info"`, and the health check and release workflow
        badges are inserted first in `"project-status"`, in that order.

        Returns:
            Category name to list of badge Markdown strings. The
            `"project-info"` and `"project-status"` keys are present by default;
            other keys appear only when a registered tool belongs to that
            `Group` category.
        """
        badge_groups = Tool.grouped_badges()
        self.add_additional_badges(badge_groups)
        return badge_groups

    def add_additional_badges(
        self,
        grouped_badges: defaultdict[str, list[str]],
    ) -> None:
        """Add the badges defined by `additional_badges()` in tuple order.

        Args:
            grouped_badges: Badge groups to modify in place.
        """
        for badge, group, index in self.additional_badges():
            self.add_badge(
                grouped_badges,
                badge=badge,
                group=group,
                index=index,
            )

    def add_badge(
        self,
        grouped_badges: defaultdict[str, list[str]],
        *,
        badge: str,
        group: str,
        index: int | None = None,
    ) -> None:
        """Append or insert a badge into a group, creating the group if absent.

        Args:
            grouped_badges: Badge groups to modify in place.
            badge: Markdown badge string to add.
            group: Category name receiving the badge.
            index: Insertion position using `list.insert()` semantics, or
                `None` to append after the group's existing badges.
        """
        if index is None:
            grouped_badges[group].append(badge)
        else:
            grouped_badges[group].insert(index, badge)

    def additional_badges(self) -> tuple[tuple[str, str, int | None], ...]:
        """Return the non-tool badges and their insertion positions.

        Returns:
            Tuples in `(badge, group, index)` order. Defaults to the license
            badge appended to `"project-info"`, followed by the health check
            and release workflow badges at indices 0 and 1 in `"project-status"`.
            An index of `None` appends the badge.
        """
        return (
            (
                LicenseConfigFile.I.license_badge(),
                Group.PROJECT_INFO,
                None,
            ),
            (
                RemoteVersionController.I.cicd_badge(
                    HealthCheckWorkflowConfigFile.I.stem(),
                    "CI",
                ),
                Group.PROJECT_STATUS,
                0,
            ),
            (
                RemoteVersionController.I.cicd_badge(
                    ReleaseWorkflowConfigFile.I.stem(),
                    "CD",
                ),
                Group.PROJECT_STATUS,
                1,
            ),
        )
