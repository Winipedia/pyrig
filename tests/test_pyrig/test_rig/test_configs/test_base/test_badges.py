"""module."""

from contextlib import chdir
from pathlib import Path

from pytest_mock import MockerFixture

from pyrig.rig.configs.base.badges import BadgesConfigFile
from pyrig.rig.configs.license import LicenseConfigFile
from pyrig.rig.configs.pyproject import PyprojectConfigFile
from pyrig.rig.configs.readme import ReadmeConfigFile
from pyrig.rig.tools.pyrigger import Pyrigger
from pyrig.rig.tools.version_control.controller import VersionController


class TestBadgesConfigFile:
    """Test class."""

    def test_merge_configs(self, tmp_project_root_path: Path) -> None:
        """Test method."""
        assert issubclass(ReadmeConfigFile, BadgesConfigFile)

        # make sure repo owner is cached before entering non git folder tmp
        assert VersionController.I.repo_owner()
        assert VersionController.I.repo_owner()

        with chdir(tmp_project_root_path):
            LicenseConfigFile().validate()
            PyprojectConfigFile().validate()
            ReadmeConfigFile().validate()
            assert ReadmeConfigFile().is_correct()

            # change the description in readme to a false one
            false_description = "My False Description."
            correct_description = PyprojectConfigFile().project_description()
            content = ReadmeConfigFile().read_content()
            assert correct_description in content
            assert false_description not in content
            # we replace the actual description with a false one
            false_content = content.replace(correct_description, false_description)
            assert correct_description not in false_content
            assert false_description in false_content
            # we write the false content to the readme file
            ReadmeConfigFile().dump(ReadmeConfigFile().split_lines(false_content))
            # now the is correct method should correct the mistakes
            merged_lines = ReadmeConfigFile().merge_configs()
            merged_content = ReadmeConfigFile().join_lines(merged_lines)
            assert correct_description in merged_content
            assert false_description not in merged_content
            assert merged_content == content

            # dump configs and check file is correct
            ReadmeConfigFile().dump(ReadmeConfigFile().configs())
            assert ReadmeConfigFile().is_correct()
            assert ReadmeConfigFile().read_content() == content
            # remove one of the lines with a badge completely
            content_lines = ReadmeConfigFile().split_lines(content)
            badge_line = content_lines[3]
            assert badge_line.startswith("[![")
            content_lines.remove(badge_line)
            ReadmeConfigFile().dump(content_lines)
            assert not ReadmeConfigFile().is_correct()
            # merge configs
            merged_lines = ReadmeConfigFile().merge_configs()
            merged_content = ReadmeConfigFile().join_lines(merged_lines)
            assert merged_content == content
            # validate configs and check file is correct
            ReadmeConfigFile().validate()
            assert ReadmeConfigFile().is_correct()

        # clear the cache so other tests have the correct readme configs again
        ReadmeConfigFile.configs.cache_clear()

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

    def test_lines(self) -> None:
        """Test method."""
        lines = ReadmeConfigFile().lines()
        content_str = "\n".join(lines)
        assert isinstance(content_str, str)

    def test_badges(self) -> None:
        """Test method."""
        assert issubclass(ReadmeConfigFile, BadgesConfigFile)
        badges = ReadmeConfigFile().badges()
        assert isinstance(badges, dict)
