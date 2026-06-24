"""CLI command implementation for executing the project scratch file."""

from runpy import run_path

from pyrig.rig.configs.scratch import ScratchConfigFile


def run_scratch_file() -> None:
    """Execute the project's .scratch.py file in a fresh namespace.

    The script runs in an isolated namespace and does not affect the
    calling environment.

    Raises:
        FileNotFoundError: If .scratch.py does not exist at the project root.
    """
    run_path(ScratchConfigFile.I.path().as_posix())
