"""module."""

from pathlib import Path

from pyrig.rig.tools.security_checker import SecurityChecker


class TestSecurityChecker:
    """Test class."""

    def test_image_url(self) -> None:
        """Test method."""
        assert (
            SecurityChecker.I.image_url()
            == "https://img.shields.io/badge/security-bandit-yellow.svg"
        )

    def test_link_url(self) -> None:
        """Test method."""
        assert SecurityChecker.I.link_url() == "https://github.com/PyCQA/bandit"

    def test_target_paths(self) -> None:
        """Test method."""
        assert SecurityChecker.I.target_paths() == (
            Path("src/pyrig"),
            Path("tests"),
        )

    def test_target_posix_paths(self) -> None:
        """Test method."""
        assert tuple(SecurityChecker.I.target_posix_paths()) == tuple(
            path.as_posix() for path in SecurityChecker.I.target_paths()
        )

    def test_group(self) -> None:
        """Test method."""
        result = SecurityChecker.I.group()
        assert isinstance(result, str)
        assert result == "code-quality"

    def test_name(self) -> None:
        """Test method."""
        result = SecurityChecker.I.name()
        assert result == "bandit"

    def test_run_args(self) -> None:
        """Test method."""
        result = SecurityChecker.I.run_args()
        assert result == ("bandit",)

    def test_run_with_config_args(self) -> None:
        """Test method."""
        result = SecurityChecker.I.run_with_config_args()
        assert result == ("bandit", "-c", "pyproject.toml", "-r", "src/pyrig", "tests")
