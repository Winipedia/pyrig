"""module."""

from pathlib import Path

from pyrig.dev.configs.docs.requirements import RequirementsConfigFile


class TestRequirementsConfigFile:
    """Test class."""

    def test_get_parent_path(self) -> None:
        """Test method."""
        parent_path = RequirementsConfigFile.get_parent_path()
        assert parent_path == Path("docs")

    def test_get_content_str(self) -> None:
        """Test method."""
        content_str = RequirementsConfigFile.get_content_str()
        assert isinstance(content_str, str)

    def test_get_dependencies(self) -> None:
        """Test method."""
        dependencies = RequirementsConfigFile.get_dependencies()
        assert isinstance(dependencies, list)

    def test_is_correct(self) -> None:
        """Test method."""
        assert RequirementsConfigFile.is_correct()
