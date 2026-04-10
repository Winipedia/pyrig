"""Test module."""

import pytest

from pyrig.core.exceptions.dependency_subclass.multiple_found import (
    MultipleSubclassesFoundError,
)
from pyrig.rig.configs.base.config_file import ConfigFile


class TestMultipleSubclassesFoundError:
    """Test class."""

    def test___init__(self) -> None:
        """Test method."""
        with pytest.raises(MultipleSubclassesFoundError):
            raise MultipleSubclassesFoundError(subcls=ConfigFile)
