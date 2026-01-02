"""module."""

from pyrig.dev.management.type_checker import TypeChecker


class TestTypeChecker:
    """Test class."""

    def test_name(self) -> None:
        """Test method."""
        result = TypeChecker.name()
        assert result == "ty"

    def test_get_check_args(self) -> None:
        """Test method."""
        result = TypeChecker.get_check_args()
        assert result == ("ty", "check")
