"""module."""

from pyrig.rig.tools import remote_version_controller
from pyrig.rig.tools.remote_version_controller import RemoteVersionController


class TestRemoteVersionController:
    """Test class."""

    def test_access_token_key(self) -> None:
        """Test method."""
        assert RemoteVersionController.I.access_token_key() == "REPO_TOKEN"

    def test_running_in_ci(self) -> None:
        """Test method."""
        assert isinstance(RemoteVersionController.I.running_in_ci(), bool)

    def test_cicd_badge(self) -> None:
        """Test method."""
        result = RemoteVersionController.I.cicd_badge_url("health_check", "CI")
        expected = "https://img.shields.io/github/actions/workflow/status/Winipedia/pyrig/health_check.yml?label=CI&logo=github"
        assert result == expected, f"Expected {expected}, got {result}"

    def test_group(self) -> None:
        """Test method."""
        result = RemoteVersionController.I.group()
        assert isinstance(result, str)
        assert result == "tooling"

    def test_badge_urls(self) -> None:
        """Test method."""
        result = RemoteVersionController.I.badge_urls()
        assert isinstance(result, tuple)
        assert all(isinstance(url, str) for url in result)

    def test_dev_dependencies(self) -> None:
        """Test method."""
        result = RemoteVersionController.I.dev_dependencies()
        assert result == ("pygithub",)

    def test_name(self) -> None:
        """Test method."""
        result = RemoteVersionController.I.name()
        assert result == "github"

    def test_url_base(self) -> None:
        """Test method."""
        result = RemoteVersionController.I.url_base()
        assert isinstance(result, str), f"Expected str, got {type(result)}"
        assert result == "https://github.com"

    def test_repo_url(self) -> None:
        """Test method."""
        result = RemoteVersionController.I.repo_url()
        assert result == "https://github.com/Winipedia/pyrig"

    def test_issues_url(self) -> None:
        """Test method."""
        result = RemoteVersionController.I.issues_url()
        assert result == "https://github.com/Winipedia/pyrig/issues"

    def test_releases_url(self) -> None:
        """Test method."""
        result = RemoteVersionController.I.releases_url()
        assert result == "https://github.com/Winipedia/pyrig/releases"

    def test_cicd_url(self) -> None:
        """Test method."""
        result = RemoteVersionController.I.cicd_url("health_check")
        assert (
            result
            == "https://github.com/Winipedia/pyrig/actions/workflows/health_check.yml"
        )

    def test_cicd_badge_url(self) -> None:
        """Test method."""
        result = RemoteVersionController.I.cicd_badge_url("health_check", "CI")
        assert (
            result
            == "https://img.shields.io/github/actions/workflow/status/Winipedia/pyrig/health_check.yml?label=CI&logo=github"
        )


def test_module_docstring() -> None:
    """Test module docstring."""
    assert (
        remote_version_controller.__doc__
        == """Remote version controller wrapper.

Wraps RemoteVersionController commands and information.
"""
    )
