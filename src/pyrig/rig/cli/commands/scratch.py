"""CLI command for executing the project scratch file."""

from runpy import run_path

from pyrig.rig.configs.scratch import ScratchConfigFile


def run_scratch_file() -> None:
    """Execute `.scratch.py` at the project root.

    Raises:
        FileNotFoundError: If `.scratch.py` does not exist at the project root.
    """
    run_path(ScratchConfigFile.I.path().as_posix())
