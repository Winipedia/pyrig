"""Test module."""

import pytest

from pyrig.core.exceptions.subprocesses.shell import ShellModeForbiddenError


class TestShellModeForbiddenError:
    """Test class."""

    def test___init__(self) -> None:
        """Test method."""
        with pytest.raises(ShellModeForbiddenError):
            raise ShellModeForbiddenError
