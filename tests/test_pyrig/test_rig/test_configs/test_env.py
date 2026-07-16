"""module."""

from contextlib import chdir
from pathlib import Path
from typing import Any

import pytest

from pyrig.rig.configs.env import EnvConfigFile


class TestEnvConfigFile:
    """Test class."""

    def test_is_correct(self, tmp_path: Path) -> None:
        """Test method."""
        with chdir(tmp_path):
            assert not EnvConfigFile.I.is_correct()
            EnvConfigFile.I.create_file()
            assert EnvConfigFile.I.is_correct()

    def test_extension_separator(self) -> None:
        """Test method."""
        assert EnvConfigFile.I.extension_separator() == ""

    def test_version_control_ignored(self) -> None:
        """Test method."""
        assert EnvConfigFile.I.version_control_ignored() is True

    def test__load(self) -> None:
        """Test method."""
        with pytest.raises(RuntimeError, match=r".* should never be loaded."):
            EnvConfigFile.I._load()  # noqa: SLF001

    def test__dump(self) -> None:
        """Test method."""
        with pytest.raises(
            ValueError,
            match=r"cannot dump to .*",
        ):
            EnvConfigFile.I._dump({"key": "val"})  # noqa: SLF001

        EnvConfigFile.I._dump({})  # noqa: SLF001

    def test_extension(self) -> None:
        """Test method."""
        assert EnvConfigFile.I.extension() == ""

    def test_stem(self) -> None:
        """Test method."""
        assert EnvConfigFile.I.stem() == ".env"

    def test_parent_path(
        self,
        tmp_path: Path,
    ) -> None:
        """Test method."""
        # Should return Path() (root)
        with chdir(tmp_path):
            expected = Path()
            actual = EnvConfigFile.I.parent_path()
            assert actual == expected, f"Expected {expected}, got {actual}"

    def test__configs(self) -> None:
        """Test method."""
        # Should return empty dict
        expected: dict[str, Any] = {}
        actual = EnvConfigFile.I.configs()
        assert actual == expected, f"Expected {expected}, got {actual}"
