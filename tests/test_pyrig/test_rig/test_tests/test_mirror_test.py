"""module."""

import sys
from collections.abc import Callable
from contextlib import chdir
from pathlib import Path
from types import ModuleType

import pytest
from pytest_mock import MockerFixture

from pyrig.core.introspection.modules import reimport_module
from pyrig.core.introspection.packages import import_package_with_dir_fallback
from pyrig.core.introspection.paths import path_as_module_name
from pyrig.rig import tests
from pyrig.rig.tests import mirror_test
from pyrig.rig.tests.mirror_test import MirrorTestConfigFile

MIRROR_MODULE_PATH = Path("mirror_test_package/mirror_test_module.py")
MIRROR_MODULE_NAME = "mirror_test_package.mirror_test_module"
TESTS_MIRROR_MODULE_NAME = "tests.test_mirror_test_package.test_mirror_test_module"
TESTS_MIRROR_MODULE_PATH = Path(
    "tests/test_mirror_test_package/test_mirror_test_module.py"
)


@pytest.fixture
def my_test_mirror_test_config_file(
    config_file_factory: Callable[
        [type[MirrorTestConfigFile]], type[MirrorTestConfigFile]
    ],
    tmp_path: Path,
    create_module: Callable[[Path], ModuleType],
    create_package: Callable[[Path], ModuleType],
) -> type[MirrorTestConfigFile]:
    """Create a test mirror test config file class with tmp_path."""
    with chdir(tmp_path):
        cached_module = sys.modules.pop(MIRROR_MODULE_NAME, None)
        if cached_module is not None:
            # needed for the debugger for some reason
            Path(cached_module.__file__).unlink()  # ty:ignore[invalid-argument-type]

        cached_tests_module = sys.modules.pop(TESTS_MIRROR_MODULE_NAME, None)
        if cached_tests_module is not None:
            # needed for the debugger for some reason
            Path(cached_tests_module.__file__).unlink()  # ty:ignore[invalid-argument-type]

        module = create_module(MIRROR_MODULE_PATH)
        # create package for each parent dir of the module
        # needs to be imported bc import_module needs to work with them
        for parent in MIRROR_MODULE_PATH.parents:
            if parent == Path():
                break
            create_package(parent)
        # write a simple class with one method to the module
        MIRROR_MODULE_PATH.write_text("""
class MirrorClass:
    def mirror_method(self):
        pass

def mirror_function():
    pass
""")
        module = reimport_module(module)

    class MyTestMirrorTestConfigFile(config_file_factory(MirrorTestConfigFile)):  # ty:ignore[unsupported-base]
        """Test mirror test config file with tmp_path override."""

        def mirror_module(self) -> ModuleType:
            """Get the source module."""
            return module

    return MyTestMirrorTestConfigFile


