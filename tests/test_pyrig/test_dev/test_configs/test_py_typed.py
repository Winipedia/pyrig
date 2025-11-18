"""module."""

from collections.abc import Callable

import pytest

from pyrig.dev.configs.py_typed import PyTypedConfigFile
from pyrig.src.testing.assertions import assert_with_msg


@pytest.fixture
def my_test_py_typed_config_file(
    config_file_factory: Callable[[type[PyTypedConfigFile]], type[PyTypedConfigFile]],
) -> type[PyTypedConfigFile]:
    """Create a test py.typed config file class with tmp_path."""

    class MyTestPyTypedConfigFile(config_file_factory(PyTypedConfigFile)):  # type: ignore [misc]
        """Test py.typed config file with tmp_path override."""

    return MyTestPyTypedConfigFile


class TestPyTypedConfigFile:
    """Test class."""

    def test_get_parent_path(
        self, my_test_py_typed_config_file: type[PyTypedConfigFile]
    ) -> None:
        """Test method for get_parent_path."""
        parent_path = my_test_py_typed_config_file.get_parent_path()
        # The parent path should be the package name
        assert_with_msg(
            len(parent_path.as_posix()) > 0,
            "Expected parent_path to be non-empty",
        )
