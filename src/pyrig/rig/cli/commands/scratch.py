"""Contains a function that executes the .scratch file of a project."""

from runpy import run_path

from pyrig.rig.configs.python.dot_scratch import DotScratchConfigFile


def run_scratch_file() -> None:
    """Execute the .scratch file of the project, if it exists.

    The .scratch file is a Python script located at the project root. It is
    intended for temporary, ad-hoc code that doesn't belong in the main source
    files. This function checks for the existence of .scratch and executes it
    in a clean namespace.

    Example usage:
        $ uv run pyrig scratch

    Note:
        The .scratch file is not tracked by version control and should be used
        for experimental code, debugging, or one-off scripts related to the
        project.
    """
    run_path(DotScratchConfigFile.I.path())
