"""Tests for pyrig.src.projects.project module."""

from pyrig.dev.cli.commands.create_root import (
    make_project_root,
)


def test_make_project_root() -> None:
    """Test func for _create_project_root."""
    make_project_root()
