"""module."""

from pyrig.dev.cli.subcommands import (
    build,
    init,
    mkinits,
    mkroot,
    mktests,
    protect_repo,
)
from pyrig.src.os.os import run_subprocess
from pyrig.src.project.mgt import (
    get_pyrig_cli_cmd_args,
)
from pyrig.src.testing.assertions import assert_with_msg


def test_mkroot() -> None:
    """Test func for create_root."""
    # run --help comd to see if its available
    stoud = run_subprocess([*get_pyrig_cli_cmd_args(mkroot), "--help"]).stdout.decode(
        "utf-8"
    )
    assert_with_msg(
        mkroot.__name__ in stoud,
        f"Expected {mkroot.__name__} in stdout, got {stoud}",
    )


def test_mktests() -> None:
    """Test func for create_tests."""
    # run --help comd to see if its available
    stoud = run_subprocess([*get_pyrig_cli_cmd_args(mktests), "--help"]).stdout.decode(
        "utf-8"
    )
    assert_with_msg(
        mktests.__name__ in stoud,
        f"Expected {mktests.__name__} in stdout, got {stoud}",
    )


def test_mkinits() -> None:
    """Test func for mkinits."""
    # run --help comd to see if its available
    stoud = run_subprocess([*get_pyrig_cli_cmd_args(mkinits), "--help"]).stdout.decode(
        "utf-8"
    )
    assert_with_msg(
        mkinits.__name__ in stoud,
        f"Expected {mkinits.__name__} in stdout, got {stoud}",
    )


def test_init() -> None:
    """Test func for setup."""
    # run --help comd to see if its available
    stoud = run_subprocess([*get_pyrig_cli_cmd_args(init), "--help"]).stdout.decode(
        "utf-8"
    )
    assert_with_msg(
        init.__name__ in stoud,
        f"Expected {init.__name__} in stdout, got {stoud}",
    )


def test_build() -> None:
    """Test func for build."""
    # run --help comd to see if its available
    stoud = run_subprocess([*get_pyrig_cli_cmd_args(build), "--help"]).stdout.decode(
        "utf-8"
    )
    assert_with_msg(
        build.__name__ in stoud,
        f"Expected {build.__name__} in stdout, got {stoud}",
    )


def test_protect_repo() -> None:
    """Test func for protect_repo."""
    # run --help comd to see if its available
    stoud = run_subprocess(
        [*get_pyrig_cli_cmd_args(protect_repo), "--help"]
    ).stdout.decode("utf-8")
    name = protect_repo.__name__.replace("_", "-")
    assert_with_msg(
        name in stoud,
        f"Expected {name} in stdout, got {stoud}",
    )
