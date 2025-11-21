"""module."""

from pyrig.dev.configs.testing.fixtures.fixture import FixtureConfigFile
from pyrig.dev.tests.fixtures import fixture


class TestFixtureConfigFile:
    """Test class."""

    def test_get_src_module(self) -> None:
        """Test method."""
        assert FixtureConfigFile.get_src_module() == fixture
