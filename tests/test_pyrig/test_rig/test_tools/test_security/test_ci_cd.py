"""Test module."""

from pyrig.rig.tools.security.ci_cd import CICDSecurityChecker


class TestCICDSecurityChecker:
    """Test class."""

    def test_group(self) -> None:
        """Test method."""
        assert CICDSecurityChecker.I.group() == "code-quality"

    def test_image_url(self) -> None:
        """Test method."""
        assert (
            CICDSecurityChecker.I.image_url()
            == "https://img.shields.io/badge/CI/CD--security-zizmor-yellow"
        )

    def test_link_url(self) -> None:
        """Test method."""
        assert (
            CICDSecurityChecker.I.link_url() == "https://github.com/zizmorcore/zizmor"
        )

    def test_name(self) -> None:
        """Test method."""
        assert CICDSecurityChecker.I.name() == "zizmor"

    def test_check_args(self) -> None:
        """Test method."""
        assert CICDSecurityChecker.I.check_args() == ("zizmor",)

    def test_check_hook(self) -> None:
        """Test method."""
        hook = CICDSecurityChecker.I.check_hook()
        assert isinstance(hook, dict)
        assert hook["types"] == ["yaml"]

    def test_check_ci_cd(self) -> None:
        """Test method."""
        assert CICDSecurityChecker.I.check_ci_cd() == ("uv", "run", "zizmor")

    def test_ci_cd_files_pattern(self) -> None:
        """Test method."""
        assert (
            CICDSecurityChecker.I.ci_cd_files_pattern()
            == r"^\.github/workflows/|^\.github/dependabot\.|/action\."
        )
