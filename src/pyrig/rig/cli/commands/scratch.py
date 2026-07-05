"""CLI command for executing the project scratch file."""

from runpy import run_path

from pyrig.rig.configs.scratch import ScratchConfigFile


def run_scratch_file() -> None:
    """Execute `.scratch.py` at the project root as `__main__`."""
    run_path(ScratchConfigFile.I.path().as_posix(), run_name="__main__")
