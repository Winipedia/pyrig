"""module."""

from pathlib import Path

from pyrig.core.resources import resource_content, resource_path
from pyrig.rig import resources


def test_resource_path() -> None:
    """Test function."""
    path = resource_path("LATEST_PYTHON_VERSION", resources)
    assert isinstance(path, Path)
    assert path.name == "LATEST_PYTHON_VERSION"
    assert path.exists()


def test_resource_content() -> None:
    """Test function."""
    path = resource_path("LATEST_PYTHON_VERSION", resources)
    content = resource_content("LATEST_PYTHON_VERSION", resources)
    assert content == path.read_text(encoding="utf-8")
    assert content.strip()
