"""Entry point to call the current project's main function."""

from importlib import import_module

from pyrig import main
from pyrig.dev.configs.pyproject import PyprojectConfigFile
from pyrig.src.modules.package import get_src_package


def call_main() -> None:
    """Call the main function from the current project.

    Mainly exists for the pyinstaller builder or another builder to call
    when creating an executable or another artifact that needs to call
    the project's main function.
    """
    main_module_name = PyprojectConfigFile.get_module_name_replacing_start_module(
        main, get_src_package().__name__
    )
    main_module = import_module(main_module_name)
    main_module.main()


if __name__ == "__main__":
    call_main()
