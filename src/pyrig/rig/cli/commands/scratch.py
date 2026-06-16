"""CLI command implementation for executing the project scratch file."""

from runpy import run_path

from pyrig.rig.configs.scratch import ScratchConfigFile


def run_scratch_file() -> None:
    """Execute the project's .scratch.py file in a fresh namespace.

    Locates .scratch.py at the project root via ``ScratchConfigFile``
    and runs it using ``runpy.run_path``. The script executes in an
    isolated namespace and does not affect the calling environment.

    Raises:
        FileNotFoundError: If .scratch.py does not exist at the project root.
    """
    run_path(ScratchConfigFile.I.path().as_posix())
