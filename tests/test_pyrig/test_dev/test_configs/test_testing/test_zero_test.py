"""module."""

from collections.abc import Callable

import pytest
from pytest_mock import MockFixture

from pyrig.dev.configs.testing import zero_test
from pyrig.dev.configs.testing.zero_test import ZeroTestConfigFile
from pyrig.src.modules.module import make_obj_importpath
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
    """Test class for ZeroTestConfigFile."""

    def test_create_tests(self, mocker: MockFixture) -> None:
        """Test method for create_tests."""
        # mock run_subprocess to avoid actually running poetry run create-tests
        mock_run = mocker.patch(
            make_obj_importpath(zero_test) + ".run_subprocess",
            return_value=0,
        )
        ZeroTestConfigFile.create_tests()
        mock_run.assert_called_once()

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
