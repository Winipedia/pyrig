"""This module defines the ProgrammingLanguage tool.

It provides information about the programming language used in the project.
This will always be python but this functions as a warpper for reusability and
consistency across the codebase.
It also provides the badge urls for the programming language badge.
"""

from pyrig.rig.tools.base.base import Tool, ToolGroup
from pyrig.rig.tools.package_manager import PackageManager


class ProgrammingLanguage(Tool):
    """Tool class that wraps info and functionality related to the programming language.

    This tool provides the badge urls for the programming language badge and other
    info related to the programming language used in the project.
    """

    def name(self) -> str:
        """Return the name of the tool."""
        return "python"

    def group(self) -> str:
        """Return the group to which the tool belongs."""
        return ToolGroup.PROJECT_INFO

    def badge_urls(self) -> tuple[str, str]:
        """Return badge image URL and link URL for the programming language badge."""
        return (
            f"https://img.shields.io/pypi/pyversions/{PackageManager.I.project_name()}",
            "https://www.python.org",
        )

    def dev_dependencies(self) -> tuple[str, ...]:
        """No dev dependencies needed for the programming language itself."""
        return ()
