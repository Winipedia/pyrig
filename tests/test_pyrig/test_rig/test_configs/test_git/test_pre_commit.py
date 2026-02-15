"""module."""

from collections.abc import Callable
from contextlib import chdir
from pathlib import Path

import pytest

from pyrig.rig.configs.git.pre_commit import PrekConfigFile
from pyrig.src.processes import Args


@pytest.fixture
def my_test_prek_config_file(
    config_file_factory: Callable[[type[PrekConfigFile]], type[PrekConfigFile]],
) -> type[PrekConfigFile]:
    """Create a test prek config file class with tmp_path."""

    class MyTestPrekConfigFile(
        config_file_factory(PrekConfigFile)  # type: ignore [misc]
    ):
        """Test prek config file with tmp_path override."""

    return MyTestPrekConfigFile


class TestPrekConfigFile:
    """Test class."""

    def test_hook(self) -> None:
        """Test method."""
        hook = PrekConfigFile.I.hook("test", Args(("test",)))
        assert hook["id"] == "test", f"Expected id to be 'test', got {hook['id']}"

    def test_parent_path(
        self,
        my_test_prek_config_file: type[PrekConfigFile],
        tmp_path: Path,
    ) -> None:
        """Test method."""
        with chdir(tmp_path):
            parent_path = my_test_prek_config_file().parent_path()
            assert parent_path == Path(), f"Expected Path(), got {parent_path}"

    def test__configs(self, my_test_prek_config_file: type[PrekConfigFile]) -> None:
        """Test method."""
        configs = my_test_prek_config_file().configs()
        assert "repos" in configs, "Expected 'repos' key in configs"
        assert isinstance(configs["repos"], list), "Expected 'repos' to be a list"
        assert len(configs["repos"]) > 0, "Expected at least one repo in configs"
        repo = configs["repos"][0]
        assert repo["repo"] == "local", (
            f"Expected repo to be 'local', got {repo['repo']}"
        )
        assert "hooks" in repo, "Expected 'hooks' key in repo"
        assert isinstance(repo["hooks"], list), "Expected 'hooks' to be a list"
        assert len(repo["hooks"]) > 0, "Expected at least one hook in repo"
