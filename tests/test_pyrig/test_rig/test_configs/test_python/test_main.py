"""module."""

from collections.abc import Callable
from contextlib import chdir
from pathlib import Path

import pytest
from pytest_mock import MockFixture

from pyrig import main
from pyrig.rig.configs.python.main import MainConfigFile


@pytest.fixture
def my_test_main_config_file(
    config_file_factory: Callable[[type[MainConfigFile]], type[MainConfigFile]],
) -> type[MainConfigFile]:
    """Create a test main config file class with tmp_path."""

    class MyTestMainConfigFile(config_file_factory(MainConfigFile)):  # type: ignore [misc]
        """Test main config file with tmp_path override."""

    return MyTestMainConfigFile


class TestMainConfigFile:
    """Test class."""

    def test___init__(
        self,
        mocker: MockFixture,
    ) -> None:
        """Test method."""
        # spy on delete_root_main
        spy = mocker.spy(
            MainConfigFile,
            MainConfigFile.delete_root_main.__name__,
        )
        MainConfigFile()
        spy.assert_called_once()

    def test_get_src_module(self) -> None:
        """Test method for get_src_module."""
        module = MainConfigFile.get_src_module()
        assert module == main

    def test_is_correct(self) -> None:
        """Test method for is_correct."""
        assert MainConfigFile.is_correct()

    def test_delete_root_main(self, tmp_path: Path) -> None:
        """Test method for delete_root_main."""
        with chdir(tmp_path):
            Path("main.py").write_text("test")
            MainConfigFile.delete_root_main()
            assert not Path("main.py").exists(), "Expected main.py to be deleted"
