"""module."""

from collections.abc import Callable

import pytest

from pyrig.rig.configs.py_typed import PyTypedConfigFile


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

    def test_parent_path(
        self, my_test_py_typed_config_file: type[PyTypedConfigFile]
    ) -> None:
        """Test method."""
        parent_path = my_test_py_typed_config_file.parent_path()
        # The parent path should be the package name
        assert len(parent_path.as_posix()) > 0, "Expected parent_path to be non-empty"
