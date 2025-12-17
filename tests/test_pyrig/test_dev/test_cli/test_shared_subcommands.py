"""module."""

from pyrig.dev.cli.shared_subcommands import version
from pyrig.src.os.os import run_subprocess
from pyrig.src.project.mgt import PROJECT_MGT_RUN_ARGS


def test_version() -> None:
    """Test function."""
    result = run_subprocess([*PROJECT_MGT_RUN_ARGS, "pyrig", version.__name__])
    stdout = result.stdout.decode("utf-8")
    assert "version" in stdout, f"Expected 'version' in stdout, got {stdout}"

    # is callable
    version()
