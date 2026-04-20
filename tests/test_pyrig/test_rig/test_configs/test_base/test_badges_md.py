"""module."""

from pytest_mock import MockerFixture

from pyrig.rig.configs.base.badges_md import BadgesMarkdownConfigFile
from pyrig.rig.configs.markdown.readme import ReadmeConfigFile
from pyrig.rig.configs.pyproject import PyprojectConfigFile


class TestBadgesMarkdownConfigFile:
    """Test class."""

    def test_replace_badges(self, mocker: MockerFixture) -> None:
        """Test method."""
        # we take pyrigs actual content and change the some urls
        content = ReadmeConfigFile.I.join_lines(ReadmeConfigFile.I.lines())
        # we replace the actual badge urls with some dummy ones
        false_https = "https-false://"
        correct_https = "https://"
        false_content = content.replace(correct_https, false_https)
        assert correct_https not in false_content
        assert false_https in false_content
        corrected_content = ReadmeConfigFile().replace_badges(false_content)
        assert correct_https in corrected_content
        assert false_https not in corrected_content

        assert corrected_content == content

        # mock re.search to return None to test that the method handles it gracefully
        search_mock = mocker.patch("re.search", return_value=None)
        result = ReadmeConfigFile().replace_badges(false_content)
        search_mock.assert_called()
        assert result == false_content

    def test_replace_description(self) -> None:
        """Test that replace_description replaces a stale description."""
        expected_description = PyprojectConfigFile.I.project_description()
        old_description = "Old stale project description"
        content = f"# Project\n\n---\n\n> {old_description}\n\n---\n"
        result = ReadmeConfigFile().replace_description(content)
        assert f"> {expected_description}" in result
        assert old_description not in result

    def test_lines(self) -> None:
        """Test method."""
        lines = ReadmeConfigFile().lines()
        content_str = "\n".join(lines)
        assert isinstance(content_str, str)

    def test_is_correct(self) -> None:
        """Test method."""
        assert issubclass(ReadmeConfigFile, BadgesMarkdownConfigFile)

        assert ReadmeConfigFile.I.is_correct()

    def test_badges(self) -> None:
        """Test method."""
        assert issubclass(ReadmeConfigFile, BadgesMarkdownConfigFile), (
            "ReadmeConfigFile should inherit from BadgesMarkdownConfigFile"
        )
        badges = ReadmeConfigFile().badges()
        assert isinstance(badges, dict)
