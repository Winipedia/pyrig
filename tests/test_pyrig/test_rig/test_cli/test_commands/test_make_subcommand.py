"""module."""

from contextlib import chdir
from pathlib import Path

from pyrig.rig.cli.commands.make_subcommand import make_subcommand


def test_make_subcommand(tmp_path: Path) -> None:
    """Test function."""
    project_path = tmp_path / "my-project"
    project_path.mkdir()

    with chdir(project_path):
        # create a new subcommand
        make_subcommand("my-new-command", shared=False)

        # check if the file was created and contains the expected content
        subcommands_file = (
            project_path / "src" / "my_project" / "rig" / "cli" / "subcommands.py"
        )
        assert subcommands_file.exists()

        content = subcommands_file.read_text()
        assert "def my_new_command() -> None:" in content
