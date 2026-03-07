"""module."""

import sys
from collections.abc import Callable
from contextlib import chdir
from pathlib import Path
from types import ModuleType

import pytest
from pytest_mock import MockFixture

from pyrig.rig import tests
from pyrig.rig.tests import mirror_test
from pyrig.rig.tests.mirror_test import MirrorTestConfigFile
from pyrig.rig.tools.project_tester import ProjectTester
from pyrig.src.modules.imports import import_package_with_dir_fallback
from pyrig.src.modules.module import create_module
from pyrig.src.modules.package import create_package


@pytest.fixture
def my_test_mirror_test_config_file(
    config_file_factory: Callable[
        [type[MirrorTestConfigFile]], type[MirrorTestConfigFile]
    ],
    tmp_path: Path,
) -> type[MirrorTestConfigFile]:
    """Create a test mirror test config file class with tmp_path."""
    with chdir(tmp_path):
        path = Path("mirror_test_module.py")
        # write a simple class with one method to the module
        path.write_text("""
class MirrorClass:
    def mirror_method(self):
        pass

def mirror_function():
    pass
""")
        mock_module = create_module(path)

    class MyTestMirrorTestConfigFile(config_file_factory(MirrorTestConfigFile)):  # ty:ignore[unsupported-base]
        """Test mirror test config file with tmp_path override."""

        def src_module(self) -> ModuleType:
            """Get the source module."""
            return mock_module

    return MyTestMirrorTestConfigFile


