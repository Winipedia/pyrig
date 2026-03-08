"""module."""

from pyrig.rig.tools.base.base import ToolGroup
from pyrig.rig.tools.programming_language import ProgrammingLanguage


class TestProgrammingLanguage:
    """Test class."""

    def test_dev_dependencies(self) -> None:
        """Test method."""
        assert ProgrammingLanguage().dev_dependencies() == ()

    def test_name(self) -> None:
        """Test method."""
        assert ProgrammingLanguage().name() == "python"

    def test_group(self) -> None:
        """Test method."""
        assert ProgrammingLanguage().group() == ToolGroup.PROJECT_INFO

    def test_badge_urls(self) -> None:
        """Test method."""
        badge_image_url, badge_link_url = ProgrammingLanguage().badge_urls()
        assert isinstance(badge_image_url, str)
        assert isinstance(badge_link_url, str)
