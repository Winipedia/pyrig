"""Contains an simple test for cli."""

from pyrig.src.os.os import run_subprocess
from pyrig.src.testing.assertions import assert_with_msg


def test_add_subcommands() -> None:
    """Test for the add_subcommands func."""
    # run --help comd to see if its available
    result = run_subprocess(["poetry", "run", "pyrig", "--help"])
    stdout = result.stdout.decode("utf-8")
    assert_with_msg(
        "pyrig" in stdout,
        f"Expected pyrig in stdout, got {stdout}",
    )


def test_main() -> None:
    """Test for the main cli entrypoint."""
    result = run_subprocess(["poetry", "run", "pyrig", "--help"])
    assert_with_msg(
        result.returncode == 0,
        "Expected returncode 0",
    )
