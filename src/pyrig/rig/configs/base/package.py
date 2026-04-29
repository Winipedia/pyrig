'''Base class for Python config files that must reside inside a proper package tree.

Subclass `PythonPackageConfigFile` when a generated .py file must live inside a
directory hierarchy where every ancestor directory is a valid Python package
(i.e. contains an ``__init__.py``). After writing the file itself, the class
automatically creates any missing ``__init__.py`` files up the directory tree,
stopping at the project source root and tests source root so those boundaries
are never touched.

Example:
    >>> from pathlib import Path
    >>> from pyrig.rig.configs.base.package import PythonPackageConfigFile
    >>>
    >>> class MySubpackageModule(PythonPackageConfigFile):
    ...
    ...     def parent_path(self) -> Path:
    ...         return Path("src/mypackage/subpackage")
    ...
    ...
    ...     def stem(self) -> str:
    ...         return "my_subpackage_module"
    ...
    ...
    ...     def lines(self) -> list[str]:
    ...         return ['"""Subpackage module."""']
    >>>
    >>> # Writing creates src/mypackage/subpackage/my_subpackage_module.py and
    >>> # ensures src/mypackage/__init__.py and
    >>> # src/mypackage/subpackage/__init__.py exist.
'''

from pyrig.core.introspection.packages import make_package_dir
from pyrig.rig.configs.base.python import PythonConfigFile
from pyrig.rig.tools.package_manager import PackageManager
from pyrig.rig.tools.programming_language import ProgrammingLanguage
from pyrig.rig.tools.project_tester import ProjectTester


class PythonPackageConfigFile(PythonConfigFile):
    """Base class for Python source files that require a valid package tree.

    Extends `PythonConfigFile` so that, after writing the file, every ancestor
    directory up to (but not including) the project source root and tests source
    root is guaranteed to contain an ``__init__.py``. This makes the generated
    file immediately importable without any extra setup steps.

    Use this class instead of `PythonConfigFile` whenever the generated file
    lives inside a package hierarchy that may not yet be fully initialised—for
    example, when scaffolding new sub-packages or mirror test modules.

    Subclasses must implement:
        - ``parent_path``: Directory that will contain the generated file.
        - ``stem``: The filename without its extension.
        - ``lines``: Python source lines that form the file content.
    """

    def _dump(self, configs: list[str]) -> None:
        """Write the file and initialise any uninitialised ancestor packages.

        First delegates to the parent ``_dump`` to write the file content, then
        calls ``make_package_dir`` on the file's parent directory. That call
        walks up the directory tree, creating an ``__init__.py`` in every
        directory that does not already have one, stopping when it reaches the
        project source root (``PackageManager.source_root``) or the tests source
        root (``ProjectTester.tests_source_root``). Those boundary directories
        themselves are not modified.

        Each generated ``__init__.py`` is written with the project's standard
        init content (``ProgrammingLanguage.standard_init_content``).

        Args:
            configs: Lines of Python source code to write to the target file.
        """
        super()._dump(configs)
        make_package_dir(
            self.path().parent,
            until=(
                ProjectTester.I.tests_source_root(),
                PackageManager.I.source_root(),
            ),
            content=ProgrammingLanguage.I.standard_init_content(),
        )
