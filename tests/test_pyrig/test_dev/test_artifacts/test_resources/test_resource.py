"""module."""

from contextlib import chdir
from pathlib import Path

from pyrig.dev.artifacts.resources.resource import get_resource_path
from pyrig.src.modules.module import import_module_from_path


def test_get_resource_path(tmp_path: Path) -> None:
    """Test function."""
    with chdir(tmp_path):
        # create a pkg
        pkg_path = tmp_path / "pkg"
        pkg_path.mkdir()
        init_file = pkg_path / "__init__.py"
        init_file.write_text('"""Test package."""\n')
        # create a resource
        resource_path = pkg_path / "resource.txt"
        relative_resource_path = resource_path.relative_to(tmp_path)
        resource_path.write_text("Hello World!")
        # import the pkg
        pkg = import_module_from_path(pkg_path)

        assert get_resource_path("resource.txt", pkg) == relative_resource_path
