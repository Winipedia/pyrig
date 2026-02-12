"""module."""

from contextlib import chdir
from pathlib import Path

from pyrig.src.modules.package import create_package
from pyrig.src.resource import resource_path


def test_resource_path(tmp_path: Path) -> None:
    """Test function."""
    with chdir(tmp_path):
        # create a pkg
        pkg_path = tmp_path / "pkg"
        pkg = create_package(pkg_path)
        # create a resource
        path = pkg_path / "resource.txt"
        path.write_text("Hello World!")

        assert resource_path("resource.txt", pkg) == path
