"""module."""

from collections.abc import Callable

import pytest
from pytest_mock import MockFixture

from pyrig.dev.configs.testing import conftest
from pyrig.dev.configs.testing.conftest import ConftestConfigFile
from pyrig.src.modules.module import make_obj_importpath
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
    """Test class for ConftestConfigFile."""

    def test_get_content_str(
        self, my_test_conftest_config_file: type[ConftestConfigFile]
    ) -> None:
        """Test method for get_content_str."""
        content_str = my_test_conftest_config_file.get_content_str()
        assert_with_msg(
            "pytest_plugins" in content_str,
            "Expected 'pytest_plugins' in conftest content",
        )

    def test_run_tests(
        self,
        my_test_conftest_config_file: type[ConftestConfigFile],
        mocker: MockFixture,
    ) -> None:
        """Test method for run_tests."""
        mock_run = mocker.patch(
            make_obj_importpath(conftest) + ".run_subprocess",
            return_value=0,
        )
        my_test_conftest_config_file.run_tests()
        mock_run.assert_called_once()
