"""PyPI package index wrapper.

Provides PyPI package URL generation and version badge integration.
Assumes the PyPI package name matches the Git repository name.

Example:
    >>> from pyrig.rig.tools.package_index import PackageIndex
    >>> PackageIndex.I.package_index_url()
    'https://pypi.org/project/pyrig'
"""

from pyrig.rig.tools.base.base import Tool, ToolGroup
from pyrig.rig.tools.version_controller import VersionController


class PackageIndex(Tool):
    """PyPI package index wrapper.

    Constructs PyPI URLs and badge information for package distribution.
    Uses `pyrig.rig.tools.version_controller.VersionController` to derive
    the package name from the Git repository name.

    Example:
        >>> PackageIndex.I.package_index_url()
        'https://pypi.org/project/pyrig'
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
        """Get tool group.

        Returns:
            `ToolGroup.PROJECT_INFO`
        """
        return ToolGroup.PROJECT_INFO

    @classmethod
    def badge_urls(cls) -> tuple[str, str]:
        """Returns the PyPI version badge and project page URLs."""
        _, repo = VersionController.I.repo_owner_and_name(
            check_repo_url=False, url_encode=True
        )
        return (
            f"https://img.shields.io/pypi/v/{repo}?logo=pypi&logoColor=white",
            cls.package_index_url(),
        )

    @classmethod
    def package_index_url(cls) -> str:
        """Construct PyPI package URL.

        Assumes package name matches repository name.

        Returns:
            URL in format: `https://pypi.org/project/{repo}`
        """
        _, repo = VersionController.I.repo_owner_and_name(
            check_repo_url=False, url_encode=True
        )
        return f"https://pypi.org/project/{repo}"

    @classmethod
    def dev_dependencies(cls) -> list[str]:
        """Get development dependencies for this tool.

        PyPI integration requires no dev dependencies; the package manager
        (e.g. uv) handles publishing via pyproject.toml.

        Returns:
            Empty list.
        """
        return []
