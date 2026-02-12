"""module."""

from contextlib import chdir
from pathlib import Path

from pyrig.rig.configs.base.py_tests import PythonTestsConfigFile
from pyrig.rig.tests.mirror_test import MirrorTestConfigFile


class TestPythonTestsConfigFile:
    """Test class."""

    def test_parent_path(
        self,
        tmp_path: Path,
    ) -> None:
        """Test method."""
        with chdir(tmp_path):
            expected = Path(MirrorTestConfigFile.tests_package_name())
            actual = PythonTestsConfigFile.parent_path()
            assert actual == expected, f"Expected {expected}, got {actual}"