class TestMirrorTestConfigFile:
    """Test class."""

    def test_create_all_test_modules(self, mocker: MockFixture) -> None:
        """Test method."""
        mock_create_test_modules_for_package = mocker.patch.object(
            MirrorTestConfigFile,
            MirrorTestConfigFile.create_test_modules_for_package.__name__,
        )
        MirrorTestConfigFile.I.create_all_test_modules()
        mock_create_test_modules_for_package.assert_called_once()

    def test_create_test_modules_for_package(self, tmp_path: Path) -> None:
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

            package = import_package_with_dir_fallback(package_path)
            MirrorTestConfigFile.I.create_test_modules_for_package(package)

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
            # delete file after
            my_test_mirror_test_config_file().path().unlink()
            # remove module from cache to avoid interference with other tests
            sys.modules.pop(my_test_mirror_test_config_file().test_module_name(), None)

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

    def test_obj_from_test_obj(self) -> None:
        """Test method."""
        result = MirrorTestConfigFile.I.obj_from_test_obj(TestMirrorTestConfigFile)
        assert result.__name__ == MirrorTestConfigFile.__name__

    def test_test_obj_from_obj(self) -> None:
        """Test method."""
        result = MirrorTestConfigFile.I.test_obj_from_obj(MirrorTestConfigFile)
        assert result.__name__ == TestMirrorTestConfigFile.__name__

    def test_test_obj_importpath_from_obj(self) -> None:
        """Test method."""
        result = MirrorTestConfigFile.I.test_obj_importpath_from_obj(
            MirrorTestConfigFile
        )
        expected = "tests.test_pyrig.test_rig.test_tests.test_mirror_test.TestMirrorTestConfigFile"  # noqa: E501
        assert result == expected

    def test_obj_importpath_from_test_obj(self) -> None:
        """Test method."""
        result = MirrorTestConfigFile.I.obj_importpath_from_test_obj(
            TestMirrorTestConfigFile
        )
        assert result == "pyrig.rig.tests.mirror_test.MirrorTestConfigFile"

    def test_test_name_for_obj(self) -> None:
        """Test method."""
        result = MirrorTestConfigFile.I.test_name_for_obj(MirrorTestConfigFile)
        assert result == "TestMirrorTestConfigFile"

    def test_remove_test_prefix_from_test_name(self) -> None:
        """Test method."""
        test_name = "test_mirror_method"
        obj_name = MirrorTestConfigFile.I.remove_test_prefix_from_test_name(test_name)
        assert obj_name == "mirror_method"

    def test_test_prefix_for_obj(self) -> None:
        """Test method."""
        result = MirrorTestConfigFile.I.test_prefix_for_obj(
            MirrorTestConfigFile.I.test_prefix_for_obj
        )
        assert result == "test_"
        result = MirrorTestConfigFile.I.test_prefix_for_obj(MirrorTestConfigFile)
        assert result == "Test"

    def test_test_prefixes(self) -> None:
        """Test method."""
        result = MirrorTestConfigFile.I.test_prefixes()
        assert result == ("test_", "Test", "test_")

    def test_test_func_prefix(self) -> None:
        """Test method."""
        result = MirrorTestConfigFile.I.test_func_prefix()
        assert result == "test_"

    def test_test_class_prefix(self) -> None:
        """Test method."""
        result = MirrorTestConfigFile.I.test_class_prefix()
        assert result == "Test"

    def test_test_module_prefix(self) -> None:
        """Test method."""
        result = MirrorTestConfigFile.I.test_module_prefix()
        assert result == "test_"

    def test_merge_configs(
        self,
        my_test_mirror_test_config_file: type[MirrorTestConfigFile],
        tmp_path: Path,
    ) -> None:
        """Test method."""
        with chdir(tmp_path):
            create_module(my_test_mirror_test_config_file().test_path())
            assert (
                my_test_mirror_test_config_file().merge_configs()
                == my_test_mirror_test_config_file().configs()
            )

    def test_definition_package(self) -> None:
        """Test method."""
        assert MirrorTestConfigFile.I.definition_package() is tests

    def test_src_module(
        self, my_test_mirror_test_config_file: type[MirrorTestConfigFile]
    ) -> None:
        """Test method."""
        src_module = my_test_mirror_test_config_file().src_module()
        assert src_module.__name__ == "mirror_test_module"

    def test_filename(
        self, my_test_mirror_test_config_file: type[MirrorTestConfigFile]
    ) -> None:
        """Test method."""
        filename = my_test_mirror_test_config_file().filename()
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
            assert parent_path == Path(ProjectTester.I.tests_package_name())

    def test_lines(
        self,
        my_test_mirror_test_config_file: type[MirrorTestConfigFile],
        tmp_path: Path,
    ) -> None:
        """Test method."""
        with chdir(tmp_path):
            # create the file first to not trigger dump in content_str
            sys.modules.pop(my_test_mirror_test_config_file().test_module_name(), None)
            create_module(my_test_mirror_test_config_file().test_path())
            lines = my_test_mirror_test_config_file().lines()
            content = "\n".join(lines)
            assert "def test_mirror_method" in content
            assert "def test_mirror_function" in content
            assert "class TestMirrorClass" in content

    def test_should_override_content(self) -> None:
        """Test method."""
        assert MirrorTestConfigFile.I.should_override_content(), "Expected True"

    def test_is_correct(self) -> None:
        """Test method."""
        subclass = MirrorTestConfigFile.I.make_subclass_for_module(mirror_test)
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
        assert test_path == Path("tests/test_mirror_test_module.py")

    def test_test_module_name(
        self, my_test_mirror_test_config_file: type[MirrorTestConfigFile]
    ) -> None:
        """Test method."""
        test_module_name = my_test_mirror_test_config_file().test_module_name()
        assert test_module_name == "tests.test_mirror_test_module"

    def test_test_module_name_from_src_module(
        self, my_test_mirror_test_config_file: type[MirrorTestConfigFile]
    ) -> None:
        """Test method."""
        test_module_name = (
            my_test_mirror_test_config_file().test_module_name_from_src_module(
                my_test_mirror_test_config_file().src_module()
            )
        )
        assert test_module_name == "tests.test_mirror_test_module"

    def test_test_module(
        self,
        my_test_mirror_test_config_file: type[MirrorTestConfigFile],
        tmp_path: Path,
    ) -> None:
        """Test method."""
        with chdir(tmp_path):
            create_module(my_test_mirror_test_config_file().test_path())
            test_module = my_test_mirror_test_config_file().test_module()
            assert test_module.__name__ == "tests.test_mirror_test_module"

    def test_test_module_content_with_skeletons(
        self,
        my_test_mirror_test_config_file: type[MirrorTestConfigFile],
        tmp_path: Path,
    ) -> None:
        """Test method."""
        # create the file first
        with chdir(tmp_path):
            sys.modules.pop(my_test_mirror_test_config_file().test_module_name(), None)
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
    ) -> None:
        """Test method."""
        # create the file first
        with chdir(tmp_path):
            sys.modules.pop(my_test_mirror_test_config_file().test_module_name(), None)
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
    ) -> None:
        """Test method."""
        # create the file first
        with chdir(tmp_path):
            sys.modules.pop(my_test_mirror_test_config_file().test_module_name(), None)
            create_module(my_test_mirror_test_config_file().test_path())
            untested_func_names = tuple(
                my_test_mirror_test_config_file().untested_func_names()
            )
        assert len(untested_func_names) > 0

    def test_test_func_skeleton(self) -> None:
        """Test method."""
        skeleton = MirrorTestConfigFile.I.test_func_skeleton("test_func")
        assert "def test_func" in skeleton
        assert "NotImplementedError" in skeleton

    def test_test_module_content_with_class_skeletons(
        self,
        my_test_mirror_test_config_file: type[MirrorTestConfigFile],
        tmp_path: Path,
    ) -> None:
        """Test method."""
        # create the file first

        with chdir(tmp_path):
            sys.modules.pop(my_test_mirror_test_config_file().test_module_name(), None)
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
    ) -> None:
        """Test method."""
        # create the file first
        with chdir(tmp_path):
            sys.modules.pop(my_test_mirror_test_config_file().test_module_name(), None)
            create_module(my_test_mirror_test_config_file().test_path())
            untested_class_and_method_names = tuple(
                my_test_mirror_test_config_file().untested_class_and_method_names()
            )
        assert len(untested_class_and_method_names) > 0

    def test_test_class_skeleton(self) -> None:
        """Test method."""
        skeleton = MirrorTestConfigFile.I.test_class_skeleton("TestClass")
        assert "class TestClass" in skeleton

    def test_test_method_skeleton(self) -> None:
        """Test method."""
        skeleton = MirrorTestConfigFile.I.test_method_skeleton("test_method")
        assert "def test_method" in skeleton
        assert "NotImplementedError" in skeleton

    def test_make_subclasses_for_modules(self) -> None:
        """Test method."""
        subclasses = tuple(
            MirrorTestConfigFile.I.make_subclasses_for_modules([mirror_test])
        )
        assert len(subclasses) > 0

    def test_make_subclass_for_module(self) -> None:
        """Test method."""
        subclass = MirrorTestConfigFile.I.make_subclass_for_module(mirror_test)
        assert subclass().src_module() == mirror_test

    def test_create_test_modules(self) -> None:
        """Test method."""
        MirrorTestConfigFile.I.create_test_modules([mirror_test])
