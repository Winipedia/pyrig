"""Test module."""

import pytest

from pyrig.core.exceptions.dependency_subclass.no_found import NoSubclassesFoundError
from pyrig.rig.configs.git.version_controller import VersionControllerIgnoreConfigFile


class TestNoSubclassesFoundError:
    """Test class."""

    def test___init__(self) -> None:
        """Test method."""
        with pytest.raises(NoSubclassesFoundError):
            raise NoSubclassesFoundError(subcls=VersionControllerIgnoreConfigFile)
