"""module."""

from collections.abc import Callable
from pathlib import Path

import pytest

from pyrig.rig.configs.testing.test_zero import ZeroTestConfigFile
from pyrig.rig.tests import test_zero


@pytest.fixture
def my_test_zero_test_config_file(
    config_file_factory: Callable[[type[ZeroTestConfigFile]], type[ZeroTestConfigFile]],
) -> type[ZeroTestConfigFile]:
    """Create a test zero test config file class with tmp_path."""

    class MyTestZeroTestConfigFile(config_file_factory(ZeroTestConfigFile)):  # ty: ignore[unsupported-base]
        """Test zero test config file with tmp_path override."""

    return MyTestZeroTestConfigFile


class TestZeroTestConfigFile:
    """Test class."""

    def test_parent_path(self) -> None:
        """Test method."""
        assert ZeroTestConfigFile().parent_path() == Path("tests")

    def test_copy_module(self) -> None:
        """Test method."""
        assert ZeroTestConfigFile().copy_module() is test_zero
