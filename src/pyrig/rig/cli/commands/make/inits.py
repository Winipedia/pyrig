"""Create all missing `__init__.py` files in the project."""


def make_project_init_files() -> None:
    """Create all missing `__init__.py` files in the project.

    Each created file's path is printed to standard output.
    """
    from pyrig.rig.tools.programming_language import (  # noqa: PLC0415
        ProgrammingLanguage,
    )

    ProgrammingLanguage.I.make_init_files()
