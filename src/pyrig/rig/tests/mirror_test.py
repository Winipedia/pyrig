"""Mirror test configuration management for automatic test skeleton generation.

Provides MirrorTestConfigFile for creating and maintaining test files that mirror
source module structure. This is a core component of pyrig's testing infrastructure,
enabling automatic discovery of untested code and generation of test skeletons.

The mirror testing pattern ensures every source module has a corresponding test module,
every function has a test function, and every class/method has test counterparts.
Test skeletons are generated with NotImplementedError to mark them as pending
implementation.

Key Features:
    - Automatic test file path derivation from source module paths
    - Detection of untested functions, classes, and methods
    - Non-destructive skeleton generation (preserves existing tests)
    - Dynamic subclass creation for batch processing of modules
    - Idempotent operation (safe to run multiple times)

Naming Conventions:
    - Source module `foo.py` → Test module `test_foo.py`
    - Source function `bar()` → Test function `test_bar()`
    - Source class `Baz` → Test class `TestBaz`
    - Source method `qux()` → Test method `test_qux()`

Example:
    Create a mirror test config for a specific module::

        from types import ModuleType
        from pyrig.rig.tests.mirror_test import MirrorTestConfigFile
        import myproject.core

        class CoreMirrorTest(MirrorTestConfigFile):

            def mirror_module(self) -> ModuleType:
                return myproject.core

        CoreMirrorTest()  # Creates tests/test_myproject/test_core.py

    Batch process multiple modules::

        modules = [myproject.core, myproject.utils, myproject.api]
        MirrorTestConfigFile.L.create_test_modules(modules)

See Also:
    pyrig.rig.configs.base.py_package.PythonPackageConfigFile: Parent class
    pyrig.rig.cli.commands.make_tests: CLI command using this class
"""

import logging
from abc import abstractmethod
from collections.abc import Callable, Generator, Iterable
from importlib import import_module
from pathlib import Path
from types import ModuleType
from typing import Any, Self, cast

from pyrig.core.introspection.classes import (
    all_cls_from_module,
    all_methods_from_cls,
    discard_parent_methods,
)
from pyrig.core.introspection.functions import all_functions_from_module
from pyrig.core.introspection.imports import walk_package
from pyrig.core.introspection.inspection import (
    qualname_of_obj,
    sorted_by_def_line,
    unwrapped_obj,
)
from pyrig.core.introspection.modules import (
    import_module_with_file_fallback,
    module_has_docstring,
    reimport_module,
)
from pyrig.core.iterate import generator_has_items
from pyrig.core.strings import make_name_from_obj
from pyrig.rig import tests
from pyrig.rig.configs.base.config_file import ConfigList
from pyrig.rig.configs.base.package import PythonPackageConfigFile
from pyrig.rig.tools.package_manager import PackageManager
from pyrig.rig.tools.project_tester import ProjectTester
from pyrig.rig.utils.path import module_name_as_root_path

logger = logging.getLogger(__name__)


