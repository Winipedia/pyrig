"""module."""

from pathlib import Path

import pytest

from pyrig.core.resources import (
    resource_content,
    resource_name_from_func,
    resource_path,
)
from pyrig.rig import resources


def test_resource_content() -> None:
    """Test function."""
    path = resource_path("latest_python_version", resources)
    content = resource_content("latest_python_version", resources)
    assert content == path.read_text(encoding="utf-8")
    assert content.strip()


def test_resource_name_from_func() -> None:
    """Test function."""

    def named_function(value: int) -> str:
        return str(value)

    class NamedCallable:
        __name__ = "NAMED_CALLABLE"

        def __call__(self, value: int) -> str:
            return str(value)

        def bound_method(self, value: int) -> str:
            return str(value)

    class UnnamedCallable:
        def __call__(self) -> None:
            pass

    assert resource_name_from_func(named_function) == "named_function"
    assert resource_name_from_func(NamedCallable().bound_method) == "bound_method"
    assert resource_name_from_func(NamedCallable()) == "named_callable"
    assert resource_name_from_func(len) == "len"
    with pytest.raises(AttributeError):
        resource_name_from_func(UnnamedCallable())


def test_resource_path() -> None:
    """Test function."""
    path = resource_path("latest_python_version", resources)
    assert isinstance(path, Path)
    assert path.name == "latest_python_version"
    assert path.exists()
