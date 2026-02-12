"""module."""

from pyrig.rig.configs.testing.conftest import ConftestConfigFile
from pyrig.rig.configs.testing.fixtures_init import FixturesInitConfigFile
from pyrig.rig.tests import fixtures


class TestFixturesInitConfigFile:
    """Test class."""

    def test_priority(self) -> None:
        """Test method."""
        assert FixturesInitConfigFile.priority() > 0
        assert FixturesInitConfigFile.priority() > ConftestConfigFile.priority()

    def test_src_module(self) -> None:
        """Test method."""
        assert FixturesInitConfigFile.src_module() == fixtures
