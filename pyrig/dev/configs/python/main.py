"""Configuration for {package_name}/main.py template.

Generates {package_name}/main.py by copying pyrig.main module. Provides empty main()
function template that gets auto-discovered and registered as CLI command. Cleans up
legacy root-level main.py files.

See Also:
    pyrig.main
    pyrig.dev.cli.cli
    pyrig.dev.configs.pyproject.PyprojectConfigFile
"""

import logging
from pathlib import Path
from types import ModuleType

from pyrig import main
from pyrig.dev.configs.base.copy_module import CopyModuleConfigFile

logger = logging.getLogger(__name__)


class MainConfigFile(CopyModuleConfigFile):
    """Manages {package_name}/main.py.

    Generates {package_name}/main.py by copying pyrig.main module. Provides empty
    main() function template that gets auto-discovered and registered as CLI command.
    Automatically deletes root-level main.py files on initialization.

    Examples:
        Generate {package_name}/main.py::

            MainConfigFile()

        Generated file structure::

            \"\"\"Main entrypoint for the project.\"\"\"


            def main() -> None:
                \"\"\"Main entrypoint for the project.\"\"\"


            if __name__ == "__main__":
                main()

    See Also:
        pyrig.main
        pyrig.dev.cli.cli.add_subcommands
        pyrig.dev.configs.base.copy_module.CopyModuleConfigFile
    """

    def __init__(self) -> None:
        """Initialize and clean up legacy files.

        Side Effects:
            Creates {package_name}/main.py and deletes ./main.py if exists.
        """
        super().__init__()
        self.__class__.delete_root_main()

    @classmethod
    def get_src_module(cls) -> ModuleType:
        """Get the source module to copy.

        Returns:
            ModuleType: pyrig.main module.

        Note:
            Entire module is copied, not just docstring.
        """
        return main

    @classmethod
    def is_correct(cls) -> bool:
        """Check if the main.py file is valid.

        Returns:
            bool: True if file contains "def main" and __main__ guard.

        Note:
            Reads file from disk to check content.
        """
        return super().is_correct() or (
            "def main" in cls.get_file_content()
            and 'if __name__ == "__main__":' in cls.get_file_content()
        )

    @classmethod
    def delete_root_main(cls) -> None:
        """Delete root-level main.py file.

        Side Effects:
            Deletes ./main.py if exists and logs info message.

        Note:
            Called automatically during __init__()
            to clean up legacy files from uv init.
        """
        root_main_path = Path("main.py")
        if root_main_path.exists():
            logger.info("Deleting root-level main.py file")
            root_main_path.unlink()
