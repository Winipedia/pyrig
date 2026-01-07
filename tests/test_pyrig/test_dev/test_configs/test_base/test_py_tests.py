"""module."""

from contextlib import chdir
from pathlib import Path

from pyrig.dev.configs.base.py_tests import PythonTestsConfigFile
from pyrig.dev.tests.mirror_test import MirrorTestConfigFile


class TestPythonTestsConfigFile:
    """Test class."""

    def test_get_parent_path(
        self,
        tmp_path: Path,
    ) -> None:
        """Test method for get_parent_path."""
        with chdir(tmp_path):
            expected = Path(MirrorTestConfigFile.get_tests_package_name())
            actual = PythonTestsConfigFile.get_parent_path()
            assert actual == expected, f"Expected {expected}, got {actual}"
