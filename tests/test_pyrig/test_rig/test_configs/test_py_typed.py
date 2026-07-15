"""module."""

from pathlib import Path

import pytest

from pyrig.rig.configs.py_typed import PyTypedConfigFile


class TestPyTypedConfigFile:
    """Test class."""

    def test_stem(self) -> None:
        """Test method."""
        assert PyTypedConfigFile.I.stem() == "py"
        assert PyTypedConfigFile().path().name == "py.typed"

    def test_parent_path(
        self,
    ) -> None:
        """Test method."""
        parent_path = PyTypedConfigFile.I.parent_path()
        assert parent_path == Path("src/pyrig")

    def test_extension(self) -> None:
        """Test method."""
        assert PyTypedConfigFile.I.extension() == "typed"

    def test__configs(self) -> None:
        """Test method."""
        configs = PyTypedConfigFile.I._configs()  # noqa: SLF001
        assert configs == {}

    def test__dump(self) -> None:
        """Test method."""
        PyTypedConfigFile.I._dump({})  # noqa: SLF001
        with pytest.raises(ValueError, match="cannot dump to"):
            PyTypedConfigFile.I._dump({"key": "value"})  # noqa: SLF001

    def test__load(self) -> None:
        """Test method."""
        configs = PyTypedConfigFile.I._load()  # noqa: SLF001
        assert configs == {}
