"""Test module."""

import pytest

from pyrig.core.exceptions.config_file.dump import ConfigFileDumpForbiddenError
from pyrig.rig.configs.pyproject import PyprojectConfigFile


class TestConfigFileDumpForbiddenError:
    """Test class."""

    def test___init__(self) -> None:
        """Test method."""
        with pytest.raises(
            ConfigFileDumpForbiddenError,
            match=r"is forbidden because of test reason",
        ):
            raise ConfigFileDumpForbiddenError(
                PyprojectConfigFile.I, reason="of test reason"
            )
