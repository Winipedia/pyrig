"""CLI entry point for `pyrig init-project`.

Delegates all initialization logic to `Pyrigger.init_project`.
"""

from pyrig.rig.tools.pyrigger import Pyrigger


def init_project() -> None:
    """Initialize a new pyrig project.

    Delegates to `Pyrigger.I.init_project`, which runs the full setup
    sequence: version control, dependencies, config files, test skeletons,
    pre-commit hooks, and an initial commit.
    """
    Pyrigger.I.init_project()
