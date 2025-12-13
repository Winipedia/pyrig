"""module."""

from collections.abc import Callable

import pytest

from pyrig.dev.configs.testing.zero_test import ZeroTestConfigFile
from pyrig.src.testing.assertions import assert_with_msg


@pytest.fixture
def my_test_zero_test_config_file(
    config_file_factory: Callable[[type[ZeroTestConfigFile]], type[ZeroTestConfigFile]],
) -> type[ZeroTestConfigFile]:
    """Create a test zero test config file class with tmp_path."""

    class MyTestZeroTestConfigFile(config_file_factory(ZeroTestConfigFile)):  # type: ignore [misc]
        """Test zero test config file with tmp_path override."""

    return MyTestZeroTestConfigFile


class TestZeroTestConfigFile:
    """Test class."""

    def test_get_filename(
        self, my_test_zero_test_config_file: type[ZeroTestConfigFile]
    ) -> None:
        """Test method for get_filename."""
        filename = my_test_zero_test_config_file.get_filename()
        # ZeroTestConfigFile reverses the filename
        assert_with_msg(
            filename.startswith("test_"),
            f"Expected filename to start with 'test_', got {filename}",
        )

    def test_get_content_str(
        self, my_test_zero_test_config_file: type[ZeroTestConfigFile]
    ) -> None:
        """Test method for get_content_str."""
        content_str = my_test_zero_test_config_file.get_content_str()
        assert_with_msg(
            "test_zero" in content_str,
            "Expected 'test_zero' in content",
        )
