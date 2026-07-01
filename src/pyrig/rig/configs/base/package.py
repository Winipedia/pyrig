"""Base class for Python config files that must reside within a valid package tree."""

from pyrig.core.introspection.packages import make_package_dir
from pyrig.rig.configs.base.python import PythonConfigFile
from pyrig.rig.tools.package_manager import PackageManager
from pyrig.rig.tools.programming_language import ProgrammingLanguage
from pyrig.rig.tools.testers.project import ProjectTester


class PythonPackageConfigFile(PythonConfigFile):
    """Base class for Python source files that require a valid package tree.

    Before writing the file, ensures every ancestor directory up to (but not
    including) the project source root and tests source root contains an
    `__init__.py`, making the generated file immediately importable.

    Use this class instead of `PythonConfigFile` whenever the generated file
    lives inside a package hierarchy that may not yet be fully initialised—for
    example, when scaffolding new sub-packages or mirror test modules.
    """

    def _dump(self, configs: list[str]) -> None:
        """Create any missing ancestor package directories, then write the file.

        Args:
            configs: Lines of Python source code to write to the target file.
        """
        make_package_dir(
            self.path().parent,
            until=(
                ProjectTester.I.tests_source_root(),
                PackageManager.I.source_root(),
            ),
            content=ProgrammingLanguage.I.standard_init_content(),
        )
        super()._dump(configs)
