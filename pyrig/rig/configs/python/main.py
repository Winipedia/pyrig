"""Configuration for {package_name}/main.py template.

Generates {package_name}/main.py by copying pyrig.main module. Provides empty main()
function template that gets auto-discovered and registered as CLI command. Cleans up
legacy root-level main.py files.

See Also:
    pyrig.main
    pyrig.rig.cli.cli
    pyrig.rig.configs.pyproject.PyprojectConfigFile
"""

import logging
from pathlib import Path
from types import ModuleType

from pyrig import main
from pyrig.rig.configs.base.copy_module import CopyModuleConfigFile

logger = logging.getLogger(__name__)


class MainConfigFile(CopyModuleConfigFile):
    """Manages {package_name}/main.py.

    Generates {package_name}/main.py by copying pyrig.main module. Provides empty
    main() function template that gets auto-discovered and registered as CLI command.
    Automatically deletes root-level main.py files on validation.

    Examples:
        Generate {package_name}/main.py::

            MainConfigFile.I.validate()

        Generated file structure::

            \"\"\"Main entrypoint for the project.\"\"\"


            def main() -> None:
                \"\"\"Main entrypoint for the project.\"\"\"


            if __name__ == "__main__":
                main()

    See Also:
        pyrig.main
        pyrig.rig.cli.cli.add_subcommands
        pyrig.rig.configs.base.copy_module.CopyModuleConfigFile
    """

    def create_file(self) -> None:
        """Create main.py by copying the `pyrig.main` module.

        Also delete root-level main.py if it exists to clean up legacy
        files from ``uv init``.
        """
        super().create_file()
        self.delete_root_main()

    def src_module(self) -> ModuleType:
        """Get the source module to copy.

        Returns:
            ModuleType: pyrig.main module.

        Note:
            Entire module is copied, not just docstring.
    def src_module(self) -> ModuleType:
        return main

    def is_correct(self) -> bool:
        """Check if the main.py file is valid.

        Returns:
            bool: True if the parent check passes or the file contains
                ``def main`` and an ``__main__`` guard.

        Note:
            Reads file from disk to check content.
    def is_correct(self) -> bool:
        return super().is_correct() or (
            "def main" in self.file_content()
            and 'if __name__ == "__main__":' in self.file_content()
        )

    def delete_root_main(self) -> None:
        """Delete root-level main.py if it exists.

        Note:
            Called automatically during `create_file` to clean up legacy
            files from ``uv init``.
        """
        root_main_path = Path("main.py")
        if root_main_path.exists():
            logger.info("Deleting root-level main.py file")
            root_main_path.unlink()
