"""module."""

import sys
from collections.abc import Callable
from contextlib import chdir
from pathlib import Path
from types import ModuleType

import pytest
from pyrig_runtime.core.introspection.inspection import obj_members

from pyrig.core.introspection.modules import reimport_module
from pyrig.rig import tests
from pyrig.rig.tests import mirror_test
from pyrig.rig.tests.mirror_test import MirrorTestConfigFile
from pyrig.rig.tools.linting.python import PythonLinter
from pyrig.rig.tools.testing.project import ProjectTester

MIRROR_MODULE_PATH = Path("mirror_test_package/mirror_test_module.py")
MIRROR_MODULE_NAME = "mirror_test_package.mirror_test_module"
TESTS_MIRROR_MODULE_NAME = "tests.test_mirror_test_package.test_mirror_test_module"
TESTS_MIRROR_MODULE_PATH = Path(
    "tests/test_mirror_test_package/test_mirror_test_module.py",
)


@pytest.fixture
def my_test_mirror_test_config_file(
    config_file_factory: Callable[
        [type[MirrorTestConfigFile]],
        type[MirrorTestConfigFile],
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

    class MyTestMirrorTestConfigFile(config_file_factory(MirrorTestConfigFile.L)):  # ty:ignore[unsupported-base]
        """Test mirror test config file with tmp_path override."""

        def mirror_module(self) -> ModuleType:
            """Get the source module."""
            return module

    return MyTestMirrorTestConfigFile


class TestMirrorTestConfigFile:
    """Test class for MirrorTestConfigFile."""

    def test_modules_and_members(
        self,
        my_test_mirror_test_config_file: type[MirrorTestConfigFile],
        create_module: Callable[[Path], ModuleType],
        tmp_path: Path,
    ) -> None:
        """Test method."""
        with chdir(tmp_path):
            create_module(my_test_mirror_test_config_file().test_path())
            module, test_module, module_members, test_module_members = (
                my_test_mirror_test_config_file().modules_and_members()
            )
            assert module.__name__ == MIRROR_MODULE_NAME
            assert test_module.__name__ == TESTS_MIRROR_MODULE_NAME
            assert len(module_members) > 0
            assert len(test_module_members) > 0

    def test_package_root(
        self,
        my_test_mirror_test_config_file: type[MirrorTestConfigFile],
    ) -> None:
        """Test method."""
        assert (
            my_test_mirror_test_config_file().package_root()
            == ProjectTester.I.package_root()
        )
        assert (
            my_test_mirror_test_config_file().source_root()
            == ProjectTester.I.source_root()
        )

    def test_test_module_prefix(
        self,
        my_test_mirror_test_config_file: type[MirrorTestConfigFile],
    ) -> None:
        """Test method."""
        assert my_test_mirror_test_config_file().test_module_prefix() == "test_"

    def test_validate(
        self,
        my_test_mirror_test_config_file: type[MirrorTestConfigFile],
        tmp_path: Path,
    ) -> None:
        """Test method."""
        with chdir(tmp_path):
            config = my_test_mirror_test_config_file()
            config.create_file()  # ensure file exists for content generation
            assert config.read_content() == '"""Test module."""\n'
            config.validate()
            assert (
                my_test_mirror_test_config_file().module().__name__
                == TESTS_MIRROR_MODULE_NAME
            )
            content = config.read_content()
            assert "class TestMirrorClass" in content
            assert "def test_mirror_method" in content
            assert "def test_mirror_function" in content
            assert "NotImplementedError" in content
            assert content.endswith("\n")
            # assert two lines between docstring and first class
            assert '"""\n\n\ndef test_mirror_function' in content
            assert "NotImplementedError\n\n\nclass TestMirrorClass:" in content

            PythonLinter.I.check_args(
                my_test_mirror_test_config_file().test_path().as_posix(),
            ).run()
            PythonLinter.I.format_args(
                my_test_mirror_test_config_file().test_path().as_posix(),
            ).run()

    def test_test_func_name(
        self,
        my_test_mirror_test_config_file: type[MirrorTestConfigFile],
    ) -> None:
        """Test method."""
        assert (
            my_test_mirror_test_config_file().test_func_name(
                MirrorTestConfigFile.L.test_func_name,
            )
            == self.test_test_func_name.__name__
        )

    def test_test_cls_name(
        self,
        my_test_mirror_test_config_file: type[MirrorTestConfigFile],
    ) -> None:
        """Test method."""
        assert (
            my_test_mirror_test_config_file().test_cls_name(MirrorTestConfigFile)
            == "TestMirrorTestConfigFile"
        )

    def test_test_module_docstring(
        self,
        my_test_mirror_test_config_file: type[MirrorTestConfigFile],
    ) -> None:
        """Test method."""
        docstring = my_test_mirror_test_config_file().test_module_docstring()
        assert isinstance(docstring, str)

    def test_create_file(
        self,
        my_test_mirror_test_config_file: type[MirrorTestConfigFile],
    ) -> None:
        """Test method."""
        # create the file and check it exists
        my_test_mirror_test_config_file().create_file()
        test_module_name = my_test_mirror_test_config_file().test_module_name()
        assert test_module_name in sys.modules

    def test_test_func_prefix(
        self,
        my_test_mirror_test_config_file: type[MirrorTestConfigFile],
    ) -> None:
        """Test method."""
        result = my_test_mirror_test_config_file().test_func_prefix()
        assert result == "test_"

    def test_test_cls_prefix(
        self,
        my_test_mirror_test_config_file: type[MirrorTestConfigFile],
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

    def test_discovery_module(
        self,
        my_test_mirror_test_config_file: type[MirrorTestConfigFile],
    ) -> None:
        """Test method."""
        assert my_test_mirror_test_config_file().discovery_module() is tests

    def test_mirror_module(
        self,
        my_test_mirror_test_config_file: type[MirrorTestConfigFile],
    ) -> None:
        """Test method."""
        mirror_module = my_test_mirror_test_config_file().mirror_module()
        assert mirror_module.__name__ == MIRROR_MODULE_NAME

    def test_stem(
        self,
        my_test_mirror_test_config_file: type[MirrorTestConfigFile],
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

    def test_content(
        self,
        my_test_mirror_test_config_file: type[MirrorTestConfigFile],
        tmp_path: Path,
        create_module: Callable[[Path], ModuleType],
    ) -> None:
        """Test method."""
        with chdir(tmp_path):
            # create the file first to not trigger dump in content
            create_module(my_test_mirror_test_config_file().test_path())
            content = my_test_mirror_test_config_file().content()
            assert "def test_mirror_method" in content
            assert "def test_mirror_function" in content
            assert "class TestMirrorClass" in content

    def test_is_correct(self) -> None:
        """Test method."""
        subclass = MirrorTestConfigFile.generate_subclass(mirror_test)
        assert subclass().is_correct()

    def test_test_path(
        self,
        my_test_mirror_test_config_file: type[MirrorTestConfigFile],
        tmp_path: Path,
    ) -> None:
        """Test method."""
        test_path = my_test_mirror_test_config_file().test_path()
        assert test_path == my_test_mirror_test_config_file().path().relative_to(
            tmp_path,
        )
        assert test_path == TESTS_MIRROR_MODULE_PATH

    def test_test_module_name(
        self,
        my_test_mirror_test_config_file: type[MirrorTestConfigFile],
    ) -> None:
        """Test method."""
        test_module_name = my_test_mirror_test_config_file().test_module_name()
        assert test_module_name == TESTS_MIRROR_MODULE_NAME

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
                my_test_mirror_test_config_file().test_module_content_with_skeletons(),
                *my_test_mirror_test_config_file().modules_and_members(),
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
                my_test_mirror_test_config_file().untested_func_names(
                    *my_test_mirror_test_config_file().modules_and_members(),
                ),
            )
        assert len(untested_func_names) > 0

    def test_test_func_skeleton(
        self,
        my_test_mirror_test_config_file: type[MirrorTestConfigFile],
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
                my_test_mirror_test_config_file().test_module_content_with_skeletons(),
                *my_test_mirror_test_config_file().modules_and_members(),
            )
        assert "def test_mirror_method" in content
        assert "def test_mirror_function" in content
        assert "class TestMirrorClass" in content

    def test_test_module_content_with_class_skeletons_decorated_class(
        self,
        tmp_path: Path,
        create_module: Callable[[Path], ModuleType],
        create_package: Callable[[Path], ModuleType],
    ) -> None:
        """Test method.

        Regression test: a test class decorated with `@pytest.mark.skip` (or
        anything else besides the exact auto-generated skeleton shape) must not
        cause a duplicate class definition to be appended, which would silently
        shadow the original class's existing tests. `skip` is used here (rather
        than e.g. `slow`) because it is a pytest builtin and needs no marker
        registration, unlike a custom marker.
        """
        source_path = Path("decorated_case/source_module.py")
        test_path = Path("decorated_case/test_source_module.py")
        with chdir(tmp_path):
            for path in (source_path, test_path):
                for parent in path.parents:
                    if parent == Path():
                        break
                    create_package(parent)
            source_module = create_module(source_path)
            test_module = create_module(test_path)

            source_path.write_text("""
class Foo:
    def bar(self):
        pass

    def baz(self):
        pass
""")
            test_path.write_text('''"""Test module."""

import pytest


@pytest.mark.skip(reason="example decorator for the regression test")
class TestFoo:
    """Test class."""

    def test_bar(self) -> None:
        """Test method."""
        assert True
''')
            source_module = reimport_module(source_module)
            test_module = reimport_module(test_module)

            config = MirrorTestConfigFile.generate_subclass(source_module)()
            result = config.test_module_content_with_class_skeletons(
                test_path.read_text(),
                module=source_module,
                test_module=test_module,
                module_members=tuple(obj_members(source_module)),
                test_module_members=tuple(obj_members(test_module)),
            )

        assert result.count("class TestFoo:") == 1
        assert "def test_bar" in result
        assert "def test_baz" in result
        compile(result, "<test>", "exec")

    def test_test_module_content_with_class_skeletons_multiple_classes(
        self,
        tmp_path: Path,
        create_module: Callable[[Path], ModuleType],
        create_package: Callable[[Path], ModuleType],
    ) -> None:
        """Test method.

        Two classes both needing new methods in the same pass must each get
        their own new method, without either landing in the wrong class.
        """
        source_path = Path("multi_class_case/source_module.py")
        test_path = Path("multi_class_case/test_source_module.py")
        with chdir(tmp_path):
            for path in (source_path, test_path):
                for parent in path.parents:
                    if parent == Path():
                        break
                    create_package(parent)
            source_module = create_module(source_path)
            test_module = create_module(test_path)

            source_path.write_text("""
class Alpha:
    def existing_a(self):
        pass

    def new_a(self):
        pass


class Beta:
    def existing_b(self):
        pass

    def new_b(self):
        pass
""")
            test_path.write_text('''"""Test module."""


class TestAlpha:
    """Test class."""

    def test_existing_a(self) -> None:
        """Test method."""
        assert True


class TestBeta:
    """Test class."""

    def test_existing_b(self) -> None:
        """Test method."""
        assert True
''')
            source_module = reimport_module(source_module)
            test_module = reimport_module(test_module)

            config = MirrorTestConfigFile.generate_subclass(source_module)()
            result = config.test_module_content_with_class_skeletons(
                test_path.read_text(),
                module=source_module,
                test_module=test_module,
                module_members=tuple(obj_members(source_module)),
                test_module_members=tuple(obj_members(test_module)),
            )

        assert result.count("class TestAlpha:") == 1
        assert result.count("class TestBeta:") == 1
        assert "def test_new_a" in result
        assert "def test_new_b" in result
        # the new method for Beta must not have landed inside Alpha's body
        assert "test_new_b" not in result.split("class TestBeta:")[0]
        # exactly the original two blank lines must separate the classes --
        # not three, which would mean the class's original trailing
        # whitespace got preserved *and* an extra one got added on top of it
        assert "raise NotImplementedError\n\n\nclass TestBeta:" in result
        assert "\n\n\n\nclass TestBeta:" not in result
        compile(result, "<test>", "exec")

    def test_test_module_content_with_class_skeletons_no_trailing_newline(
        self,
        tmp_path: Path,
        create_module: Callable[[Path], ModuleType],
        create_package: Callable[[Path], ModuleType],
    ) -> None:
        """Test method.

        Regression test: when the existing test class is the last thing in a
        file that itself has no trailing newline, `inspect.getsource()` still
        returns text ending in a newline, which must not prevent the new
        method from being inserted.
        """
        source_path = Path("no_trailing_newline_case/source_module.py")
        test_path = Path("no_trailing_newline_case/test_source_module.py")
        with chdir(tmp_path):
            for path in (source_path, test_path):
                for parent in path.parents:
                    if parent == Path():
                        break
                    create_package(parent)
            source_module = create_module(source_path)
            test_module = create_module(test_path)

            source_path.write_text("""
class Gamma:
    def existing(self):
        pass

    def new_one(self):
        pass
""")
            no_trailing_newline_content = '''"""Test module."""


class TestGamma:
    """Test class."""

    def test_existing(self) -> None:
        """Test method."""
        assert True'''
            test_path.write_text(no_trailing_newline_content)
            source_module = reimport_module(source_module)
            test_module = reimport_module(test_module)

            config = MirrorTestConfigFile.generate_subclass(source_module)()
            result = config.test_module_content_with_class_skeletons(
                no_trailing_newline_content,
                module=source_module,
                test_module=test_module,
                module_members=tuple(obj_members(source_module)),
                test_module_members=tuple(obj_members(test_module)),
            )

        assert result.count("class TestGamma:") == 1
        assert "def test_new_one" in result
        # a blank line must still separate the existing and new methods
        assert "assert True\n\n    def test_new_one" in result
        # the file's original (missing) trailing newline is preserved as-is,
        # not doubled into an extra blank line
        assert result.endswith("raise NotImplementedError")
        assert not result.endswith("\n\n")
        compile(result, "<test>", "exec")

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
                my_test_mirror_test_config_file().untested_class_and_method_names(
                    *my_test_mirror_test_config_file().modules_and_members(),
                ),
            )
        assert len(untested_class_and_method_names) > 0
        # the test module was just created empty, so no test class exists yet
        assert all(source is None for _, _, source in untested_class_and_method_names)

    def test_test_class_skeleton(
        self,
        my_test_mirror_test_config_file: type[MirrorTestConfigFile],
    ) -> None:
        """Test method."""
        skeleton = my_test_mirror_test_config_file().test_class_skeleton("TestClass")
        assert "class TestClass" in skeleton

    def test_test_method_skeleton(
        self,
        my_test_mirror_test_config_file: type[MirrorTestConfigFile],
    ) -> None:
        """Test method."""
        skeleton = my_test_mirror_test_config_file().test_method_skeleton("test_method")
        assert "def test_method" in skeleton
        assert "NotImplementedError" in skeleton

    def test_generate_subclass(self) -> None:
        """Test method."""
        subclass = MirrorTestConfigFile.L.generate_subclass(mirror_test)
        assert subclass().mirror_module() == mirror_test
