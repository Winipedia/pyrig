"""module."""

from contextlib import chdir
from pathlib import Path

from pyrig.src.modules.package import create_package
from pyrig.src.resource import (
    get_resource_path,
)


def test_get_resource_path(tmp_path: Path) -> None:
    """Test function."""
    with chdir(tmp_path):
        # create a pkg
        pkg_path = tmp_path / "pkg"
        pkg = create_package(pkg_path)
        # create a resource
        resource_path = pkg_path / "resource.txt"
        resource_path.write_text("Hello World!")

        assert get_resource_path("resource.txt", pkg) == resource_path
