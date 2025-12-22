"""module."""

from collections.abc import Callable
from pathlib import Path

import pytest

from pyrig.dev.configs.base.badges_md import BadgesMarkdownConfigFile


@pytest.fixture
def my_test_badges_markdown_config_file(
    config_file_factory: Callable[
        [type[BadgesMarkdownConfigFile]], type[BadgesMarkdownConfigFile]
    ],
) -> type[BadgesMarkdownConfigFile]:
    """Create a test badges markdown config file class with tmp_path."""

    class MyTestBadgesMarkdownConfigFile(
        config_file_factory(BadgesMarkdownConfigFile)  # type: ignore [misc]
    ):
        """Test badges markdown config file."""

        @classmethod
        def get_parent_path(cls) -> Path:
            """Get the parent path."""
            return Path()

    return MyTestBadgesMarkdownConfigFile


class TestBadgesMarkdownConfigFile:
    """Test class."""

    def test_get_content_str(
        self, my_test_badges_markdown_config_file: type[BadgesMarkdownConfigFile]
    ) -> None:
        """Test method."""
        content_str = my_test_badges_markdown_config_file.get_content_str()
        assert isinstance(content_str, str)

    def test_is_correct(
        self, my_test_badges_markdown_config_file: type[BadgesMarkdownConfigFile]
    ) -> None:
        """Test method."""
        my_test_badges_markdown_config_file()
        is_correct = my_test_badges_markdown_config_file.is_correct()
        assert is_correct

    def test_get_badges(
        self, my_test_badges_markdown_config_file: type[BadgesMarkdownConfigFile]
    ) -> None:
        """Test method."""
        badges = my_test_badges_markdown_config_file.get_badges()
        assert isinstance(badges, dict)
