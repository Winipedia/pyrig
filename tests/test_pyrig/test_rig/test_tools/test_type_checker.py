"""module."""

from pyrig.rig.tools.type_checker import TypeChecker


class TestTypeChecker:
    """Test class."""

    def test_image_url(self) -> None:
        """Test method."""
        assert (
            TypeChecker.I.image_url()
            == "https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ty/main/assets/badge/v0.json"
        )

    def test_link_url(self) -> None:
        """Test method."""
        assert TypeChecker.I.link_url() == "https://github.com/astral-sh/ty"

    def test_group(self) -> None:
        """Test method."""
        result = TypeChecker.I.group()
        assert isinstance(result, str)
        assert result == "code-quality"

    def test_name(self) -> None:
        """Test method."""
        result = TypeChecker.I.name()
        assert result == "ty"

    def test_check_args(self) -> None:
        """Test method."""
        result = TypeChecker.I.check_args()
        assert result == ("ty", "check")
