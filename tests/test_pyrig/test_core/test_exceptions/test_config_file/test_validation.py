"""Test module."""

import re

import pytest

from pyrig.core.exceptions.base.config_file import ConfigFileError
from pyrig.core.exceptions.config_file.validation import ConfigFileValidationError
from pyrig.rig.configs.pyproject import PyprojectConfigFile


class TestConfigFileValidationError:
    """Test class."""

    def test___init__(self) -> None:
        """Test method."""
        with pytest.raises(
            ConfigFileValidationError,
            match=re.escape(f"Validation failed for {PyprojectConfigFile.I}"),
        ):
            raise ConfigFileValidationError(PyprojectConfigFile.I)

        assert issubclass(ConfigFileValidationError, ConfigFileError)
