"""module."""

from collections.abc import Callable
from contextlib import chdir
from pathlib import Path

import pytest

from pyrig.rig.configs.base.string_ import StringConfigFile


@pytest.fixture
def my_test_string_config_file(
    config_file_factory: Callable[[type[StringConfigFile]], type[StringConfigFile]],
) -> type[StringConfigFile]:
    """Create a test text config file class with tmp_path."""

    class MyTestStringConfigFile(config_file_factory(StringConfigFile)):  # type: ignore [misc]
        """Test text config file with tmp_path override."""

        @classmethod
        def get_parent_path(cls) -> Path:
            """Get the parent path."""
            return Path()

        @classmethod
        def get_lines(cls) -> list[str]:
            """Get the content string."""
            return ["Test content."]

        @classmethod
        def get_file_extension(cls) -> str:
            """Get the file extension."""
            return "txt"

    return MyTestStringConfigFile


class TestStringConfigFile:
    """Test class."""

    def test_add_missing_configs(
        self,
        my_test_string_config_file: type[StringConfigFile],
        tmp_path: Path,
    ) -> None:
        """Test method."""
        with chdir(tmp_path):
            my_test_string_config_file()

            my_test_string_config_file.dump(["New content."])
            added_configs = my_test_string_config_file.add_missing_configs()
            assert added_configs == ["Test content.", "", "New content."]

    def test_make_string_from_lines(self) -> None:
        """Test method."""
        lines = ["Test content.", "Second line."]
        string = StringConfigFile.make_string_from_lines(lines)
        assert string == "Test content.\nSecond line."

    def test_override_content(self) -> None:
        """Test method."""
        assert not StringConfigFile.override_content(), "Expected False"

    def test_get_lines(
        self, my_test_string_config_file: type[StringConfigFile]
    ) -> None:
        """Test method."""
        lines = my_test_string_config_file.get_lines()
        assert lines == ["Test content."]

    def test__load(self, my_test_string_config_file: type[StringConfigFile]) -> None:
        """Test method."""
        my_test_string_config_file()
        loaded = my_test_string_config_file.load()
        assert loaded == ["Test content."]

    def test__dump(self, my_test_string_config_file: type[StringConfigFile]) -> None:
        """Test method."""
        my_test_string_config_file()
        # Test successful dump
        content = ["New content."]
        my_test_string_config_file.dump(content)
        loaded = my_test_string_config_file.load()
        content = my_test_string_config_file.get_path().read_text()
        # assert has empyt line at the end
        assert content.endswith("\n")
        # load doesnt preserve the last "\n" as an "" in list bc of splitlines()
        assert loaded == ["New content."]

    def test__get_configs(
        self, my_test_string_config_file: type[StringConfigFile]
    ) -> None:
        """Test method."""
        configs = my_test_string_config_file.get_configs()
        # empty line is added to the end of the file
        assert configs == ["Test content."]

    def test_is_correct(
        self, my_test_string_config_file: type[StringConfigFile]
    ) -> None:
        """Test method."""
        my_test_string_config_file()
        is_correct = my_test_string_config_file.is_correct()
        assert is_correct, "Expected config to be correct after initialization"

    def test_get_file_content(
        self, my_test_string_config_file: type[StringConfigFile]
    ) -> None:
        """Test method."""
        my_test_string_config_file()
        file_content = my_test_string_config_file.get_file_content()
        assert file_content == "Test content.", "Expected 'Test content.'"
