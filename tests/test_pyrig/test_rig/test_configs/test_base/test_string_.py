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

        def parent_path(self) -> Path:
            """Get the parent path."""
            return Path()

        def lines(self) -> list[str]:
            """Get the content string."""
            return ["Test content."]

        def extension(self) -> str:
            """Get the file extension."""
            return "txt"

    return MyTestStringConfigFile


class TestStringConfigFile:
    """Test class."""

    def test_merge_configs(
        self,
        my_test_string_config_file: type[StringConfigFile],
        tmp_path: Path,
    ) -> None:
        """Test method."""
        with chdir(tmp_path):
            my_test_string_config_file().validate()

            my_test_string_config_file().dump(["New content."])
            added_configs = my_test_string_config_file().merge_configs()
            assert added_configs == ["Test content.", "", "New content."]

    def test_make_string_from_lines(
        self, my_test_string_config_file: type[StringConfigFile]
    ) -> None:
        """Test method."""
        lines = ["Test content.", "Second line."]
        string = my_test_string_config_file().make_string_from_lines(lines)
        assert string == "Test content.\nSecond line."

    def test_should_override_content(
        self, my_test_string_config_file: type[StringConfigFile]
    ) -> None:
        """Test method."""
        assert not my_test_string_config_file().should_override_content(), (
            "Expected False"
        )

    def test_lines(self, my_test_string_config_file: type[StringConfigFile]) -> None:
        """Test method."""
        lines = my_test_string_config_file().lines()
        assert lines == ["Test content."]

    def test__load(self, my_test_string_config_file: type[StringConfigFile]) -> None:
        """Test method."""
        my_test_string_config_file().validate()
        loaded = my_test_string_config_file().load()
        assert loaded == ["Test content."]

    def test__dump(self, my_test_string_config_file: type[StringConfigFile]) -> None:
        """Test method."""
        my_test_string_config_file().validate()
        # Test successful dump
        content = ["New content."]
        my_test_string_config_file().dump(content)
        loaded = my_test_string_config_file().load()
        content = my_test_string_config_file().path().read_text()
        # assert has empyt line at the end
        assert content.endswith("\n")
        # load doesnt preserve the last "\n" as an "" in list bc of splitlines()
        assert loaded == ["New content."]

    def test__configs(self, my_test_string_config_file: type[StringConfigFile]) -> None:
        """Test method."""
        configs = my_test_string_config_file().configs()
        # empty line is added to the end of the file
        assert configs == ["Test content."]

    def test_is_correct(
        self, my_test_string_config_file: type[StringConfigFile]
    ) -> None:
        """Test method."""
        my_test_string_config_file().validate()
        is_correct = my_test_string_config_file().is_correct()
        assert is_correct, "Expected config to be correct after validation"

    def test_file_content(
        self, my_test_string_config_file: type[StringConfigFile]
    ) -> None:
        """Test method."""
        my_test_string_config_file().validate()
        file_content = my_test_string_config_file().file_content()
        assert file_content == "Test content.", "Expected 'Test content.'"
