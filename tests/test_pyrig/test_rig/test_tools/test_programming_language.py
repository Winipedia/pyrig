"""module."""

from pyrig.rig.tools import programming_language
from pyrig.rig.tools.base.tool import ToolGroup
from pyrig.rig.tools.programming_language import ProgrammingLanguage


class TestProgrammingLanguage:
    """Test class."""

    def test_standard_init_content(self) -> None:
        """Test method."""
        assert isinstance(ProgrammingLanguage().standard_init_content(), str)

    def test_no_bytecode_env_var(self) -> None:
        """Test method."""
        assert ProgrammingLanguage().no_bytecode_env_var() == "PYTHONDONTWRITEBYTECODE"

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


def test_module_docstring() -> None:
    """Test module docstring."""
    assert (
        programming_language.__doc__
        == """Programming language tool wrapper.

Wraps ProgrammingLanguage commands and information.
"""
    )
