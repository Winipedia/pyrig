"""module."""

from contextlib import chdir
from pathlib import Path

from pyrig.rig.cli.commands.make_fixture import make_fixture


def test_make_fixture(tmp_path: Path) -> None:
    """Test function."""
    project_path = tmp_path / "my-project"
    project_path.mkdir()

    with chdir(project_path):
        # create a new subcommand
        make_fixture("my-new-fixture")

        # check if the file was created and contains the expected content
        fixtures_file = (
            project_path
            / "src"
            / "my_project"
            / "rig"
            / "tests"
            / "fixtures"
            / "fixtures.py"
        )
        assert fixtures_file.exists(), f"{fixtures_file} does not exist"

        content = fixtures_file.read_text()
        assert "def my_new_fixture() -> None:" in content
        assert "@pytest.fixture" in content
        assert "import pytest" in content
        assert content.endswith("\n")
