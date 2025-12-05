"""module."""

from collections.abc import Callable
from pathlib import Path

import pytest

from pyrig.dev.configs.python.dot_experiment import DotExperimentConfigFile
from pyrig.src.testing.assertions import assert_with_msg


@pytest.fixture
def my_test_dot_experiment_config_file(
    config_file_factory: Callable[
        [type[DotExperimentConfigFile]], type[DotExperimentConfigFile]
    ],
) -> type[DotExperimentConfigFile]:
    """Create a test experiment config file class with tmp_path."""

    class MyTestDotExperimentConfigFile(config_file_factory(DotExperimentConfigFile)):  # type: ignore [misc]
        """Test experiment config file with tmp_path override."""

    return MyTestDotExperimentConfigFile


class TestDotExperimentConfigFile:
    """Test class."""

    def test_get_filename(
        self, my_test_dot_experiment_config_file: type[DotExperimentConfigFile]
    ) -> None:
        """Test method for get_filename."""
        expected = ".experiment"
        actual = my_test_dot_experiment_config_file.get_filename()
        assert_with_msg(actual == expected, f"Expected {expected}, got {actual}")

    def test_get_parent_path(
        self, my_test_dot_experiment_config_file: type[DotExperimentConfigFile]
    ) -> None:
        """Test method for get_parent_path."""
        expected = Path()
        actual = my_test_dot_experiment_config_file.get_parent_path()
        assert_with_msg(actual == expected, f"Expected {expected}, got {actual}")

    def test_get_content_str(
        self, my_test_dot_experiment_config_file: type[DotExperimentConfigFile]
    ) -> None:
        """Test method for get_content_str."""
        content_str = my_test_dot_experiment_config_file.get_content_str()
        assert_with_msg(
            "experimentation" in content_str,
            "Expected 'experimentation' in content",
        )
