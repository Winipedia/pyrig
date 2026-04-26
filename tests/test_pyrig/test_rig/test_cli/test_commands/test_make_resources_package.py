"""module."""

from contextlib import chdir
from pathlib import Path

from pyrig.rig import resources
from pyrig.rig.cli.commands.make_resources_package import make_resources_package


def test_make_resources_package(tmp_path: Path) -> None:
    """Test function."""
    project_path = tmp_path / "my-project"
    project_path.mkdir()

    with chdir(project_path):
        # create a new subcommand
        make_resources_package()

        # check if the file was created and contains the expected content
        subcommands_file = (
            project_path / "src" / "my_project" / "rig" / "resources" / "__init__.py"
        )
        assert subcommands_file.exists()


def test_resources_docstring() -> None:
    """Test function."""
    assert resources.__doc__ == """Static resource files for this project."""
