"""module."""

import sys
from collections.abc import Callable
from contextlib import chdir
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

from pyrig.core.introspection.modules import reimport_module
from pyrig.rig.configs.base.copy_module import (
    CopyModuleConfigFile,
    CopyModuleDocstringConfigFile,
)
from pyrig.rig.configs.base.python import PythonPackageConfigFile
from pyrig.rig.configs.community.license import LicenseConfigFile
from pyrig.rig.tools.version_control.controller import VersionController


@pytest.fixture
def my_test_copy_module_config_file(
    config_file_factory: Callable[
        [type[PythonPackageConfigFile]],
        type[PythonPackageConfigFile],
    ],
    tmp_path: Path,
) -> type[PythonPackageConfigFile]:
    """Create a test copy module config file class with tmp_path."""
    # Create a mock module for testing

    mock_module = ModuleType("test_package.test_subpackage.test_module")
    mock_module.__file__ = str(
        tmp_path / "test_package" / "test_subpackage" / "test_module.py",
    )

    # Create the module file with some content
    module_path = Path(mock_module.__file__)
    module_path.parent.mkdir(parents=True, exist_ok=True)
    test_content = (
        '"""Test module content."""\n\n'
        "def test_func():\n"
        '    """Test function."""\n'
        "    pass\n"
    )
    module_path.write_text(test_content)

    class MyTestCopyModuleConfigFile(config_file_factory(CopyModuleConfigFile)):  # ty: ignore[unsupported-base]
        """Test copy module config file with tmp_path override."""

        def copy_module(self) -> ModuleType:
            """Get the source module."""
            return mock_module

        def _dump(self, configs: list[Any]) -> None:
            """Dump the config file."""
            with chdir(tmp_path):
                super()._dump(configs)

    return MyTestCopyModuleConfigFile


class TestCopyModuleConfigFile:
    """Test class."""

    def test_module_path(self) -> None:
        """Test method."""
        # Create a mock module to test
        module = ModuleType("test_package.test_subpackage.test_module")
        module.__file__ = "test_package/test_subpackage/test_module.py"

        # Generate the subclass config file
        subclass = CopyModuleConfigFile.generate_subclass(module)

        # Verify the generated subclass has the correct module_path method
        subclass_instance = subclass()
        expected_path = Path("src/pyrig/test_subpackage/test_module.py")
        actual_path = subclass_instance.module_path()
        assert actual_path == expected_path

    def test_generate_subclass(self) -> None:
        """Test method."""
        # Create a mock module to subclass
        module = ModuleType("test_package.test_subpackage.test_module")
        module.__file__ = "test_package/test_subpackage/test_module.py"

        # Generate the subclass config file
        subclass = CopyModuleConfigFile.generate_subclass(module)

        # Verify the generated subclass has the correct src_module method
        subclass_instance = subclass()
        assert isinstance(subclass_instance, CopyModuleConfigFile)
        assert subclass_instance.copy_module() == module

    def test_copy_module(
        self,
        my_test_copy_module_config_file: type[CopyModuleConfigFile],
    ) -> None:
        """Test method."""
        src_module = my_test_copy_module_config_file().copy_module()
        assert isinstance(src_module, ModuleType), "Expected ModuleType"
        expected_name = "test_package.test_subpackage.test_module"
        assert src_module.__name__ == expected_name, (
            f"Expected '{expected_name}', got {src_module.__name__}"
        )

    def test_parent_path(
        self,
        my_test_copy_module_config_file: type[CopyModuleConfigFile],
    ) -> None:
        """Test method."""
        parent_path = my_test_copy_module_config_file().parent_path()
        assert isinstance(parent_path, Path), "Expected Path"

    def test_content(
        self,
        my_test_copy_module_config_file: type[CopyModuleConfigFile],
    ) -> None:
        """Test method."""
        content = my_test_copy_module_config_file().content()
        assert len(content) > 0, "Expected non-empty string"
        # Verify it contains the module content
        assert "Test module content" in content, "Expected module content in string"

    def test_stem(
        self,
        my_test_copy_module_config_file: type[CopyModuleConfigFile],
    ) -> None:
        """Test method."""
        filename = my_test_copy_module_config_file().stem()
        assert filename == "test_module", f"Expected 'test_module', got {filename}"


@pytest.fixture
def my_test_copy_module_only_docstring_config_file(
    config_file_factory: Callable[
        [type[CopyModuleDocstringConfigFile]],
        type[CopyModuleDocstringConfigFile],
    ],
    tmp_path: Path,
    create_module: Callable[[Path], ModuleType],
) -> type[CopyModuleDocstringConfigFile]:
    """Create a test copy module only docstring config file class with tmp_path."""
    path = Path("test_package") / "test_subpackage" / "test_module.py"
    with chdir(tmp_path):
        cached_module = sys.modules.pop(
            "test_package.test_subpackage.test_module",
            None,
        )
        if cached_module is not None:
            # needed for the debugger for some reason
            Path(cached_module.__file__).unlink()  # ty:ignore[invalid-argument-type]
        module = create_module(path)

        path.write_text('"""Test module content."""')

        module = reimport_module(module)

    class MyTestCopyModuleDocstringConfigFile(
        config_file_factory(CopyModuleDocstringConfigFile),  # ty: ignore[unsupported-base]
    ):
        """Test copy module only docstring config file with tmp_path override."""

        def copy_module(self) -> ModuleType:
            """Get the source module."""
            return module

    return MyTestCopyModuleDocstringConfigFile


class TestCopyModuleDocstringConfigFile:
    """Test class."""

    def test_default_docstring(
        self,
        my_test_copy_module_only_docstring_config_file: type[
            CopyModuleDocstringConfigFile
        ],
    ) -> None:
        """Test method."""
        assert isinstance(
            my_test_copy_module_only_docstring_config_file().default_docstring(),
            str,
        )

    def test_content(
        self,
        my_test_copy_module_only_docstring_config_file: type[
            CopyModuleDocstringConfigFile
        ],
    ) -> None:
        """Test method."""
        config = my_test_copy_module_only_docstring_config_file()
        module = config.copy_module()

        # plain docstring, wrapped in double triple quotes, trailing newline added
        module.__doc__ = "Test module content."
        assert config.content() == '"""Test module content."""\n'

        # a docstring containing `"""` falls back to single triple quotes
        module.__doc__ = 'Contains """ inside.'
        assert config.content() == "'''Contains \"\"\" inside.'''\n"

        # a docstring containing `'''` keeps the default double triple quotes
        module.__doc__ = "Contains ''' inside."
        assert config.content() == '"""Contains \'\'\' inside."""\n'

        # a docstring containing both falls back to escaping instead of
        # producing invalid syntax
        module.__doc__ = "Contains \"\"\" and ''' inside."
        assert config.content() == "'''Contains \"\"\" and \\'\\'\\' inside.'''\n"

        # multiline docstrings keep their real newlines, not `\n` escapes
        module.__doc__ = "Line one.\n\nLine two."
        assert config.content() == '"""Line one.\n\nLine two."""\n'

        # no docstring falls back to `default_docstring`
        module.__doc__ = None
        assert config.content() == f'"""{config.default_docstring()}"""\n'

    def test_is_correct(
        self,
        my_test_copy_module_only_docstring_config_file: type[
            CopyModuleDocstringConfigFile
        ],
        tmp_path: Path,
    ) -> None:
        """Test method."""
        VersionController.I.repo_owner()
        with chdir(tmp_path):
            LicenseConfigFile.I.validate()
            my_test_copy_module_only_docstring_config_file().validate()
            assert my_test_copy_module_only_docstring_config_file().is_correct()
