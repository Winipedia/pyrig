"""module."""

import pytest

from pyrig.rig.tools.base.file import FileTool


class TestFileTool:
    """Test class."""

    def test_types(self) -> None:
        """Test method."""
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            FileTool()
