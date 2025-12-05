"""module."""

from pyrig.dev.configs.testing.fixtures_init import FixturesInitConfigFile
from pyrig.dev.tests import fixtures


class TestFixturesInitConfigFile:
    """Test class."""

    def test_get_src_module(self) -> None:
        """Test method."""
        assert FixturesInitConfigFile.get_src_module() == fixtures
