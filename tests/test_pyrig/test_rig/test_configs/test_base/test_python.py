"""module."""

from pytest_mock import MockerFixture

from pyrig.rig.configs.base.python import PythonConfigFile
from pyrig.rig.configs.base.string_ import StringConfigFile
from pyrig.rig.configs.python.package_init import PackageInitConfigFile
from pyrig.rig.configs.testing.test_zero import ZeroTestConfigFile


class TestPythonConfigFile:
    """Test class."""

    def test__dump(self, mocker: MockerFixture) -> None:
        """Test method."""
        module_before = ZeroTestConfigFile.I.module()
        dump_mock = mocker.patch.object(StringConfigFile, "_dump")
        ZeroTestConfigFile.I._dump([])  # noqa: SLF001
        dump_mock.assert_called_once()
        module_after = ZeroTestConfigFile.I.module()
        assert module_before is not module_after
        assert module_before.__name__ == module_after.__name__
        assert module_before.__file__ == module_after.__file__

    def test_module(self) -> None:
        """Test method."""
        assert ZeroTestConfigFile.I.module().__name__ == "tests.test_zero"

        assert PackageInitConfigFile.I.module().__name__ == "pyrig"

    def test_extension(self) -> None:
        """Test method."""
        expected = "py"
        assert issubclass(ZeroTestConfigFile, PythonConfigFile)
        actual = ZeroTestConfigFile().extension()
        assert actual == expected, f"Expected {expected}, got {actual}"
