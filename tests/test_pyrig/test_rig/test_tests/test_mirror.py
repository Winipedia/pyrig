"""Test module."""

import ast
from contextlib import chdir
from pathlib import Path

import pytest

from pyrig.core.introspection.ast import cls_definitions
from pyrig.rig import tests
from pyrig.rig.tests.mirror import MirrorTestConfigFile
from pyrig.rig.tools.linting.python import PythonLinter
from pyrig.rig.tools.testing.project import ProjectTester

SOURCE_PATH = Path("src/example_module.py")
TEST_PATH = Path("tests/test_example_module.py")
SOURCE_CONTENT = '''"""Example module."""

def func() -> None:
    pass

async def async_func() -> None:
    pass

class Example:
    def method(self) -> None:
        pass

    async def async_method(self) -> None:
        pass
'''


@pytest.fixture
def mirror_config(
    tmp_path: Path,
) -> tuple[type[MirrorTestConfigFile], Path]:
    """Test fixture."""
    source_path = tmp_path / SOURCE_PATH
    source_path.parent.mkdir(parents=True)
    source_path.write_text(SOURCE_CONTENT)

    class ExampleMirrorConfig(MirrorTestConfigFile):
        def mirror_file(self) -> Path:
            return SOURCE_PATH

        def package_root(self) -> Path:
            return Path("tests")

    return ExampleMirrorConfig, tmp_path


