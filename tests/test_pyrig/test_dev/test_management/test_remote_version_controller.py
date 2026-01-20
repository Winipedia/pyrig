"""module."""

from pyrig.dev.management.remote_version_controller import RemoteVersionController


class TestRemoteVersionController:
    """Test class."""

    def test_name(self) -> None:
        """Test method."""
        result = RemoteVersionController.L.name()
        assert result == "github"

    def test_get_url_base(self) -> None:
        """Test method."""
        result = RemoteVersionController.L.get_url_base()
        assert isinstance(result, str), f"Expected str, got {type(result)}"
        assert result == "https://github.com"

    def test_get_repo_url(self) -> None:
        """Test method."""
        result = RemoteVersionController.L.get_repo_url()
        assert result == "https://github.com/Winipedia/pyrig"

    def test_get_issues_url(self) -> None:
        """Test method."""
        result = RemoteVersionController.L.get_issues_url()
        assert result == "https://github.com/Winipedia/pyrig/issues"

    def test_get_releases_url(self) -> None:
        """Test method."""
        result = RemoteVersionController.L.get_releases_url()
        assert result == "https://github.com/Winipedia/pyrig/releases"

    def test_get_documentation_url(self) -> None:
        """Test method."""
        result = RemoteVersionController.L.get_documentation_url()
        assert result == "https://Winipedia.github.io/pyrig"

    def test_get_cicd_url(self) -> None:
        """Test method."""
        result = RemoteVersionController.L.get_cicd_url("health_check")
        assert (
            result
            == "https://github.com/Winipedia/pyrig/actions/workflows/health_check.yml"
        )

    def test_get_cicd_badge_url(self) -> None:
        """Test method."""
        result = RemoteVersionController.L.get_cicd_badge_url(
            "health_check", "CI", "github"
        )
        assert (
            result
            == "https://img.shields.io/github/actions/workflow/status/Winipedia/pyrig/health_check.yml?label=CI&logo=github"
        )

    def test_get_license_badge_url(self) -> None:
        """Test method."""
        result = RemoteVersionController.L.get_license_badge_url()
        assert result == "https://img.shields.io/github/license/Winipedia/pyrig"
