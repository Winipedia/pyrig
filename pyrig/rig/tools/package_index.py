"""PyPI package index wrapper.

Provides type-safe wrapper for PyPI package information and badges.
Shows package version badge from PyPI.

Example:
    >>> from pyrig.rig.tools.package_index import PackageIndex
    >>> PackageIndex.L.get_package_index_url()
"""

from pyrig.rig.tools.base.base import Tool, ToolGroup
from pyrig.rig.tools.version_controller import VersionController


class PackageIndex(Tool):
    """PyPI package index wrapper.

    Constructs PyPI URLs and badge information for package distribution.
    Integrates with PyPI for package version tracking and badges.

    Operations:
        - Package URL generation
        - Version badge generation
        - PyPI integration

    Example:
        >>> PackageIndex.L.get_package_index_url()
    """

    @classmethod
    def name(cls) -> str:
        """Get tool name.

        Returns:
            'pypi'
        """
        return "pypi"

    @classmethod
    def group(cls) -> str:
        """Returns the group the tools belongs to.

        E.g. testing, tool, code-quality etc...
        """
        return ToolGroup.PROJECT_INFO

    @classmethod
    def badge_urls(cls) -> tuple[str, str]:
        """Returns the badge and connected page."""
        _, repo = VersionController.L.get_repo_owner_and_name(
            check_repo_url=False, url_encode=True
        )
        return (
            f"https://img.shields.io/pypi/v/{repo}?logo=pypi&logoColor=white",
            cls.get_package_index_url(),
        )

    @classmethod
    def get_package_index_url(cls) -> str:
        """Construct PyPI package URL.

        Assumes package name matches repository name.

        Returns:
            URL in format: `https://pypi.org/project/{repo}`
        """
        _, repo = VersionController.L.get_repo_owner_and_name(
            check_repo_url=False, url_encode=True
        )
        return f"https://pypi.org/project/{repo}"

    @classmethod
    def dev_dependencies(cls) -> list[str]:
        """Get development dependencies for this tool.

        Returns:
            List of package names required for development (e.g. API clients).
        """
        # No dev dependencies needed for PyPI integration,
        # the package manager like uv handles this via the pyproject.toml file.
        return []
