"""module."""

from contextlib import chdir
from pathlib import Path

from pyrig.rig.cli.commands.make_resources import make_resources


def test_make_resources(tmp_path: Path) -> None:
    """Test function."""
    project_path = tmp_path / "my-project"
    project_path.mkdir()

    with chdir(project_path):
        # create a new subcommand
        make_resources()

        # check if the file was created and contains the expected content
        subcommands_file = (
            project_path / "my_project" / "rig" / "resources" / "__init__.py"
        )
        assert subcommands_file.exists()
