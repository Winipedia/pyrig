"""module."""

from contextlib import chdir
from pathlib import Path

from pyrig.rig.configs.base.py_tests import PythonTestsConfigFile
from pyrig.rig.configs.testing.zero_test import ZeroTestConfigFile


class TestPythonTestsConfigFile:
    """Test class."""

    def test_parent_path(
        self,
        tmp_path: Path,
    ) -> None:
        """Test method."""
        with chdir(tmp_path):
            expected = Path("tests")
            assert issubclass(ZeroTestConfigFile, PythonTestsConfigFile), (
                "ZeroTestConfigFile should inherit from PythonTestsConfigFile"
            )
            actual = ZeroTestConfigFile().parent_path()
            assert actual == expected, f"Expected {expected}, got {actual}"
