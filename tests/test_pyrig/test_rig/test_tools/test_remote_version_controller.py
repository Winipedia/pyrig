"""module."""

from pyrig.rig.tools.remote_version_controller import RemoteVersionController


class TestRemoteVersionController:
    """Test class."""

    def test_cicd_badge(self) -> None:
        """Test method."""
        result = RemoteVersionController.L.cicd_badge_url("health_check", "CI")
        expected = "https://img.shields.io/github/actions/workflow/status/Winipedia/pyrig/health_check.yml?label=CI&logo=github"
        assert result == expected, f"Expected {expected}, got {result}"

    def test_group(self) -> None:
        """Test method."""
        result = RemoteVersionController.L.group()
        assert isinstance(result, str)
        assert result == "tooling"

    def test_badge_urls(self) -> None:
        """Test method."""
        result = RemoteVersionController.L.badge_urls()
        assert isinstance(result, tuple)
        assert all(isinstance(url, str) for url in result)

    def test_dev_dependencies(self) -> None:
        """Test method."""
        result = RemoteVersionController.L.dev_dependencies()
        assert result == ["pygithub"]

    def test_name(self) -> None:
        """Test method."""
        result = RemoteVersionController.L.name()
        assert result == "github"

    def test_url_base(self) -> None:
        """Test method."""
        result = RemoteVersionController.L.url_base()
        assert isinstance(result, str), f"Expected str, got {type(result)}"
        assert result == "https://github.com"

    def test_repo_url(self) -> None:
        """Test method."""
        result = RemoteVersionController.L.repo_url()
        assert result == "https://github.com/Winipedia/pyrig"

    def test_issues_url(self) -> None:
        """Test method."""
        result = RemoteVersionController.L.issues_url()
        assert result == "https://github.com/Winipedia/pyrig/issues"

    def test_releases_url(self) -> None:
        """Test method."""
        result = RemoteVersionController.L.releases_url()
        assert result == "https://github.com/Winipedia/pyrig/releases"

    def test_cicd_url(self) -> None:
        """Test method."""
        result = RemoteVersionController.L.cicd_url("health_check")
        assert (
            result
            == "https://github.com/Winipedia/pyrig/actions/workflows/health_check.yml"
        )

    def test_cicd_badge_url(self) -> None:
        """Test method."""
        result = RemoteVersionController.L.cicd_badge_url("health_check", "CI")
        assert (
            result
            == "https://img.shields.io/github/actions/workflow/status/Winipedia/pyrig/health_check.yml?label=CI&logo=github"
        )
