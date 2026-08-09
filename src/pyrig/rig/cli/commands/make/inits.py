"""Creation logic for every `__init__.py` file in the project."""


def make_project_init_files() -> None:
    """Create missing `__init__.py` files in the project."""
    from pyrig.rig.tools.programming_language import (  # noqa: PLC0415
        ProgrammingLanguage,
    )

    ProgrammingLanguage.I.make_init_files()
