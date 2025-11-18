"""test module."""

from pyrig.dev.configs.pyproject import PyprojectConfigFile
from pyrig.src.os.os import run_subprocess


def test_main() -> None:
    """Test func for main."""
    project_name = PyprojectConfigFile.get_project_name()
    stdout = run_subprocess(["poetry", "run", project_name, "--help"]).stdout.decode(
        "utf-8"
    )
    assert project_name in stdout
