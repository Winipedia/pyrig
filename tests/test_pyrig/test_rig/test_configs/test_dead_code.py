"""Tests for the Vulture whitelist config file."""

from pathlib import Path

from pyrig.rig.configs.dead_code import DeadCodeCheckerConfigFile


class TestDeadCodeCheckerConfigFile:
    """Test class."""

    def test_content(self) -> None:
        """Test method."""
        assert DeadCodeCheckerConfigFile.I.content() == (
            '"""Explicit references for reviewed dead code false positives."""\n'
        )

    def test_parent_path(self) -> None:
        """Test method."""
        assert DeadCodeCheckerConfigFile.I.parent_path() == Path()

    def test_stem(self) -> None:
        """Test method."""
        assert DeadCodeCheckerConfigFile.I.stem() == "vulture_whitelist"
