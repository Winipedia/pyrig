"""Contains an simple test for cli."""

from py_dev.utils.os.os import run_subprocess
from py_dev.utils.testing.assertions import assert_with_msg


def test_add_subcommands() -> None:
    """Test for the add_subcommands func."""
    # run --help comd to see if its available
    result = run_subprocess(["poetry", "run", "py-dev", "--help"])
    stdout = result.stdout.decode("utf-8")
    assert_with_msg(
        "py-dev" in stdout,
        f"Expected py-dev in stdout, got {stdout}",
    )


def test_main() -> None:
    """Test for the main cli entrypoint."""
    result = run_subprocess(["poetry", "run", "py-dev", "--help"])
    assert_with_msg(
        result.returncode == 0,
        "Expected returncode 0",
    )
