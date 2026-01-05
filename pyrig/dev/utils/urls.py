"""General URL construction utilities.

Provides functions for constructing URLs related to GitHub repositories, Pages,
PyPI, Codecov, and GitHub Actions.
"""

from pyrig.dev.utils.version_control import get_repo_owner_and_name_from_version_control


def get_github_repo_url() -> str:
    """Construct HTTPS GitHub repository URL.

    Returns:
        URL in format: `https://github.com/{owner}/{repo}`
    """
    owner, repo = get_repo_owner_and_name_from_version_control(
        check_repo_url=False, url_encode=True
    )
    return f"https://github.com/{owner}/{repo}"


def get_github_pages_url() -> str:
    """Construct GitHub Pages URL.

    Returns:
        URL in format: `https://{owner}.github.io/{repo}`

    Note:
        Site may not exist if GitHub Pages not enabled.
    """
    owner, repo = get_repo_owner_and_name_from_version_control(
        check_repo_url=False, url_encode=True
    )
    return f"https://{owner}.github.io/{repo}"


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


def get_github_workflow_run_url(workflow_name: str) -> str:
    """Construct GitHub Actions workflow run URL.

    Args:
        workflow_name: Workflow file name without `.yaml` extension.

    Returns:
        URL to workflow execution history.
    """
    owner, repo = get_repo_owner_and_name_from_version_control(
        check_repo_url=False, url_encode=True
    )
    return f"https://github.com/{owner}/{repo}/actions/workflows/{workflow_name}.yaml"


def get_github_workflow_badge_url(workflow_name: str, label: str, logo: str) -> str:
    """Construct GitHub Actions workflow status badge URL.

    Args:
        workflow_name: Workflow file name without `.yaml` extension.
        label: Badge text label (e.g., "CI", "Build").
        logo: shields.io logo identifier (e.g., "github", "python").

    Returns:
        shields.io badge URL showing workflow status.
    """
    owner, repo = get_repo_owner_and_name_from_version_control(
        check_repo_url=False, url_encode=True
    )
    return f"https://img.shields.io/github/actions/workflow/status/{owner}/{repo}/{workflow_name}.yaml?label={label}&logo={logo}"


def get_licence_badge_url() -> str:
    """Construct GitHub license badge URL.

    Returns:
        shields.io badge URL showing repository license.
    """
    owner, repo = get_repo_owner_and_name_from_version_control(
        check_repo_url=False, url_encode=True
    )
    return f"https://img.shields.io/github/license/{owner}/{repo}"
