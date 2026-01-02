"""module."""

from pyrig.dev.cli.shared_subcommands import version
from pyrig.dev.management.pyrigger import Pyrigger


def test_version() -> None:
    """Test function."""
    args = Pyrigger.get_cmd_args(version)

    result = args.run()
    stdout = result.stdout.decode("utf-8")
    assert "version" in stdout, f"Expected 'version' in stdout, got {stdout}"

    # is callable
    version()
