"""module."""

import sys
from collections.abc import Callable
from contextlib import chdir
from pathlib import Path
from types import ModuleType

import pytest

from pyrig.core.introspection.modules import reimport_module
from pyrig.rig.configs.base.copy_module_docstring import CopyModuleDocstringConfigFile
from pyrig.rig.configs.license import LicenseConfigFile
from pyrig.rig.tools.version_control.controller import VersionController


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
