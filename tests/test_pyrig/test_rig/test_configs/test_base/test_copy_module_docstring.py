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
from pyrig.rig.configs.pyproject import PyprojectConfigFile


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
            "test_package.test_subpackage.test_module", None
        )
        if cached_module is not None:
            # needed for the debugger for some reason
            Path(cached_module.__file__).unlink()  # ty:ignore[invalid-argument-type]
        module = create_module(path)

        path.write_text('"""Test module content."""')

        module = reimport_module(module)

    class MyTestCopyModuleDocstringConfigFile(
        config_file_factory(CopyModuleDocstringConfigFile)  # ty: ignore[unsupported-base]
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
            my_test_copy_module_only_docstring_config_file().default_docstring(), str
        )

    def test_lines(
        self,
        my_test_copy_module_only_docstring_config_file: type[
            CopyModuleDocstringConfigFile
        ],
    ) -> None:
        """Test method."""
        lines = my_test_copy_module_only_docstring_config_file().lines()
        content_str = "\n".join(lines)

        # assert its only the docstring
        # note with extra newline at the end
        assert content_str == '"""Test module content."""\n'

    def test_is_correct(
        self,
        my_test_copy_module_only_docstring_config_file: type[
            CopyModuleDocstringConfigFile
        ],
        tmp_path: Path,
    ) -> None:
        """Test method."""
        with chdir(tmp_path):
            LicenseConfigFile.I.validate()
            PyprojectConfigFile.I.validate()
            my_test_copy_module_only_docstring_config_file().validate()
            assert my_test_copy_module_only_docstring_config_file().is_correct()
