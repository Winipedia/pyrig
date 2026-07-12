"""module."""

from pyrig.rig.configs.base.shell import ShellConfigFile
from pyrig.rig.configs.version_control.remote.configure import (
    ConfigureRepositoryConfigFile,
)


class TestShellConfigFile:
    """Test class."""

    def test_extension(self) -> None:
        """Test method."""
        expected = "sh"
        assert issubclass(ConfigureRepositoryConfigFile, ShellConfigFile)
        actual = ConfigureRepositoryConfigFile().extension()
        assert actual == expected
