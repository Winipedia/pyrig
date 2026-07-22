"""Create all missing `__init__.py` files in the project."""


def make_project_init_files() -> None:
    """Create all missing `__init__.py` files in the project.

    Echoes each directory where a file was created to standard output.

    Returns:
        Directories where `__init__.py` files were created. Empty if all
        already existed.
    """
    from pyrig.rig.tools.programming_language import (  # noqa: PLC0415
        ProgrammingLanguage,
    )

    ProgrammingLanguage.I.make_init_files()
