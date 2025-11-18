"""test module."""

from pyrig.src.modules.package import get_src_package
from pyrig.src.os.os import run_subprocess


def test_main() -> None:
    """Test func for main."""
    project_name = get_src_package().__name__
    stdout = run_subprocess(["poetry", "run", project_name, "--help"]).stdout.decode(
        "utf-8"
    )
    assert "main" in stdout.lower()
