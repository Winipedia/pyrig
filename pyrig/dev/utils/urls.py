"""General URL construction utilities.

Provides functions for constructing URLs related to GitHub repositories, Pages,
PyPI, Codecov, and GitHub Actions.
"""

from pyrig.dev.utils.version_control import get_repo_owner_and_name_from_version_control


def get_codecov_url() -> str:
    """Construct Codecov dashboard URL.

    Returns:
        URL in format: `https://codecov.io/gh/{owner}/{repo}`
    """
    owner, repo = get_repo_owner_and_name_from_version_control(
        check_repo_url=False, url_encode=True
    )
    return f"https://codecov.io/gh/{owner}/{repo}"


def get_pypi_url() -> str:
    """Construct PyPI package URL.

    Assumes package name matches repository name.

    Returns:
        URL in format: `https://pypi.org/project/{repo}`
    """
    _, repo = get_repo_owner_and_name_from_version_control(
        check_repo_url=False, url_encode=True
    )
    return f"https://pypi.org/project/{repo}"


def get_pypi_badge_url() -> str:
    """Construct PyPI version badge URL.

    Returns:
        shields.io badge URL for PyPI version.
    """
    _, repo = get_repo_owner_and_name_from_version_control(
        check_repo_url=False, url_encode=True
    )
    return f"https://img.shields.io/pypi/v/{repo}?logo=pypi&logoColor=white"
