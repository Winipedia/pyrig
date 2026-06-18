"""module."""

from collections.abc import Callable
from contextlib import chdir
from pathlib import Path
from typing import Any

import pytest

from pyrig.rig.configs.env import EnvConfigFile


@pytest.fixture
def my_test_dotenv_config_file(
    config_file_factory: Callable[[type[EnvConfigFile]], type[EnvConfigFile]],
) -> type[EnvConfigFile]:
    """Create a test dotenv config file class with tmp_path."""

    class MyTestEnvConfigFile(config_file_factory(EnvConfigFile)):  # ty: ignore[unsupported-base]
        """Test dotenv config file with tmp_path override."""

    return MyTestEnvConfigFile


class TestEnvConfigFile:
    """Test class."""

    def test_is_correct(self) -> None:
        """Test method."""
        assert EnvConfigFile.I.is_correct()

    def test_extension_separator(self) -> None:
        """Test method."""
        assert EnvConfigFile.I.extension_separator() == ""

    def test_version_control_ignored(self) -> None:
        """Test method."""
        assert EnvConfigFile.I.version_control_ignored() is True

    def test__load(self, my_test_dotenv_config_file: type[EnvConfigFile]) -> None:
        """Test method."""
        with pytest.raises(RuntimeError):
            my_test_dotenv_config_file().load()

    def test__dump(self, my_test_dotenv_config_file: type[EnvConfigFile]) -> None:
        """Test method."""
        # dump should raise RuntimeError if config is not empty (truthy)
        with pytest.raises(
            PermissionError,
            match=r"Dumping to .* is forbidden.",
        ):
            my_test_dotenv_config_file().dump({"key": "val"})

        my_test_dotenv_config_file().dump({})

    def test_extension(self, my_test_dotenv_config_file: type[EnvConfigFile]) -> None:
        """Test method."""
        assert my_test_dotenv_config_file().extension() == ""

    def test_stem(self, my_test_dotenv_config_file: type[EnvConfigFile]) -> None:
        """Test method."""
        assert my_test_dotenv_config_file().stem() == ".env"

    def test_parent_path(
        self,
        my_test_dotenv_config_file: type[EnvConfigFile],
        tmp_path: Path,
    ) -> None:
        """Test method."""
        # Should return Path() (root)
        with chdir(tmp_path):
            expected = Path()
            actual = my_test_dotenv_config_file().parent_path()
            assert actual == expected, f"Expected {expected}, got {actual}"

    def test__configs(self, my_test_dotenv_config_file: type[EnvConfigFile]) -> None:
        """Test method."""
        # Should return empty dict
        expected: dict[str, Any] = {}
        actual = my_test_dotenv_config_file().configs()
        assert actual == expected, f"Expected {expected}, got {actual}"
