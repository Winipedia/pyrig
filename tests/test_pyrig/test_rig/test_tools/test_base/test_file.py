"""module."""

import pytest

from pyrig.rig.tools.base.file import FileTool
from pyrig.rig.tools.base.tool import Group


class TestFileTool:
    """Test class."""

    def test_extension(self) -> None:
        """Test method."""
        # FileTool itself implements none of its abstract methods, so it
        # must stay uninstantiable until a subclass implements them all -
        # including extension, which PackageManager-style whole-project
        # tools never need since they stay on plain Tool. `.I` can't be
        # used here: with multiple real leaf subclasses already existing
        # (ShellLinter, PythonLinter, ...), it resolves to "which leaf?"
        # rather than instantiating FileTool itself.
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            FileTool()

    def test_regex(self) -> None:
        """Test method."""

        class MyTestFileTool(FileTool):
            """Concrete `FileTool` with a fixed extension, for testing `regex()`."""

            def group(self) -> str:
                """Get the badge group."""
                return Group.TOOLING

            def image_url(self) -> str:
                """Get the badge image URL."""
                return "https://example.com/badge"

            def link_url(self) -> str:
                """Get the badge link URL."""
                return "https://example.com"

            def name(self) -> str:
                """Get the executable name."""
                return "mytool"

            def extension(self) -> str:
                """Get the file extension."""
                return "ext"

        assert MyTestFileTool().regex() == r"\.ext$"
