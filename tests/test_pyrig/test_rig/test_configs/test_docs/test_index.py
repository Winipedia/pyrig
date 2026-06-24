"""module."""

from pathlib import Path

from pytest_mock import MockerFixture

from pyrig.rig.configs.docs.index import IndexConfigFile
from pyrig.rig.tools.version_control.version_controller import VersionController


class TestIndexConfigFile:
    """Test class."""

    def test_stem(self) -> None:
        """Test method."""
        assert IndexConfigFile.I.stem() == "index"

    def test_parent_path(self) -> None:
        """Test method."""
        parent_path = IndexConfigFile.I.parent_path()
        assert parent_path == Path("docs")

    def test_lines(self, mocker: MockerFixture) -> None:
        """Test method."""
        mock_repo_owner = mocker.patch.object(
            VersionController, "repo_owner", return_value="FakeUser13"
        )
        lines = IndexConfigFile.I.lines()
        content_str = "\n".join(lines)
        assert isinstance(content_str, str)
        mock_repo_owner.assert_called()
