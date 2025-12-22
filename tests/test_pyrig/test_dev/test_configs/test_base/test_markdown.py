"""module."""

from collections.abc import Callable
from pathlib import Path

import pytest

from pyrig.dev.configs.base.markdown import MarkdownConfigFile


@pytest.fixture
def my_test_markdown_config_file(
    config_file_factory: Callable[[type[MarkdownConfigFile]], type[MarkdownConfigFile]],
) -> type[MarkdownConfigFile]:
    """Create a test markdown config file class with tmp_path."""

    class MyTestMarkdownConfigFile(config_file_factory(MarkdownConfigFile)):  # type: ignore [misc]
        """Test markdown config file with tmp_path override."""

        @classmethod
        def get_parent_path(cls) -> Path:
            """Get the parent path."""
            return Path()

        @classmethod
        def get_content_str(cls) -> str:
            """Get the content string."""
            return "Test content."

    return MyTestMarkdownConfigFile


class TestMarkdownConfigFile:
    """Test class."""

    def test_get_file_extension(
        self, my_test_markdown_config_file: type[MarkdownConfigFile]
    ) -> None:
        """Test method for get_file_extension."""
        expected = "md"
        actual = my_test_markdown_config_file.get_file_extension()
        assert actual == expected, f"Expected {expected}, got {actual}"
