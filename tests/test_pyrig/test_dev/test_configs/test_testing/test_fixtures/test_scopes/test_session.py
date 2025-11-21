"""module."""

from pyrig.dev.configs.testing.fixtures.scopes.session import SessionScopeConfigFile
from pyrig.dev.tests.fixtures.scopes import session


class TestSessionScopeConfigFile:
    """Test class."""

    def test_get_src_module(self) -> None:
        """Test method."""
        assert SessionScopeConfigFile.get_src_module() == session
