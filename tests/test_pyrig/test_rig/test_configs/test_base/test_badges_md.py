"""module."""

from pyrig.rig.configs.base.badges_md import BadgesMarkdownConfigFile
from pyrig.rig.configs.markdown.readme import ReadmeConfigFile
from pyrig.rig.configs.pyproject import PyprojectConfigFile


class TestBadgesMarkdownConfigFile:
    """Test class."""

    def test_replace_description(self) -> None:
        """Test that replace_description replaces a stale description."""
        expected_description = PyprojectConfigFile.L.project_description()
        old_description = "Old stale project description"
        content = f"# Project\n\n---\n\n> {old_description}\n\n---\n"
        result = BadgesMarkdownConfigFile.replace_description(content)
        assert f"> {expected_description}" in result
        assert old_description not in result

    def test_lines(self) -> None:
        """Test method."""
        lines = BadgesMarkdownConfigFile.lines()
        content_str = "\n".join(lines)
        assert isinstance(content_str, str)

    def test_is_correct(self) -> None:
        """Test method."""
        badges_md_config_cls = ReadmeConfigFile
        assert issubclass(badges_md_config_cls, BadgesMarkdownConfigFile)
        assert badges_md_config_cls.is_correct()

    def test_badges(self) -> None:
        """Test method."""
        badges = BadgesMarkdownConfigFile.badges()
        assert isinstance(badges, dict)
