"""module."""

from pyrig.dev.cli.shared_subcommands import version
from pyrig.src.project.mgt import Pyrig


def test_version() -> None:
    """Test function."""
    args = Pyrig.get_venv_run_cmd_args(version)

    result = args.run()
    stdout = result.stdout.decode("utf-8")
    assert "version" in stdout, f"Expected 'version' in stdout, got {stdout}"

    # is callable
    version()
