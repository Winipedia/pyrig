"""Contains a simple test for cli."""

from pyrig.dev.cli.shared_subcommands import version
from pyrig.src.project.mgt import Pyrig
from pyrig.src.testing.assertions import assert_with_msg


def test_add_subcommands() -> None:
    """Test for the add_subcommands func."""
    # run --help comd to see if its available
    args = Pyrig.get_venv_run_args("--help")
    result = args.run()
    stdout = result.stdout.decode("utf-8")
    assert_with_msg(
        "pyrig" in stdout,
        f"Expected pyrig in stdout, got {stdout}",
    )


def test_add_shared_subcommands() -> None:
    """Test function."""
    args = Pyrig.get_venv_run_cmd_args(version)
    result = args.run()
    stdout = result.stdout.decode("utf-8")
    assert_with_msg(
        "version" in stdout,
        f"Expected version in stdout, got {stdout}",
    )


def test_main() -> None:
    """Test for the main cli entrypoint."""
    args = Pyrig.get_venv_run_args("--help")
    result = args.run()
    assert_with_msg(
        result.returncode == 0,
        "Expected returncode 0",
    )
