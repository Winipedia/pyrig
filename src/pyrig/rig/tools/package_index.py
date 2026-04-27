"""Package index tool wrapper.

Wraps PackageIndex commands and information.
"""

from pyrig.rig.tools.base.tool import Tool, ToolGroup
from pyrig.rig.tools.package_manager import PackageManager


class PackageIndex(Tool):
    """PyPI package index wrapper.

    Constructs the PyPI project URL and shields.io version badge for the
    current project. The package name is read from ``PackageManager.I.project_name()``.

    Example:
        >>> PackageIndex.I.package_index_url()
        'https://pypi.org/project/pyrig'
    """

    def name(self) -> str:
        """Get tool name.

        Returns:
            'pypi'
        """
        return "pypi"

    def group(self) -> str:
        """Returns the group the tool belongs to.

        Returns:
            `ToolGroup.PROJECT_INFO`
        """
        return ToolGroup.PROJECT_INFO

    def badge_urls(self) -> tuple[str, str]:
        """Return the PyPI version badge image URL and project page URL.

        Returns:
            Tuple of ``(badge_url, page_url)`` where ``badge_url`` is a
            shields.io URL displaying the published PyPI version and
            ``page_url`` is the package's PyPI project page.
        """
        repo = PackageManager.I.project_name()
        return (
            f"https://img.shields.io/pypi/v/{repo}?logo=pypi&logoColor=white",
            self.package_index_url(),
        )

    def package_index_url(self) -> str:
        """Construct the PyPI project page URL.

        Uses the project name from ``PackageManager.I.project_name()``.

        Returns:
            URL in format: ``https://pypi.org/project/{repo}``
        """
        repo = PackageManager.I.project_name()
        return f"https://pypi.org/project/{repo}"

    def dev_dependencies(self) -> tuple[str, ...]:
        """Get development dependencies for this tool.

        Returns an empty tuple because PyPI itself requires no extra
        development dependency; publishing is handled by the package
        manager (e.g. uv) via ``pyproject.toml``.

        Returns:
            Empty tuple.
        """
        return ()

    def access_token_key(self) -> str:
        """Get the environment variable key for the PyPI access token.

        Used in CI/CD pipelines to authenticate when publishing packages
        to PyPI.

        Returns:
            ``'PYPI_TOKEN'``
        """
        return "PYPI_TOKEN"
