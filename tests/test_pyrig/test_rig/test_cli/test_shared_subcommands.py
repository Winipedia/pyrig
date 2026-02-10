"""module."""

from pyrig.rig.cli.shared_subcommands import version
from pyrig.rig.tools.pyrigger import Pyrigger


def test_version() -> None:
    """Test function."""
    args = Pyrigger.L.get_cmd_args(cmd=version)

    result = args.run()
    stdout = result.stdout
    assert "version" in stdout, f"Expected 'version' in stdout, got {stdout}"

    # is callable
    version()
