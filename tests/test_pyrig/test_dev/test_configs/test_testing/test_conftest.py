"""module."""

from collections.abc import Callable

import pytest

from pyrig.dev.configs.testing.conftest import ConftestConfigFile
from pyrig.src.testing.assertions import assert_with_msg


@pytest.fixture
def my_test_conftest_config_file(
    config_file_factory: Callable[[type[ConftestConfigFile]], type[ConftestConfigFile]],
) -> type[ConftestConfigFile]:
    """Create a test conftest config file class with tmp_path."""

    class MyTestConftestConfigFile(config_file_factory(ConftestConfigFile)):  # type: ignore [misc]
        """Test conftest config file with tmp_path override."""

    return MyTestConftestConfigFile


class TestConftestConfigFile:
    """Test class."""

    def test_is_correct(self) -> None:
        """Test method."""
        assert ConftestConfigFile().is_correct()

    def test_get_content_str(
        self, my_test_conftest_config_file: type[ConftestConfigFile]
    ) -> None:
        """Test method for get_content_str."""
        content_str = my_test_conftest_config_file.get_content_str()
        assert_with_msg(
            "pytest_plugins" in content_str,
            "Expected 'pytest_plugins' in conftest content",
        )
