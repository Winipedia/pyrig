"""module."""

from collections.abc import Callable
from pathlib import Path

import pytest

from pyrig.dev.configs.python.experiment import ExperimentConfigFile
from pyrig.src.testing.assertions import assert_with_msg


@pytest.fixture
def my_test_experiment_config_file(
    config_file_factory: Callable[
        [type[ExperimentConfigFile]], type[ExperimentConfigFile]
    ],
) -> type[ExperimentConfigFile]:
    """Create a test experiment config file class with tmp_path."""

    class MyTestExperimentConfigFile(config_file_factory(ExperimentConfigFile)):  # type: ignore [misc]
        """Test experiment config file with tmp_path override."""

    return MyTestExperimentConfigFile


class TestExperimentConfigFile:
    """Test class for ExperimentConfigFile."""

    def test_get_parent_path(
        self, my_test_experiment_config_file: type[ExperimentConfigFile]
    ) -> None:
        """Test method for get_parent_path."""
        expected = Path()
        actual = my_test_experiment_config_file.get_parent_path()
        assert_with_msg(actual == expected, f"Expected {expected}, got {actual}")

    def test_get_content_str(
        self, my_test_experiment_config_file: type[ExperimentConfigFile]
    ) -> None:
        """Test method for get_content_str."""
        content_str = my_test_experiment_config_file.get_content_str()
        assert_with_msg(
            "experimentation" in content_str,
            "Expected 'experimentation' in content",
        )
