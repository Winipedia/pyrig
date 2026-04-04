"""module."""

from collections.abc import Callable
from contextlib import chdir
from pathlib import Path
from types import ModuleType

from pyrig.core.resource import resource_path


def test_resource_path(
    tmp_path: Path, create_package: Callable[[Path], ModuleType]
) -> None:
    """Test function."""
    with chdir(tmp_path):
        # create a package
        package_path = tmp_path / "package"
        package = create_package(package_path)
        # create a resource
        path = package_path / "resource.txt"
        path.write_text("Hello World!")

        assert resource_path("resource.txt", package) == path
