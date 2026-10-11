"""module."""

from collections import defaultdict

from pytest_mock import MockerFixture

from pyrig.rig.configs.base.badges import BadgesConfigFile
from pyrig.rig.configs.base.markdown import MarkdownConfigFile
from pyrig.rig.configs.pyproject import PyprojectConfigFile
from pyrig.rig.configs.readme import ReadmeConfigFile
from pyrig.rig.tools.base.tool import Group
from pyrig.rig.tools.pyrigger import Pyrigger


class TestBadgesConfigFile:
    """Test class."""

    def test_merge_configs(self, mocker: MockerFixture) -> None:
        """Test method."""
        config_file = ReadmeConfigFile()
        expected = config_file.configs()
        read_content_mock = mocker.patch.object(
            config_file,
            "read_content",
            return_value=config_file.join_lines(expected),
        )

        assert config_file.merge_configs() == expected
        read_content_mock.assert_called_once()

    def test_merge_configs_falls_back(self, mocker: MockerFixture) -> None:
        """Test method."""
        config_file = ReadmeConfigFile()
        read_content_mock = mocker.patch.object(
            config_file,
            "read_content",
            return_value="",
        )
        configs_is_subset_mock = mocker.patch.object(
            config_file,
            "configs_is_subset",
            return_value=False,
        )
        fallback_mock = mocker.patch.object(MarkdownConfigFile, "merge_configs")

        config_file.merge_configs()

        read_content_mock.assert_called_once()
        configs_is_subset_mock.assert_called_once()
        fallback_mock.assert_called_once()

    def test_replace_badges(self, mocker: MockerFixture) -> None:
        """Test method."""
        # we take pyrigs actual content and change the some urls
        content = ReadmeConfigFile().path().read_text(encoding="utf-8")
        correct_link = Pyrigger.I.link_url()
        # we replace the actual badge urls with some dummy ones
        false_link = "https-false://www.example.com"
        false_content = content.replace(correct_link, false_link)
        assert correct_link not in false_content
        assert false_link in false_content
        corrected_content = ReadmeConfigFile().replace_badges(false_content)
        assert correct_link in corrected_content
        assert false_link not in corrected_content

        assert corrected_content == content

        # mock re.search to return None to test that the method handles it gracefully
        search_mock = mocker.patch("re.search", return_value=None)
        result = ReadmeConfigFile().replace_badges(false_content)
        search_mock.assert_called()
        assert result == false_content

    def test_replace_description(self) -> None:
        """Test that replace_description replaces a stale description."""
        PyprojectConfigFile().load.cache_clear()
        correct_description = PyprojectConfigFile().project_description()
        false_description = "Old stale project description"
        content = f"# Project\n\n---\n\n> {false_description}\n\n---\n"
        result = ReadmeConfigFile().replace_description(content)
        assert f"> {correct_description}" in result
        assert false_description not in result

    def test_heading(self) -> None:
        """Test method."""
        heading = ReadmeConfigFile().heading()
        assert isinstance(heading, str)

    def test_content(self) -> None:
        """Test method."""
        content = ReadmeConfigFile().content()
        assert isinstance(content, str)

    def test_badges(self) -> None:
        """Test method."""
        assert issubclass(ReadmeConfigFile, BadgesConfigFile)
        badges = ReadmeConfigFile().badges()
        assert isinstance(badges, dict)

    def test_badges_content(self) -> None:
        """Test method."""
        content = ReadmeConfigFile().badges_content()
        assert isinstance(content, str)
        assert "<!--" in content
        assert "-->" in content

    def test_add_additional_badges(self) -> None:
        """Test method."""
        config_file = ReadmeConfigFile()
        additional_badges = config_file.additional_badges()
        grouped_badges: defaultdict[str, list[str]] = defaultdict(
            list,
            {
                Group.PROJECT_INFO: ["existing-info"],
                Group.PROJECT_STATUS: ["existing-status"],
            },
        )

        config_file.add_additional_badges(grouped_badges)

        assert grouped_badges[Group.PROJECT_INFO] == [
            "existing-info",
            additional_badges[0][0],
        ]
        assert grouped_badges[Group.PROJECT_STATUS] == [
            additional_badges[1][0],
            additional_badges[2][0],
            "existing-status",
        ]

    def test_add_badge(self) -> None:
        """Test method."""
        config_file = ReadmeConfigFile()
        grouped_badges: defaultdict[str, list[str]] = defaultdict(
            list,
            {Group.PROJECT_INFO: ["existing"]},
        )

        config_file.add_badge(
            grouped_badges,
            badge="appended",
            group=Group.PROJECT_INFO,
        )
        config_file.add_badge(
            grouped_badges,
            badge="inserted-first",
            group=Group.PROJECT_STATUS,
            index=0,
        )

        assert grouped_badges[Group.PROJECT_INFO] == ["existing", "appended"]
        assert grouped_badges[Group.PROJECT_STATUS] == ["inserted-first"]

    def test_additional_badges(self) -> None:
        """Test method."""
        badges = ReadmeConfigFile().additional_badges()

        assert [(group, index) for _, group, index in badges] == [
            (Group.PROJECT_INFO, None),
            (Group.PROJECT_STATUS, 0),
            (Group.PROJECT_STATUS, 1),
        ]
        assert all(badge.startswith("[![") for badge, _, _ in badges)
