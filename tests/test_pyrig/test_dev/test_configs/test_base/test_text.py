"""module."""

from collections.abc import Callable
from pathlib import Path

import pytest

from pyrig.dev.configs.base.text import TextConfigFile


@pytest.fixture
def my_test_text_config_file(
    config_file_factory: Callable[[type[TextConfigFile]], type[TextConfigFile]],
) -> type[TextConfigFile]:
    """Create a test text config file class with tmp_path."""

    class MyTestTextConfigFile(config_file_factory(TextConfigFile)):  # type: ignore [misc]
        """Test text config file with tmp_path override."""

        @classmethod
        def get_parent_path(cls) -> Path:
            """Get the parent path."""
            return Path()

        @classmethod
        def get_content_str(cls) -> str:
            """Get the content string."""
            return "Test content."

        @classmethod
        def get_file_extension(cls) -> str:
            """Get the file extension."""
            return "txt"

    return MyTestTextConfigFile


class TestTextConfigFile:
    """Test class."""

    def test_override_content(self) -> None:
        """Test method."""
        assert not TextConfigFile.override_content(), "Expected False"

    def test_get_content_str(
        self, my_test_text_config_file: type[TextConfigFile]
    ) -> None:
        """Test method for get_content_str."""
        content_str = my_test_text_config_file.get_content_str()
        assert content_str == "Test content.", "Expected 'Test content.'"

    def test__load(self, my_test_text_config_file: type[TextConfigFile]) -> None:
        """Test method for load."""
        my_test_text_config_file()
        loaded = my_test_text_config_file.load()
        assert loaded[TextConfigFile.CONTENT_KEY] == "Test content.", (
            "Expected 'Test content.'"
        )

    def test__dump(self, my_test_text_config_file: type[TextConfigFile]) -> None:
        """Test method for dump."""
        my_test_text_config_file()
        # Test successful dump
        content = "New content."
        my_test_text_config_file.dump({TextConfigFile.CONTENT_KEY: content})
        loaded = my_test_text_config_file.load()
        assert (
            loaded[TextConfigFile.CONTENT_KEY]
            == content + "\n" + my_test_text_config_file.get_content_str()
        )

    def test_get_configs(self, my_test_text_config_file: type[TextConfigFile]) -> None:
        """Test method for get_configs."""
        configs = my_test_text_config_file.get_configs()
        assert configs[TextConfigFile.CONTENT_KEY] == "Test content.", (
            "Expected 'Test content.'"
        )

    def test_is_correct(self, my_test_text_config_file: type[TextConfigFile]) -> None:
        """Test method for is_correct."""
        my_test_text_config_file()
        is_correct = my_test_text_config_file.is_correct()
        assert is_correct, "Expected config to be correct after initialization"

    def test_get_file_content(
        self, my_test_text_config_file: type[TextConfigFile]
    ) -> None:
        """Test method for get_file_content."""
        my_test_text_config_file()
        file_content = my_test_text_config_file.get_file_content()
        assert file_content == "Test content.", "Expected 'Test content.'"
