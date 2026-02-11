"""module."""

from pyrig.rig.tools.type_checker import TypeChecker


class TestTypeChecker:
    """Test class."""

    def test_get_group(self) -> None:
        """Test method."""
        result = TypeChecker.L.get_group()
        assert isinstance(result, str)
        assert result == "code-quality"

    def test_get_badge_urls(self) -> None:
        """Test method."""
        result = TypeChecker.L.get_badge_urls()
        assert isinstance(result, tuple)
        assert all(isinstance(url, str) for url in result)

    def test_name(self) -> None:
        """Test method."""
        result = TypeChecker.L.name()
        assert result == "ty"

    def test_get_check_args(self) -> None:
        """Test method."""
        result = TypeChecker.L.get_check_args()
        assert result == ("ty", "check")