class TestMirrorTestConfigFile:
    """Test class."""

    def test_test_func_name(
        self, my_test_mirror_test_config_file: type[MirrorTestConfigFile]
    ) -> None:
        """Test method."""
        assert (
            my_test_mirror_test_config_file().test_func_name(
                MirrorTestConfigFile.L.test_func_name
            )
            == self.test_test_func_name.__name__
        )

    def test_test_cls_name(
        self, my_test_mirror_test_config_file: type[MirrorTestConfigFile]
    ) -> None:
        """Test method."""
        assert (
            my_test_mirror_test_config_file().test_cls_name(MirrorTestConfigFile)
            == "TestMirrorTestConfigFile"
        )

    def test_test_module_docstring(
        self, my_test_mirror_test_config_file: type[MirrorTestConfigFile]
    ) -> None:
        """Test method."""
        docstring = my_test_mirror_test_config_file().test_module_docstring()
        assert isinstance(docstring, str)

    def test_create_all_test_modules(self, mocker: MockerFixture) -> None:
        """Test method."""
        mock_create_test_modules_for_package = mocker.patch.object(
            MirrorTestConfigFile,
            MirrorTestConfigFile.create_test_modules_for_package.__name__,
        )
        MirrorTestConfigFile.L.create_all_test_modules()
        mock_create_test_modules_for_package.assert_called_once()

    def test_create_test_modules_for_package(
        self,
        tmp_path: Path,
        create_module: Callable[[Path], ModuleType],
        create_package: Callable[[Path], ModuleType],
    ) -> None:
        """Test method."""
        with chdir(tmp_path):
            # Create a source package with a module
            package_path = Path("src_package")
            subpackage_path = package_path / "subpackage"
            mod1_path = package_path / "mod1.py"
            mod2_path = package_path / "mod2.py"
            sub_mod1_path = subpackage_path / "sub_mod1.py"
            sub_mod2_path = subpackage_path / "sub_mod2.py"

            # create the package and modules
            create_package(package_path)
            create_package(subpackage_path)
            create_module(mod1_path)
            create_module(mod2_path)
            create_module(sub_mod1_path)
            create_module(sub_mod2_path)

            assert mod1_path.exists()
            assert mod2_path.exists()
            assert sub_mod1_path.exists()

            package = import_package_with_dir_fallback(
                package_path, name=path_as_module_name(package_path)
            )
            MirrorTestConfigFile.L.create_test_modules_for_package(package)

            # assert the test modules were created
            test_mod1_path = Path("tests/test_src_package/test_mod1.py")
            test_mod2_path = Path("tests/test_src_package/test_mod2.py")
            test_sub_mod1_path = Path(
                "tests/test_src_package/test_subpackage/test_sub_mod1.py"
            )
            test_sub_mod2_path = Path(
                "tests/test_src_package/test_subpackage/test_sub_mod2.py"
            )
            assert test_mod1_path.exists()
            assert test_mod2_path.exists()
            assert test_sub_mod1_path.exists()
            assert test_sub_mod2_path.exists()

    def test__dump(
        self,
        my_test_mirror_test_config_file: type[MirrorTestConfigFile],
        tmp_path: Path,
    ) -> None:
        """Test method."""
        with chdir(tmp_path):
            my_test_mirror_test_config_file().validate()
            # assert teh file ends with empty line
            path = my_test_mirror_test_config_file().path()
            content = path.read_text()
            assert content.endswith("\n")
            # assert two lines between docstring and first class
            assert '"""\n\n\ndef test_mirror_function' in content
            assert "NotImplementedError\n\n\nclass TestMirrorClass:" in content

    def test_create_file(
        self, my_test_mirror_test_config_file: type[MirrorTestConfigFile]
    ) -> None:
        """Test method."""
        # create the file and check it exists
        my_test_mirror_test_config_file().create_file()
        test_module_name = my_test_mirror_test_config_file().test_module_name()
        assert test_module_name in sys.modules

    def test_test_module_content(
        self,
        my_test_mirror_test_config_file: type[MirrorTestConfigFile],
        tmp_path: Path,
    ) -> None:
        """Test method."""
        with chdir(tmp_path):
            config = my_test_mirror_test_config_file()
            config.create_file()  # ensure file exists for content generation
            assert config.test_module_content() == ""
            config.validate()
            content = config.test_module_content()
            assert "class TestMirrorClass" in content
            assert "def test_mirror_method" in content
            assert "def test_mirror_function" in content

    def test_test_func_prefix(
        self, my_test_mirror_test_config_file: type[MirrorTestConfigFile]
    ) -> None:
        """Test method."""
        result = my_test_mirror_test_config_file().test_func_prefix()
        assert result == "test_"

    def test_test_cls_prefix(
        self, my_test_mirror_test_config_file: type[MirrorTestConfigFile]
    ) -> None:
        """Test method."""
        result = my_test_mirror_test_config_file().test_cls_prefix()
        assert result == "Test"

    def test_merge_configs(
        self,
        my_test_mirror_test_config_file: type[MirrorTestConfigFile],
        tmp_path: Path,
        create_module: Callable[[Path], ModuleType],
    ) -> None:
        """Test method."""
        with chdir(tmp_path):
            create_module(my_test_mirror_test_config_file().test_path())
            assert (
                my_test_mirror_test_config_file().merge_configs()
                == my_test_mirror_test_config_file().configs()
            )

    def test_definition_package(
        self, my_test_mirror_test_config_file: type[MirrorTestConfigFile]
    ) -> None:
        """Test method."""
        assert my_test_mirror_test_config_file().definition_package() is tests

    def test_mirror_module(
        self, my_test_mirror_test_config_file: type[MirrorTestConfigFile]
    ) -> None:
        """Test method."""
        mirror_module = my_test_mirror_test_config_file().mirror_module()
        assert mirror_module.__name__ == MIRROR_MODULE_NAME

    def test_stem(
        self, my_test_mirror_test_config_file: type[MirrorTestConfigFile]
    ) -> None:
        """Test method."""
        filename = my_test_mirror_test_config_file().stem()
        assert filename == "test_mirror_test_module"

    def test_parent_path(
        self,
        my_test_mirror_test_config_file: type[MirrorTestConfigFile],
        tmp_path: Path,
    ) -> None:
        """Test method."""
        # tmp path bc factory of pattern in config_file_factory
        with chdir(tmp_path):
            parent_path = my_test_mirror_test_config_file().parent_path()
            assert parent_path == TESTS_MIRROR_MODULE_PATH.parent

    def test_lines(
        self,
        my_test_mirror_test_config_file: type[MirrorTestConfigFile],
        tmp_path: Path,
        create_module: Callable[[Path], ModuleType],
    ) -> None:
        """Test method."""
        with chdir(tmp_path):
            # create the file first to not trigger dump in content_str
            create_module(my_test_mirror_test_config_file().test_path())
            lines = my_test_mirror_test_config_file().lines()
            content = "\n".join(lines)
            assert "def test_mirror_method" in content
            assert "def test_mirror_function" in content
            assert "class TestMirrorClass" in content

    def test_should_override_content(
        self, my_test_mirror_test_config_file: type[MirrorTestConfigFile]
    ) -> None:
        """Test method."""
        assert my_test_mirror_test_config_file().should_override_content()

    def test_is_correct(self) -> None:
        """Test method."""
        subclass = MirrorTestConfigFile.L.generate_subclass(mirror_test)
        assert subclass().is_correct()

    def test_test_path(
        self,
        my_test_mirror_test_config_file: type[MirrorTestConfigFile],
        tmp_path: Path,
    ) -> None:
        """Test method."""
        test_path = my_test_mirror_test_config_file().test_path()
        assert test_path == my_test_mirror_test_config_file().path().relative_to(
            tmp_path
        )
        assert test_path == TESTS_MIRROR_MODULE_PATH

    def test_test_module_name(
        self, my_test_mirror_test_config_file: type[MirrorTestConfigFile]
    ) -> None:
        """Test method."""
        test_module_name = my_test_mirror_test_config_file().test_module_name()
        assert test_module_name == TESTS_MIRROR_MODULE_NAME

    def test_test_module(
        self,
        my_test_mirror_test_config_file: type[MirrorTestConfigFile],
        tmp_path: Path,
        create_module: Callable[[Path], ModuleType],
    ) -> None:
        """Test method."""
        with chdir(tmp_path):
            create_module(my_test_mirror_test_config_file().test_path())
            test_module = my_test_mirror_test_config_file().test_module()
            assert test_module.__name__ == TESTS_MIRROR_MODULE_NAME

    def test_test_module_content_with_skeletons(
        self,
        my_test_mirror_test_config_file: type[MirrorTestConfigFile],
        tmp_path: Path,
        create_module: Callable[[Path], ModuleType],
    ) -> None:
        """Test method."""
        # create the file first
        with chdir(tmp_path):
            create_module(my_test_mirror_test_config_file().test_path())
            content = (
                my_test_mirror_test_config_file().test_module_content_with_skeletons()
            )
            assert "def test_mirror_method" in content
            assert "def test_mirror_function" in content
            assert "class TestMirrorClass" in content

    def test_test_module_content_with_func_skeletons(
        self,
        my_test_mirror_test_config_file: type[MirrorTestConfigFile],
        tmp_path: Path,
        create_module: Callable[[Path], ModuleType],
    ) -> None:
        """Test method."""
        # create the file first
        with chdir(tmp_path):
            create_module(my_test_mirror_test_config_file().test_path())
            content = my_test_mirror_test_config_file().test_module_content_with_func_skeletons(  # noqa: E501
                my_test_mirror_test_config_file().test_module_content_with_skeletons()
            )
            assert "def test_mirror_method" in content
            assert "def test_mirror_function" in content
            assert "class TestMirrorClass" in content

    def test_untested_func_names(
        self,
        my_test_mirror_test_config_file: type[MirrorTestConfigFile],
        tmp_path: Path,
        create_module: Callable[[Path], ModuleType],
    ) -> None:
        """Test method."""
        # create the file first
        with chdir(tmp_path):
            create_module(my_test_mirror_test_config_file().test_path())
            untested_func_names = tuple(
                my_test_mirror_test_config_file().untested_func_names()
            )
        assert len(untested_func_names) > 0

    def test_test_func_skeleton(
        self, my_test_mirror_test_config_file: type[MirrorTestConfigFile]
    ) -> None:
        """Test method."""
        skeleton = my_test_mirror_test_config_file().test_func_skeleton("test_func")
        assert "def test_func" in skeleton
        assert "NotImplementedError" in skeleton

    def test_test_module_content_with_class_skeletons(
        self,
        my_test_mirror_test_config_file: type[MirrorTestConfigFile],
        tmp_path: Path,
        create_module: Callable[[Path], ModuleType],
    ) -> None:
        """Test method."""
        # create the file first

        with chdir(tmp_path):
            create_module(my_test_mirror_test_config_file().test_path())
            content = my_test_mirror_test_config_file().test_module_content_with_class_skeletons(  # noqa: E501
                my_test_mirror_test_config_file().test_module_content_with_skeletons()
            )
        assert "def test_mirror_method" in content
        assert "def test_mirror_function" in content
        assert "class TestMirrorClass" in content

    def test_untested_class_and_method_names(
        self,
        my_test_mirror_test_config_file: type[MirrorTestConfigFile],
        tmp_path: Path,
        create_module: Callable[[Path], ModuleType],
    ) -> None:
        """Test method."""
        # create the file first
        with chdir(tmp_path):
            create_module(my_test_mirror_test_config_file().test_path())
            untested_class_and_method_names = tuple(
                my_test_mirror_test_config_file().untested_class_and_method_names()
            )
        assert len(untested_class_and_method_names) > 0

    def test_test_class_skeleton(
        self, my_test_mirror_test_config_file: type[MirrorTestConfigFile]
    ) -> None:
        """Test method."""
        skeleton = my_test_mirror_test_config_file().test_class_skeleton("TestClass")
        assert "class TestClass" in skeleton

    def test_test_method_skeleton(
        self, my_test_mirror_test_config_file: type[MirrorTestConfigFile]
    ) -> None:
        """Test method."""
        skeleton = my_test_mirror_test_config_file().test_method_skeleton("test_method")
        assert "def test_method" in skeleton
        assert "NotImplementedError" in skeleton

    def test_generate_subclasses(self) -> None:
        """Test method."""
        subclasses = tuple(MirrorTestConfigFile.L.generate_subclasses([mirror_test]))
        assert len(subclasses) > 0

    def test_generate_subclass(self) -> None:
        """Test method."""
        subclass = MirrorTestConfigFile.L.generate_subclass(mirror_test)
        assert subclass().mirror_module() == mirror_test

    def test_create_test_modules(self) -> None:
        """Test method."""
        MirrorTestConfigFile.L.create_test_modules([mirror_test])
