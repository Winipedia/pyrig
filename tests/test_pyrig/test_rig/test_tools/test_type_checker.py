"""module."""

from pyrig.rig.tools.type_checker import TypeChecker


class TestTypeChecker:
    """Test class."""

    def test_group(self) -> None:
        """Test method."""
        result = TypeChecker.I.group()
        assert isinstance(result, str)
        assert result == "code-quality"

    def test_badge_urls(self) -> None:
        """Test method."""
        result = TypeChecker.I.badge_urls()
        assert isinstance(result, tuple)
        assert all(isinstance(url, str) for url in result)

    def test_name(self) -> None:
        """Test method."""
        result = TypeChecker.I.name()
        assert result == "ty"

    def test_check_args(self) -> None:
        """Test method."""
        result = TypeChecker.I.check_args()
        assert result == ("ty", "check")
