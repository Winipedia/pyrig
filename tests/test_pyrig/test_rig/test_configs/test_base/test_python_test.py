"""module."""

from contextlib import chdir
from pathlib import Path

from pyrig.rig.configs.base.python_test import PythonTestConfigFile
from pyrig.rig.configs.testing.zero_test import ZeroTestConfigFile


class TestPythonTestConfigFile:
    """Test class."""

    def test_parent_path(
        self,
        tmp_path: Path,
    ) -> None:
        """Test method."""
        with chdir(tmp_path):
            expected = Path("tests")
            assert issubclass(ZeroTestConfigFile, PythonTestConfigFile), (
                "ZeroTestConfigFile should inherit from PythonTestConfigFile"
            )
            actual = ZeroTestConfigFile().parent_path()
            assert actual == expected, f"Expected {expected}, got {actual}"
