"""module."""

from pyrig.rig.tools.version_control.remote.controller import (
    RemoteVersionController,
)


class TestRemoteVersionController:
    """Test class."""

    def test_repository(self) -> None:
        """Test method."""
        assert RemoteVersionController.I.repository() == "Winipedia/pyrig"

    def test_image_url(self) -> None:
        """Test method."""
        assert (
            RemoteVersionController.I.image_url()
            == "https://img.shields.io/github/stars/Winipedia/pyrig?style=social"
        )

    def test_link_url(self) -> None:
        """Test method."""
        assert (
            RemoteVersionController.I.link_url() == "https://github.com/Winipedia/pyrig"
        )

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

    def test_dev_dependencies(self) -> None:
        """Test method."""
        result = RemoteVersionController.I.dev_dependencies()
        assert result == ()

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

    def test_security_advisory_url(self) -> None:
        """Test method."""
        result = RemoteVersionController.I.security_advisory_url()
        assert result == "https://github.com/Winipedia/pyrig/security/advisories/new"

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

    def test_config_dir(self) -> None:
        """Test method."""
        assert RemoteVersionController.I.config_dir().as_posix() == ".github"

    def test_args(self) -> None:
        """Test method."""
        result = RemoteVersionController.I.args("release")
        assert tuple(result) == ("gh", "release")

    def test_release_args(self) -> None:
        """Test method."""
        result = RemoteVersionController.I.release_args("create")
        assert tuple(result) == ("gh", "release", "create")

    def test_create_release_args(self) -> None:
        """Test method."""
        result = RemoteVersionController.I.create_release_args(tag="1.2.3")
        assert tuple(result) == (
            "gh",
            "release",
            "create",
            "1.2.3",
            "--title=1.2.3",
            "--generate-notes",
        )

    def test_create_release_args_with_files(self) -> None:
        """Test method."""
        files = (f for f in ("dist/foo.whl", "dist/bar.tar.gz#Source"))
        result = RemoteVersionController.I.create_release_args(
            tag="1.2.3",
            files=files,
        )
        assert tuple(result) == (
            "gh",
            "release",
            "create",
            "1.2.3",
            "dist/foo.whl",
            "dist/bar.tar.gz#Source",
            "--title=1.2.3",
            "--generate-notes",
        )

    def test_api_args(self) -> None:
        """Test method."""
        result = RemoteVersionController.I.api_args(
            "--method=PATCH",
            endpoint='"repos/${repo}"',
        )
        assert tuple(result) == ("gh", "api", '"repos/${repo}"', "--method=PATCH")

    def test_api_method_args(self) -> None:
        """Test method."""
        result = RemoteVersionController.I.api_method_args(
            endpoint='"repos/${repo}"',
            method="PUT",
        )
        assert tuple(result) == ("gh", "api", '"repos/${repo}"', "--method=PUT")

    def test_api_method_input_args(self) -> None:
        """Test method."""
        result = RemoteVersionController.I.api_method_input_args(
            endpoint='"repos/${repo}"',
            method="PATCH",
            input_="-",
        )
        assert tuple(result) == (
            "gh",
            "api",
            '"repos/${repo}"',
            "--method=PATCH",
            "--input=-",
        )
