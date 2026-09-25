"""module."""

from pyrig.rig.tools.linting.python import PythonLinter
from pyrig.rig.tools.packages.manager import PackageManager
from pyrig.rig.tools.security.checker import SecurityChecker


class TestSecurityChecker:
    """Test class."""

    def test_group(self) -> None:
        """Test method."""
        result = SecurityChecker.I.group()
        assert isinstance(result, str)
        assert result == "code-quality"

    def test_image_url(self) -> None:
        """Test method."""
        assert (
            SecurityChecker.I.image_url()
            == "https://img.shields.io/badge/security-bandit-yellow.svg"
        )

    def test_link_url(self) -> None:
        """Test method."""
        assert SecurityChecker.I.link_url() == "https://github.com/PyCQA/bandit"

    def test_name(self) -> None:
        """Test method."""
        result = SecurityChecker.I.name()
        assert result == "bandit"

    def test_check_args(self) -> None:
        """Test method."""
        result = SecurityChecker.I.check_args("flag1", "flag2")
        assert result == ("bandit", "flag1", "flag2")

    def test_check_hook(self) -> None:
        """Test method."""
        # Bandit runs after Ruff's Python fixer
        hook = SecurityChecker.I.check_hook()
        check_hook = PythonLinter.I.check_hook()
        assert hook["priority"] > check_hook["priority"]
        assert hook["types"] == ["python"]

    def test_check_security(self) -> None:
        """Test method."""
        assert SecurityChecker.I.check_security() == PackageManager.I.run_args(
            *SecurityChecker.I.check_args(),
        )
