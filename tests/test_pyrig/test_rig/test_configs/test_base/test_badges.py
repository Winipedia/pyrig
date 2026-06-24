"""module."""

from contextlib import chdir
from pathlib import Path

from pytest_mock import MockerFixture

from pyrig.rig.configs.base.badges import BadgesConfigFile
from pyrig.rig.configs.license import LicenseConfigFile
from pyrig.rig.configs.pyproject import PyprojectConfigFile
from pyrig.rig.configs.readme import ReadmeConfigFile
from pyrig.rig.tools.version_control.version_controller import VersionController


class TestBadgesConfigFile:
    """Test class."""

    def test_merge_configs(
        self, tmp_project_root_path: Path, mocker: MockerFixture
    ) -> None:
        """Test method."""
        assert issubclass(ReadmeConfigFile, BadgesConfigFile)

        mock_repo_owner = mocker.patch.object(
            VersionController, "repo_owner", return_value="FakeUser5"
        )

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

            # now dump smth completely false and check
            # that configs are inserted at beginning
            false_content = "Completely false content"
            ReadmeConfigFile().dump([false_content])
            merged_lines = ReadmeConfigFile().merge_configs()
            merged_content = ReadmeConfigFile().join_lines(merged_lines)
            assert merged_content.endswith(false_content)
            assert merged_content.startswith(
                ReadmeConfigFile().join_lines(ReadmeConfigFile().configs())
            )

            # dump configs and check file is correct
            ReadmeConfigFile().dump(ReadmeConfigFile().configs())
            assert ReadmeConfigFile().is_correct()
            assert ReadmeConfigFile().read_content() == content

        mock_repo_owner.assert_called()

    def test_replace_badges(self, mocker: MockerFixture) -> None:
        """Test method."""
        mock_repo_owner = mocker.patch.object(
            VersionController, "repo_owner", return_value="FakeUser6"
        )
        # we take pyrigs actual content and change the some urls
        content = ReadmeConfigFile().join_lines(ReadmeConfigFile().lines())
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

        mock_repo_owner.assert_called()

    def test_replace_description(self) -> None:
        """Test that replace_description replaces a stale description."""
        expected_description = PyprojectConfigFile().project_description()
        old_description = "Old stale project description"
        content = f"# Project\n\n---\n\n> {old_description}\n\n---\n"
        result = ReadmeConfigFile().replace_description(content)
        assert f"> {expected_description}" in result
        assert old_description not in result

    def test_lines(self, mocker: MockerFixture) -> None:
        """Test method."""
        mock_repo_owner = mocker.patch.object(
            VersionController, "repo_owner", return_value="FakeUser7"
        )
        lines = ReadmeConfigFile().lines()
        content_str = "\n".join(lines)
        assert isinstance(content_str, str)
        mock_repo_owner.assert_called()

    def test_badges(self, mocker: MockerFixture) -> None:
        """Test method."""
        assert issubclass(ReadmeConfigFile, BadgesConfigFile), (
            "ReadmeConfigFile should inherit from BadgesConfigFile"
        )
        mock_repo_owner = mocker.patch.object(
            VersionController, "repo_owner", return_value="FakeUser8"
        )
        badges = ReadmeConfigFile().badges()
        assert isinstance(badges, dict)
        mock_repo_owner.assert_called()
