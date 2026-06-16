"""module."""

from contextlib import chdir
from pathlib import Path

from pytest_mock import MockerFixture

from pyrig.rig.configs.scratch import ScratchConfigFile


class TestScratchConfigFile:
    """Test class."""

    def test_create_file(self, mocker: MockerFixture) -> None:
        """Test method."""
        delete_main_spy = mocker.spy(
            ScratchConfigFile,
            ScratchConfigFile.I.delete_root_main.__name__,
        )
        ScratchConfigFile.I.create_file()
        delete_main_spy.assert_called_once()

    def test_delete_root_main(self, tmp_path: Path) -> None:
        """Test method."""
        with chdir(tmp_path):
            # Create a dummy main.py file
            main_file = tmp_path / "main.py"
            main_file.write_text("print('Hello, World!')")

            # Ensure the file exists
            assert main_file.exists(), "main.py should exist before deletion"

            # Call the delete_root_main method
            ScratchConfigFile.I.delete_root_main()

            # Check that the file has been deleted
            assert not main_file.exists(), "main.py should be deleted"

    def test_version_control_ignored(self) -> None:
        """Test method."""
        assert ScratchConfigFile.I.version_control_ignored() is True

    def test_is_correct(self) -> None:
        """Test method."""
        ScratchConfigFile.I.validate()
        assert ScratchConfigFile.I.is_correct()

    def test_stem(self) -> None:
        """Test method."""
        assert ScratchConfigFile.I.stem() == ".scratch"

    def test_parent_path(
        self,
    ) -> None:
        """Test method."""
        assert ScratchConfigFile.I.parent_path() == Path()

    def test_lines(self) -> None:
        """Test method."""
        lines = ScratchConfigFile.I.lines()
        assert isinstance(lines, list)
        for line in lines:
            assert isinstance(line, str)