class MirrorTestConfigFile(PythonPackageConfigFile):
    """Base class for creating test files that mirror source module structure.

    MirrorTestConfigFile analyzes a source module, identifies all functions, classes,
    and methods, then generates corresponding test skeletons in the appropriate test
    module. It detects which source elements lack tests and appends skeleton
    implementations without disturbing existing test code.

    The class handles the complete workflow:
    1. Derive test file path from source module path
    2. Analyze source module for functions, classes, and methods
    3. Compare against existing tests to find untested elements
    4. Generate skeleton code for missing tests
    5. Merge new skeletons with existing test file content

    Subclasses must implement:
        - `mirror_module`: Return the source module to mirror

    Methods for Batch Processing:
        - `generate_subclasses`: Create config subclasses for multiple modules
        - `generate_subclass`: Create a config subclass for a single module
        - `create_test_modules`: Generate test files for multiple modules at once

    Examples:
        Subclass for a specific module::

            class MyModuleMirrorTest(MirrorTestConfigFile):

                def mirror_module(self) -> ModuleType:
                    return my_module

        Dynamic subclass creation::

            subclass = MirrorTestConfigFile.L.generate_subclass(my_module)
            subclass()  # Triggers test file creation

    See Also:
        pyrig.rig.configs.base.py_package.PythonPackageConfigFile: Parent class
        pyrig.rig.cli.commands.make_tests.make_test_skeletons: CLI integration
    """

    @abstractmethod
    def mirror_module(self) -> ModuleType:
        """Return the source module to mirror with tests.

        This abstract method must be implemented by subclasses to specify which
        module's structure should be analyzed and mirrored in the test file.

        Returns:
            The source module whose functions, classes, and methods will have
            corresponding test skeletons generated.
        """

    def _dump(self, config: ConfigList) -> None:
        """Forcing reload after dump.

        This is needed because modules are cached and after adding new test skeletons,
        we want to ensure that the next time we access the test module,
        we get the updated version with the new skeletons included.
        By reloading the module after dumping the new content,
        we ensure that any subsequent introspection of the test module
        reflects the latest changes. Needed by is_correct() to work properly
        after skeleton generation.
        """
        super()._dump(config)
        reimport_module(self.test_module())

    def stem(self) -> str:
        """Extract test filename from the derived test path.

        Returns:
            Test module filename without extension (e.g., "test_utils").
        """
        return self.test_path().stem  # filename without extension

    def parent_path(self) -> Path:
        """Get parent directory for the test file.

        Returns:
            Directory path where the test file will be created.
        """
        return self.test_path().parent

    def lines(self) -> ConfigList:
        """Generate complete test module content with skeletons for untested code.

        Returns:
            Full test module source code including existing tests and new skeletons.
        """
        return self.split_lines(self.test_module_content_with_skeletons())

    def should_override_content(self) -> bool:
        """Enable content override mode for skeleton insertion.

        Returns:
            True to enable override mode, allowing lines() to provide
            the complete merged content (existing tests plus new skeletons).

        """
        return True

    def create_file(self) -> None:
        """Create the test file and also import it from the file system."""
        super().create_file()
        import_module_with_file_fallback(self.path(), name=self.test_module_name())

    def is_correct(self) -> bool:
        """Check if all source elements have corresponding tests.

        Validates that every function and method in the source module has a
        corresponding test skeleton or implementation in the test module.

        Returns:
            True if all functions and methods are covered by tests, or if the
            parent class validation passes.
        """
        if not self.path().exists():
            return False

        return not (
            any(self.untested_func_names())
            or any(self.untested_class_and_method_names())
        )

    def merge_configs(self) -> ConfigList:
        """Return test configurations without merging.

        For mirror tests, configs() already includes existing tests,
        so no additional merging is needed.

        Returns:
            List of test configurations from configs().
        """
        return self.configs()

    @classmethod
    def definition_package(cls) -> ModuleType:
        """Get the package where ConfigFile subclasses are defined.

        Defaults to ``pyrig.rig.tests``, which overrides the default of
        ``pyrig.rig.configs``. Can be overridden by subclasses to define
        their own package.
        MirrorTestConfigFile and its subclasses are defined in the tests package because
        they are conceptually part of the testing infrastructure rather than the
        configuration management infrastructure, but also because the dynamic subclass
        creation is unique compared to regular config files and how they are handled

        Returns:
            Package module where the ConfigFile subclass is defined.
        """
        return tests

    def test_path(self) -> Path:
        """Compute the file path for the test module.

        Converts the test module's import name to a filesystem path.

        Returns:
            Relative path to the test file
            (e.g., Path("tests/test_package/test_mod.py")).
        """
        return module_name_as_root_path(self.test_module_name())

    def test_module_name(self) -> str:
        """Get the fully qualified import name for the test module.

        Returns:
            Dotted import path (e.g., "tests.test_mypackage.test_mymodule").
        """
        return ".".join(
            [ProjectTester.I.tests_package_name()]
            + [
                ProjectTester.I.test_module_prefix() + part
                for part in self.mirror_module().__name__.split(".")
            ]
        )

    def test_module_content(self) -> str:
        """Get the current content of the test module as a string.

        Returns:
            The source code of the test module as a single string.
        """
        return self.file_content()

    def test_module(self) -> ModuleType:
        """Import and return the test module.

        Returns:
            The test module object, either imported or newly created.
        """
        return import_module_with_file_fallback(
            self.test_path(), name=self.test_module_name()
        )

    def test_module_content_with_skeletons(self) -> str:
        """Build complete test module content by adding skeletons for untested code.

        Orchestrates the full skeleton generation process:
        1. Retrieves existing test module content
        2. Ensures module has a docstring (adds default if missing)
        3. Appends function skeletons for untested functions
        4. Inserts class and method skeletons for untested classes/methods

        Returns:
            Complete test module source code ready to be written to file.

        Note:
            Preserves all existing test implementations while adding new skeletons.
        """
        test_module_content = self.test_module_content()
        # if module content has no docstring, add the default one
        if not module_has_docstring(self.test_module()):
            test_module_content = self.test_module_docstring() + test_module_content
        test_module_content = self.test_module_content_with_func_skeletons(
            test_module_content
        )
        return self.test_module_content_with_class_skeletons(test_module_content)

    def test_module_content_with_func_skeletons(self, test_module_content: str) -> str:
        """Append test function skeletons for all untested source functions.

        Args:
            test_module_content: Existing test module content to extend.

        Returns:
            Test module content with new function skeletons appended at the end.
        """
        return test_module_content + "".join(
            self.test_func_skeleton(name) for name in self.untested_func_names()
        )

    def untested_func_names(self) -> Generator[str, None, None]:
        """Identify source functions that lack corresponding test functions.

        Compares functions in the source module against functions in the test
        module. For each source function, checks if a test function with the
        expected name (test_<function_name>) exists.

        Returns:
            Generator of test function names that need to be created, using the
            test naming convention (e.g., ("test_foo", "test_bar")).

        Note:
            Logs debug information about the number and names of untested functions.
        """
        funcs = sorted_by_def_line(all_functions_from_module(self.mirror_module()))
        test_funcs = all_functions_from_module(self.test_module())

        supposed_test_func_names = (self.test_func_name(f) for f in funcs)
        actual_test_func_names = {qualname_of_obj(f) for f in test_funcs}

        return (f for f in supposed_test_func_names if f not in actual_test_func_names)

    def test_func_skeleton(self, test_func_name: str) -> str:
        '''Generate skeleton code for a test function.

        Creates a minimal test function that raises NotImplementedError,
        marking it as pending implementation.

        Args:
            test_func_name: Name for the test function (e.g., "test_my_func").

        Returns:
            Python source code for the skeleton test function.

        Example:
            Generated skeleton::

                def test_my_func() -> None:
                    """Test function."""
                    raise NotImplementedError
        '''
        return f'''

def {test_func_name}() -> None:
    """Test function."""
    raise {NotImplementedError.__name__}
'''

    def test_module_content_with_class_skeletons(self, test_module_content: str) -> str:
        """Insert test class and method skeletons for untested source classes.

        For each untested class, either creates a new test class with method
        skeletons, or adds missing method skeletons to an existing test class.
        Handles both cases where the test class doesn't exist and where it exists
        but is missing some test methods.

        Args:
            test_module_content: Existing test module content to extend.

        Returns:
            Test module content with class and method skeletons inserted.

        Raises:
            ValueError: If a test class definition appears multiple times in the
                test module, indicating a structural problem.

        Note:
            Uses string splitting to locate where to insert new methods, ensuring
            existing class content is preserved.
        """
        test_class_to_method_names = self.untested_class_and_method_names()
        for (
            test_class_name,
            test_method_names,
        ) in test_class_to_method_names:
            test_cls_skeleton = self.test_class_skeleton(test_class_name)
            test_cls_content = test_cls_skeleton + "".join(
                self.test_method_skeleton(name) for name in test_method_names
            )

            # if the class already exists we need to insert the new methods
            # rather than overwrite the class
            module_content_parts = test_module_content.split(test_cls_skeleton)
            expected_parts = 2  # bc there should be only one or zero class definition
            num_parts = len(module_content_parts)
            if num_parts > expected_parts:
                msg = (
                    f"Found {num_parts} parts, expected {expected_parts}. "
                    f"This likely means the class {test_class_name} "
                    f"is defined multiple times in the test module."
                )
                raise RuntimeError(msg)
            # we simply insert the new class content into the parts
            module_content_parts.insert(1, test_cls_content)
            test_module_content = "".join(module_content_parts)

        return test_module_content

    def untested_class_and_method_names(
        self,
    ) -> Generator[tuple[str, Generator[str, None, None]], None, None]:
        """Identify source classes and methods lacking corresponding tests.

        Performs a comprehensive comparison between source and test modules:
        1. Extracts all classes and their methods from the source module
        2. Extracts all test classes and their methods from the test module
        3. Maps source class/method names to expected test names
        4. Identifies missing test classes and missing test methods within
           existing test classes

        Returns:
            Generator of tuples of (test_class_name, missing_test_methods_generator).
            The generator yields each test class name and a generator of its
            missing test method names. If a test class is entirely missing,
            it yields a tuple with the class name and a generator
            of all its expected test method names. Returns an empty generator if
            all classes and methods have tests.

        Example:
            Return value structure::

                {
                    "TestMyClass": ("test_method_one", "test_method_two"),
                }

        Note:
            Only considers methods defined directly on the class, excluding
            inherited methods from parent classes.
        """
        classes = sorted_by_def_line(all_cls_from_module(self.mirror_module()))
        test_classes = all_cls_from_module(self.test_module())

        class_to_methods = (
            (
                c,
                sorted_by_def_line(discard_parent_methods(c, all_methods_from_cls(c))),
            )
            for c in classes
        )
        test_class_to_test_methods = (
            (tc, (discard_parent_methods(tc, all_methods_from_cls(tc))))
            for tc in test_classes
        )

        supposed_test_class_to_test_methods_names = (
            (self.test_cls_name(c), (self.test_func_name(m) for m in ms))
            for c, ms in class_to_methods
        )
        actual_test_class_to_test_methods_names = {
            unwrapped_obj(tc).__name__: {unwrapped_obj(tm).__name__ for tm in tms}
            for tc, tms in test_class_to_test_methods
        }

        for (
            supposed_test_class_name,
            supposed_test_methods_names,
        ) in supposed_test_class_to_test_methods_names:
            actual_test_methods_names = set(
                actual_test_class_to_test_methods_names.get(
                    supposed_test_class_name, ()
                )
            )
            untested_test_methods_names = (
                tmn
                for tmn in supposed_test_methods_names
                if tmn not in actual_test_methods_names
            )
            # add the test class name to the dict if there are untested methods
            # or if the test class is not in the test module at all
            has_untested_methods, untested_test_methods_names = generator_has_items(
                untested_test_methods_names
            )
            if has_untested_methods or (
                supposed_test_class_name not in actual_test_class_to_test_methods_names
            ):
                logger.debug("Class %s has untested methods", supposed_test_class_name)
                yield supposed_test_class_name, untested_test_methods_names

    def test_class_skeleton(self, test_class_name: str) -> str:
        '''Generate skeleton code for a test class.

        Creates a minimal test class definition with a docstring.

        Args:
            test_class_name: Name for the test class (e.g., "TestMyClass").

        Returns:
            Python source code for the skeleton test class definition.

        Example:
            Generated skeleton::

                class TestMyClass:
                    """Test class."""
        '''
        return f'''

class {test_class_name}:
    """Test class."""
'''

    def test_method_skeleton(self, test_method_name: str) -> str:
        '''Generate skeleton code for a test method.

        Creates a minimal test method that raises NotImplementedError,
        marking it as pending implementation.

        Args:
            test_method_name: Name for the test method (e.g., "test_my_method").

        Returns:
            Python source code for the skeleton test method with proper indentation.

        Example:
            Generated skeleton::

                def test_my_method(self) -> None:
                    """Test method."""
                    raise NotImplementedError
        '''
        return f'''
    def {test_method_name}(self) -> None:
        """Test method."""
        raise {NotImplementedError.__name__}
'''

    @classmethod
    def generate_subclasses(
        cls, modules: Iterable[ModuleType]
    ) -> Generator[type[Self], None, None]:
        """Create config subclasses for multiple modules.

        Convenience method for batch processing: creates a subclass for each
        module in input order. Priority-based ordering is handled later by
        ``validate_subclasses``.

        Args:
            modules: Sequence of source modules to create test configs for.

        Returns:
            Generator yielding dynamically created subclasses, in input order.

        See Also:
            generate_subclass: Creates individual subclasses
            validate_subclasses: Orders by priority and validates
        """
        return (cls.generate_subclass(m) for m in modules)

    @classmethod
    def generate_subclass(cls, module: ModuleType) -> type[Self]:
        """Dynamically create a config subclass for a specific source module.

        Creates a new class at runtime that:
        1. Inherits from the current class (MirrorTestConfigFile or subclass)
        2. Implements mirror_module() to return the specified module
        3. Has a descriptive class name based on the test module name

        This enables using the config file machinery without manually defining
        a subclass for each source module.

        Args:
            module: Source module that the new subclass will create tests for.

        Returns:
            Dynamically created subclass configured for the given module.

        Example:
            Dynamic subclass creation::

                import myproject.utils
                subclass = MirrorTestConfigFile.L.generate_subclass(
                    myproject.utils
                )
                # subclass.__name__ == "TestUtilsMirrorTestConfigFile"
                subclass()  # Creates tests/test_myproject/test_utils.py
        """
        test_cls_name = (
            make_name_from_obj(obj=module, split_on="_", join_on="", capitalize=True)
            + cls.__name__
        )

        def mirror_module(self: type[Self]) -> ModuleType:  # noqa: ARG001
            return module

        subclass = type(
            test_cls_name,
            (cls,),
            {cls.mirror_module.__name__: mirror_module},
        )
        return cast("type[Self]", subclass)

    @classmethod
    def create_test_modules(cls, modules: Iterable[ModuleType]) -> None:
        """Generate test files for multiple source modules at once.

        High-level convenience method that orchestrates the complete test
        generation workflow for a list of modules:
        1. Creates a subclass for each module
        2. Orders subclasses by priority
        3. Initializes all subclasses (triggering file creation)

        Args:
            modules: List of source modules to generate test files for.

        Example:
            Generate tests for an entire package::

                from myproject import core, utils, api
                MirrorTestConfigFile.L.create_test_modules([core, utils, api])

        See Also:
            generate_subclasses: Creates and orders subclasses
            validate_subclasses: Inherited method that instantiates config subclasses
        """
        subclasses = cls.generate_subclasses(modules)
        cls.validate_subclasses(subclasses)

    @classmethod
    def create_all_test_modules(cls) -> None:
        """Generate test files for all modules in the projects source package.

        Convenience method that retrieves all modules from the projects source package
        and creates test files for them. Useful for initializing tests for an
        entire package without manually listing modules.

        Example:
            Generate tests for all modules in the source package::

                MirrorTestConfigFile.L.create_all_test_modules()
        """
        src_package = import_module(PackageManager.I.package_name())
        cls.create_test_modules_for_package(src_package)

    @classmethod
    def create_test_modules_for_package(cls, package: ModuleType) -> None:
        """Generate test files for all modules in a specific source package.

        Retrieves all modules from the specified package and creates test files
        for them. Useful for initializing tests for a specific package without
        manually listing modules.

        Args:
            package: Source package to create test files for.

        Example:
            Generate tests for all modules in a specific package::

                import myproject.core
                MirrorTestConfigFile.L.create_test_modules_for_package(myproject.core)
        """
        logger.debug("Creating tests for package: %s", package.__name__)
        modules = (m for m, is_pkg in walk_package(package) if not is_pkg)
        cls.create_test_modules(modules)

    def test_func_name(self, func: Callable[..., Any]) -> str:
        """Get test function name for a source function.

        Args:
            func: Source function to get test function name for.

        Returns:
            Test function name with appropriate prefix.

        Example:
            >>> def my_function(): pass
            >>> test_func_name(my_function)
            'test_my_function'
        """
        return self.test_func_prefix() + unwrapped_obj(func).__name__

    def test_cls_name(self, cls: type) -> str:
        """Get test class name for a source class.

        Args:
            cls: Source class to get test class name for.

        Returns:
            Test class name with appropriate prefix.

        Example:
            >>> class MyClass: pass
            >>> test_cls_name(MyClass)
            'TestClass'
        """
        return self.test_cls_prefix() + cls.__name__

    def test_func_prefix(self) -> str:
        """Get test function prefix.

        Returns:
            The ``"test_"`` prefix string.
        """
        return "test_"

    def test_cls_prefix(self) -> str:
        """Get test class prefix.

        Returns:
            The ``"Test"`` prefix string.
        """
        return "Test"

    def test_module_docstring(self) -> str:
        """Get default docstring for test modules.

        Returns:
            Default docstring to use for test modules that lack one.
        """
        return '"""Test module."""\n'
