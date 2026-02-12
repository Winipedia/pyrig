"""module."""

from pyrig.rig.tools.type_checker import TypeChecker


class TestTypeChecker:
    """Test class."""

    def test_group(self) -> None:
        """Test method."""
        result = TypeChecker.L.group()
        assert isinstance(result, str)
        assert result == "code-quality"

    def test_badge_urls(self) -> None:
        """Test method."""
        result = TypeChecker.L.badge_urls()
        assert isinstance(result, tuple)
        assert all(isinstance(url, str) for url in result)

    def test_name(self) -> None:
        """Test method."""
        result = TypeChecker.L.name()
        assert result == "ty"

    def test_check_args(self) -> None:
        """Test method."""
        result = TypeChecker.L.check_args()
        assert result == ("ty", "check")
