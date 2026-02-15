"""module."""

from collections.abc import Callable

import pytest

from pyrig.rig.configs.testing.zero_test import ZeroTestConfigFile


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

    def test_filename(
        self, my_test_zero_test_config_file: type[ZeroTestConfigFile]
    ) -> None:
        """Test method."""
        filename = my_test_zero_test_config_file().filename()
        # ZeroTestConfigFile reverses the filename
        assert filename.startswith("test_"), (
            f"Expected filename to start with 'test_', got {filename}"
        )

    def test_lines(
        self, my_test_zero_test_config_file: type[ZeroTestConfigFile]
    ) -> None:
        """Test method."""
        lines = my_test_zero_test_config_file().lines()
        content_str = "\n".join(lines)
        assert "test_zero" in content_str, "Expected 'test_zero' in content"