class TestMirrorTestConfigFile:
    """Test class."""

    def test_mirror_file(
        self,
        mirror_config: tuple[type[MirrorTestConfigFile], Path],
    ) -> None:
        """Test method."""
        config_cls, _ = mirror_config
        assert config_cls().mirror_file() == SOURCE_PATH

    def test_mirror_tree(
        self,
        mirror_config: tuple[type[MirrorTestConfigFile], Path],
    ) -> None:
        """Test method."""
        config_cls, tmp_path = mirror_config
        with chdir(tmp_path):
            config = config_cls()
            mirror_tree = config.mirror_tree()
            assert isinstance(mirror_tree, ast.Module)
            assert ast.dump(mirror_tree) == ast.dump(ast.parse(SOURCE_CONTENT))

            Path(SOURCE_PATH).write_text("value = 1\n")
            assert ast.dump(config.mirror_tree()) == ast.dump(ast.parse("value = 1\n"))

    def test_test_tree(
        self,
        mirror_config: tuple[type[MirrorTestConfigFile], Path],
    ) -> None:
        """Test method."""
        config_cls, tmp_path = mirror_config
        with chdir(tmp_path):
            config = config_cls()
            config.path().parent.mkdir(parents=True)
            test_content = '"""Test module."""\n\nvalue = 1\n'
            config.write_content(test_content)

            test_tree = config.test_tree()
            assert isinstance(test_tree, ast.Module)
            assert ast.dump(test_tree) == ast.dump(ast.parse(test_content))

            config.write_content("value = 2\n")
            assert ast.dump(config.test_tree()) == ast.dump(ast.parse("value = 2\n"))

    def test_merge_key(self) -> None:
        """Test method."""
        assert MirrorTestConfigFile.merge_key() == "MirrorTestConfigFile"

    def test_validate(
        self,
        mirror_config: tuple[type[MirrorTestConfigFile], Path],
    ) -> None:
        """Test method."""
        config_cls, tmp_path = mirror_config
        with chdir(tmp_path):
            config = config_cls()
            assert not config.path().exists()
            assert config.validate() is False
            assert config.path().exists()
            assert config.is_correct()
            assert config.validate() is True
            PythonLinter.I.check_args(config.path().as_posix()).run()
            PythonLinter.I.format_args(config.path().as_posix()).run()

    def test_create_file(
        self,
        mirror_config: tuple[type[MirrorTestConfigFile], Path],
    ) -> None:
        """Test method."""
        config_cls, tmp_path = mirror_config
        with chdir(tmp_path):
            config = config_cls()
            config.create_file()
            assert config.path().read_text() == '"""Test module."""\n'

    def test_is_correct(
        self,
        mirror_config: tuple[type[MirrorTestConfigFile], Path],
    ) -> None:
        """Test method."""
        config_cls, tmp_path = mirror_config
        with chdir(tmp_path):
            config = config_cls()
            config.path().parent.mkdir(parents=True)
            config.write_content(
                '''"""Test module."""

def test_func() -> None:
    pass

def test_async_func() -> None:
    pass

class TestExample:
    def test_method(self) -> None:
        pass

    def test_async_method(self) -> None:
        pass
''',
            )
            assert config.is_correct()

            config.write_content('"""Test module."""\n')
            assert not config.is_correct()

    def test_content(
        self,
        mirror_config: tuple[type[MirrorTestConfigFile], Path],
    ) -> None:
        """Test method."""
        config_cls, tmp_path = mirror_config
        with chdir(tmp_path):
            config = config_cls()
            config.path().parent.mkdir(parents=True)
            existing = '''"""Test module."""

def test_func() -> None:
    assert True

class TestExample:
    def test_method(self) -> None:
        assert True
'''
            config.write_content(existing)

            content = config.content()
            assert content.count("def test_func") == 1
            assert content.count("def test_method") == 1
            assert "def test_async_func" in content
            assert "def test_async_method" in content
            assert "raise NotImplementedError" in content

    def test_merge_configs(
        self,
        mirror_config: tuple[type[MirrorTestConfigFile], Path],
    ) -> None:
        """Test method."""
        config_cls, tmp_path = mirror_config
        with chdir(tmp_path):
            config = config_cls()
            config.path().parent.mkdir(parents=True)
            config.write_content('"""Test module."""\n')
            assert config.merge_configs() == config.configs()

    def test_package_root(self) -> None:
        """Test method."""
        config_cls = MirrorTestConfigFile.generate_subclass(
            Path("src/pyrig/rig/tests/mirror.py"),
        )
        assert config_cls().package_root() == ProjectTester.I.package_root()

    def test_parent_path(
        self,
        mirror_config: tuple[type[MirrorTestConfigFile], Path],
    ) -> None:
        """Test method."""
        config_cls, tmp_path = mirror_config
        with chdir(tmp_path):
            assert config_cls().parent_path() == TEST_PATH.parent

    def test_stem(
        self,
        mirror_config: tuple[type[MirrorTestConfigFile], Path],
    ) -> None:
        """Test method."""
        config_cls, tmp_path = mirror_config
        with chdir(tmp_path):
            assert config_cls().stem() == "test_example_module"

    def test_discovery_module(self) -> None:
        """Test method."""
        assert MirrorTestConfigFile.discovery_module() is tests

    def test_generate_subclass(self) -> None:
        """Test method."""
        source_path = Path("src/pyrig/rig/tests/mirror.py")
        subclass = MirrorTestConfigFile.generate_subclass(source_path)
        config = subclass()
        assert isinstance(config, MirrorTestConfigFile)
        assert config.mirror_file() == source_path
        assert subclass.__name__ == "MirrorMirrorTestConfigFile"
        assert subclass.merge_key() == "MirrorTestConfigFile"

    def test_test_path(
        self,
        mirror_config: tuple[type[MirrorTestConfigFile], Path],
    ) -> None:
        """Test method."""
        config_cls, tmp_path = mirror_config
        with chdir(tmp_path):
            assert config_cls().test_path() == TEST_PATH

    def test_test_file_content_with_skeletons(
        self,
        mirror_config: tuple[type[MirrorTestConfigFile], Path],
    ) -> None:
        """Test method."""
        config_cls, tmp_path = mirror_config
        with chdir(tmp_path):
            config = config_cls()
            config.path().parent.mkdir(parents=True)
            config.write_content('"""Test module."""\n')
            content = config.test_file_content_with_skeletons()
            assert "def test_func" in content
            assert "def test_async_func" in content
            assert "class TestExample" in content
            assert "def test_method(self)" in content
            assert "def test_async_method(self)" in content

    def test_test_file_content_with_func_skeletons(
        self,
        mirror_config: tuple[type[MirrorTestConfigFile], Path],
    ) -> None:
        """Test method."""
        config_cls, tmp_path = mirror_config
        with chdir(tmp_path):
            config = config_cls()
            content = config.test_file_content_with_func_skeletons(
                '"""Test module."""\n',
                config.mirror_tree(),
                ast.parse("def test_func(): pass\n"),
            )
            assert content.count("def test_func") == 0
            assert "def test_async_func" in content

    def test_untested_func_names(
        self,
        mirror_config: tuple[type[MirrorTestConfigFile], Path],
    ) -> None:
        """Test method."""
        config_cls, tmp_path = mirror_config
        with chdir(tmp_path):
            config = config_cls()
            names = tuple(
                config.untested_func_names(config.mirror_tree(), ast.parse("")),
            )
            assert names == ("test_func", "test_async_func")

    def test_test_func_skeleton(
        self,
        mirror_config: tuple[type[MirrorTestConfigFile], Path],
    ) -> None:
        """Test method."""
        config_cls, _ = mirror_config
        skeleton = config_cls().test_func_skeleton("test_func")
        assert "def test_func" in skeleton
        assert "raise NotImplementedError" in skeleton

    def test_test_file_content_with_cls_skeletons(
        self,
        mirror_config: tuple[type[MirrorTestConfigFile], Path],
    ) -> None:
        """Test method."""
        config_cls, tmp_path = mirror_config
        with chdir(tmp_path):
            config = config_cls()
            content = config.test_file_content_with_cls_skeletons(
                '"""Test module."""\n',
                config.mirror_tree(),
                ast.parse(""),
            )
            assert "class TestExample" in content
            assert "def test_method(self)" in content
            assert "def test_async_method(self)" in content

            existing = '''"""Test module."""

@staticmethod
class TestExample:
    def test_method(self) -> None:
        assert True
'''
            config.path().parent.mkdir(parents=True)
            config.write_content(existing)
            content = config.test_file_content_with_cls_skeletons(
                existing,
                config.mirror_tree(),
                config.test_tree(),
            )
            assert content.count("class TestExample:") == 1
            assert "def test_async_method(self)" in content
            compile(content, "<generated-test>", "exec")

            Path(SOURCE_PATH).write_text(
                """\
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
""",
            )
            multiple_classes = '''"""Test module."""

class TestAlpha:
    def test_existing_a(self) -> None:
        pass

class TestBeta:
    def test_existing_b(self) -> None:
        pass
'''
            config.write_content(multiple_classes)
            content = config.test_file_content_with_cls_skeletons(
                multiple_classes,
                config.mirror_tree(),
                config.test_tree(),
            )
            assert "def test_new_a(self)" in content
            assert "def test_new_b(self)" in content
            assert "test_new_b" not in content.split("class TestBeta:")[0]
            assert content.count("class TestAlpha:") == 1
            assert content.count("class TestBeta:") == 1
            compile(content, "<generated-test>", "exec")

            Path(SOURCE_PATH).write_text(
                """\
class Gamma:
    def existing(self):
        pass

    def new_one(self):
        pass
""",
            )
            no_trailing_newline = '''"""Test module."""

class TestGamma:
    def test_existing(self) -> None:
        pass'''
            config.write_content(no_trailing_newline)
            content = config.test_file_content_with_cls_skeletons(
                no_trailing_newline,
                config.mirror_tree(),
                config.test_tree(),
            )
            assert "def test_new_one(self)" in content
            assert content.endswith("raise NotImplementedError")
            assert not content.endswith("\n\n")
            compile(content, "<generated-test>", "exec")

    def test_untested_cls_and_method_names(
        self,
        mirror_config: tuple[type[MirrorTestConfigFile], Path],
    ) -> None:
        """Test method."""
        config_cls, tmp_path = mirror_config
        with chdir(tmp_path):
            config = config_cls()
            config.path().parent.mkdir(parents=True)
            config.write_content(
                '''"""Test module."""

class TestExample:
    def test_method(self) -> None:
        pass
''',
            )
            names = tuple(
                config.untested_cls_and_method_names(
                    config.mirror_tree(),
                    config.test_tree(),
                ),
            )
            assert len(names) == 1
            cls_name, method_names, source = names[0]
            assert cls_name == "TestExample"
            assert tuple(method_names) == ("test_async_method",)
            assert source is not None

    def test_test_cls_skeleton(
        self,
        mirror_config: tuple[type[MirrorTestConfigFile], Path],
    ) -> None:
        """Test method."""
        config_cls, _ = mirror_config
        skeleton = config_cls().test_cls_skeleton("TestExample")
        assert "class TestExample" in skeleton

    def test_test_method_skeleton(
        self,
        mirror_config: tuple[type[MirrorTestConfigFile], Path],
    ) -> None:
        """Test method."""
        config_cls, _ = mirror_config
        skeleton = config_cls().test_method_skeleton("test_method")
        assert "def test_method(self)" in skeleton
        assert "raise NotImplementedError" in skeleton

    def test_test_func_name(
        self,
        mirror_config: tuple[type[MirrorTestConfigFile], Path],
    ) -> None:
        """Test method."""
        config_cls, _ = mirror_config
        func = next(
            node
            for node in ast.parse("async def sample(): pass").body
            if isinstance(node, ast.AsyncFunctionDef)
        )
        assert config_cls().test_func_name(func) == "test_sample"

    def test_test_cls_name(
        self,
        mirror_config: tuple[type[MirrorTestConfigFile], Path],
    ) -> None:
        """Test method."""
        config_cls, _ = mirror_config
        cls = next(iter(cls_definitions(ast.parse("class Example: pass"))))
        assert config_cls().test_cls_name(cls) == "TestExample"

    def test_test_func_prefix(
        self,
        mirror_config: tuple[type[MirrorTestConfigFile], Path],
    ) -> None:
        """Test method."""
        config_cls, _ = mirror_config
        assert config_cls().test_func_prefix() == "test_"

    def test_test_cls_prefix(
        self,
        mirror_config: tuple[type[MirrorTestConfigFile], Path],
    ) -> None:
        """Test method."""
        config_cls, _ = mirror_config
        assert config_cls().test_cls_prefix() == "Test"

    def test_test_module_prefix(
        self,
        mirror_config: tuple[type[MirrorTestConfigFile], Path],
    ) -> None:
        """Test method."""
        config_cls, _ = mirror_config
        assert config_cls().test_module_prefix() == "test_"

    def test_test_module_docstring(
        self,
        mirror_config: tuple[type[MirrorTestConfigFile], Path],
    ) -> None:
        """Test method."""
        config_cls, _ = mirror_config
        assert config_cls().test_module_docstring() == '"""Test module."""\n'
