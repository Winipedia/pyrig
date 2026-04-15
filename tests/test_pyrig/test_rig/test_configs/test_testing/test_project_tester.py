"""module."""

from pathlib import Path

from pyrig.rig.configs.testing.project_tester import ProjectTesterConfigFile
from pyrig.rig.tests import conftest


class TestProjectTesterConfigFile:
    """Test class."""

    def test_parent_path(self) -> None:
        """Test method."""
        assert ProjectTesterConfigFile.I.parent_path() == Path("tests")

    def test_copy_module(self) -> None:
        """Test method."""
        assert ProjectTesterConfigFile.I.copy_module() is conftest

    def test_plugin_definition(self) -> None:
        """Test method."""
        assert (
            ProjectTesterConfigFile.I.plugin_definition()
            == f'pytest_plugins = ["{conftest.__name__}"]'
        )

    def test_stem(self) -> None:
        """Test method."""
        assert ProjectTesterConfigFile.I.stem() == "conftest"

    def test_is_correct(self) -> None:
        """Test method."""
        assert ProjectTesterConfigFile.I.is_correct()

    def test_lines(self) -> None:
        """Test method."""
        lines = ProjectTesterConfigFile.I.lines()
        content_str = "\n".join(lines)
        assert ProjectTesterConfigFile.I.plugin_definition() in content_str
