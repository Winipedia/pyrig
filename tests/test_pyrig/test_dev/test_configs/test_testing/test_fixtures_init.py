"""module."""

from pyrig.dev.configs.testing.conftest import ConftestConfigFile
from pyrig.dev.configs.testing.fixtures_init import FixturesInitConfigFile
from pyrig.dev.tests import fixtures


class TestFixturesInitConfigFile:
    """Test class."""

    def test_get_priority(self) -> None:
        """Test method."""
        assert FixturesInitConfigFile.get_priority() > 0
        assert FixturesInitConfigFile.get_priority() > ConftestConfigFile.get_priority()

    def test_get_src_module(self) -> None:
        """Test method."""
        assert FixturesInitConfigFile.get_src_module() == fixtures
