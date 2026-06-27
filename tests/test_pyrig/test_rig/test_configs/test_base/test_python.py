"""module."""

from pyrig_fixtures.rig.configs.conftest import ConftestConfigFile
from pytest_mock import MockerFixture

from pyrig.rig.configs.base.python import PythonConfigFile
from pyrig.rig.configs.base.string_ import StringConfigFile
from pyrig.rig.configs.package_init import PackageInitConfigFile


class TestPythonConfigFile:
    """Test class."""

    def test_is_init_file(self) -> None:
        """Test method."""
        assert not ConftestConfigFile.I.is_init_file()
        assert PackageInitConfigFile.I.is_init_file()

    def test__dump(self, mocker: MockerFixture) -> None:
        """Test method."""
        module_before = ConftestConfigFile.I.module()
        dump_mock = mocker.patch.object(StringConfigFile, "_dump")
        ConftestConfigFile.I._dump([])  # noqa: SLF001
        dump_mock.assert_called_once()
        module_after = ConftestConfigFile.I.module()
        assert module_before is not module_after
        assert module_before.__name__ == module_after.__name__
        assert module_before.__file__ == module_after.__file__

    def test_module(self) -> None:
        """Test method."""
        assert ConftestConfigFile.I.module().__name__ == "tests.conftest"

        assert PackageInitConfigFile.I.module().__name__ == "pyrig"

    def test_extension(self) -> None:
        """Test method."""
        expected = "py"
        assert issubclass(ConftestConfigFile, PythonConfigFile)
        actual = ConftestConfigFile().extension()
        assert actual == expected, f"Expected {expected}, got {actual}"
