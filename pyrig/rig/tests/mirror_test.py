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

            def src_module(self) -> ModuleType:
                return myproject.core

        CoreMirrorTest()  # Creates tests/test_myproject/test_core.py

    Batch process multiple modules::

        modules = [myproject.core, myproject.utils, myproject.api]
        MirrorTestConfigFile.I.create_test_modules(modules)

See Also:
    pyrig.rig.configs.base.py_package.PythonPackageConfigFile: Parent class
    pyrig.rig.cli.commands.create_tests: CLI command using this class
"""

import logging
from collections.abc import Callable
from functools import cache
from pathlib import Path
from types import ModuleType
from typing import Any, Self, cast, overload

from pyrig.rig import tests
from pyrig.rig.configs.base.py_package import PythonPackageConfigFile
from pyrig.src.modules.class_ import all_cls_from_module, all_methods_from_cls
from pyrig.src.modules.function import all_functions_from_module
from pyrig.src.modules.inspection import qualname_of_obj
from pyrig.src.modules.module import (
    default_module_content,
    import_module_with_file_fallback,
    import_obj_from_importpath,
    isolated_obj_name,
    make_obj_importpath,
    module_content_as_str,
    module_has_docstring,
)
from pyrig.src.modules.path import ModulePath
from pyrig.src.string_ import make_name_from_obj

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
        - `src_module`: Return the source module to mirror

    Methods for Batch Processing:
        - `make_subclasses_for_modules`: Create config subclasses for multiple modules
        - `make_subclass_for_module`: Create a config subclass for a single module
        - `create_test_modules`: Generate test files for multiple modules at once

    Examples:
        Subclass for a specific module::

            class MyModuleMirrorTest(MirrorTestConfigFile):

                def src_module(self) -> ModuleType:
                    return my_module

        Dynamic subclass creation::

            subclass = MirrorTestConfigFile.I.make_subclass_for_module(my_module)
            subclass()  # Triggers test file creation

    See Also:
        pyrig.rig.configs.base.py_package.PythonPackageConfigFile: Parent class
        pyrig.rig.cli.commands.create_tests.make_test_skeletons: CLI integration
    """

    def src_module(self) -> ModuleType:
        """Return the source module to mirror with tests.

        This abstract method must be implemented by subclasses to specify which
        module's structure should be analyzed and mirrored in the test file.
        It is not implemented as an abstract method to allow the .I property
        to work on the base class for dynamic subclass creation.

        Returns:
            The source module whose functions, classes, and methods will have
            corresponding test skeletons generated.
        """
        msg = "Subclasses must implement src_module()"
        raise NotImplementedError(msg)

    def filename(self) -> str:
        """Extract test filename from the derived test path.

        Returns:
            Test module filename without extension (e.g., "test_utils").
        """
        test_path = self.test_path()
        return test_path.stem  # filename without extension

    def parent_path(self) -> Path:
        """Get parent directory for the test file.

        Returns:
            Directory path where the test file will be created.
        """
        test_path = self.test_path()
        return test_path.parent

    def lines(self) -> list[str]:
        """Generate complete test module content with skeletons for untested code.

        Returns:
            Full test module source code including existing tests and new skeletons.
        """
        lines = self.test_module_content_with_skeletons().splitlines()
        # if last no empty new line, add one
        last_line = lines[-1]
        if last_line.strip():
            lines.append("")
        return lines

    def should_override_content(self) -> bool:
        """Enable content override mode for skeleton insertion.

        Returns:
            True to enable override mode, allowing lines() to provide
            the complete merged content (existing tests plus new skeletons).

        Note:
            The "override" refers to the parent class file-writing behavior.
            The actual content returned by lines() is additive -
            new skeletons are appended/inserted while preserving existing tests.
        """
        return True

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
        test_module_content = module_content_as_str(self.test_module())
        untested_funcs = [
            f for f in self.untested_func_names() if f not in test_module_content
        ]
        untested_classes = [
            c
            for c in self.untested_class_and_method_names()
            if ("class " + c) not in test_module_content
        ]
        untested_methods = [
            m
            for ms in self.untested_class_and_method_names().values()
            for m in ms
            if ("def " + m + "(") not in test_module_content
        ]
        return super().is_correct() or not (
            untested_funcs or untested_classes or untested_methods
        )

    def merge_configs(self) -> list[Any]:
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
        test_module_name = self.test_module_name()
        return ModulePath.module_name_to_relative_file_path(test_module_name)

    def test_module_name(self) -> str:
        """Get the fully qualified import name for the test module.

        Returns:
            Dotted import path (e.g., "tests.test_mypackage.test_mymodule").
        """
        return self.test_module_name_from_src_module(self.src_module())

    def test_module_name_from_src_module(self, src_module: ModuleType) -> str:
        """Convert source module to its corresponding test module import path.

        Applies test naming conventions: prepends "tests" package and adds
        appropriate prefixes to each path component.

        Args:
            src_module: Source module to derive test path from.

        Returns:
            Test module import path (e.g., "tests.test_package.test_mod").
        """
        return self.test_obj_importpath_from_obj(src_module)

    @classmethod
    @cache
    def test_module(cls) -> ModuleType:
        """Import and return the test module, creating it if necessary.

        Uses file-based fallback to handle cases where the test module doesn't
        exist yet - creates an empty module from the expected file path.

        Cached for performance - avoids repeated imports of the same module
        during test skeleton generation.

        If user wants to override they should overide _test_module, not this method,
        since this method is cached.

        Returns:
            The test module object, either imported or newly created.
        """
        return cls()._test_module()  # noqa: SLF001

    def _test_module(self) -> ModuleType:
        """Import and return the test module, creating it if necessary.

        Uses file-based fallback to handle cases where the test module doesn't
        exist yet - creates an empty module from the expected file path.

        Returns:
            The test module object, either imported or newly created.
        """
        return import_module_with_file_fallback(
            ModulePath.module_name_to_relative_file_path(self.test_module_name())
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
        test_module_content = module_content_as_str(self.test_module())
        # if module content has no docstring, add the default one
        if not module_has_docstring(self.test_module()):
            test_module_content = default_module_content() + test_module_content
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
        for test_func_name in self.untested_func_names():
            test_module_content += self.test_func_skeleton(test_func_name)
        return test_module_content

    @classmethod
    @cache
    def untested_func_names(cls) -> tuple[str, ...]:
        """Identify source functions that lack corresponding test functions.

        Compares functions in the source module against functions in the test
        module. For each source function, checks if a test function with the
        expected name (test_<function_name>) exists.

        Cached for performance - called multiple times during validation.

        If user wants to override they should overide _untested_func_names,
        not this method since this method is cached.

        Returns:
            Tuple of test function names that need to be created, using the
            test naming convention (e.g., ("test_foo", "test_bar")).

        Note:
            Logs debug information about the number and names of untested functions.
        """
        return cls()._untested_func_names()  # noqa: SLF001

    def _untested_func_names(self) -> tuple[str, ...]:
        """Identify source functions that lack corresponding test functions.

        Compares functions in the source module against functions in the test
        module. For each source function, checks if a test function with the
        expected name (test_<function_name>) exists.

        Returns:
            Tuple of test function names that need to be created, using the
            test naming convention (e.g., ("test_foo", "test_bar")).

        Note:
            Logs debug information about the number and names of untested functions.
        """
        funcs = all_functions_from_module(self.src_module())
        test_funcs = all_functions_from_module(self.test_module())

        supposed_test_func_names = [self.test_name_for_obj(f) for f in funcs]
        actual_test_func_names = [qualname_of_obj(f) for f in test_funcs]

        untested_func_names = tuple(
            f for f in supposed_test_func_names if f not in actual_test_func_names
        )

        logger.debug(
            "Found %d untested functions: %s",
            len(untested_func_names),
            untested_func_names,
        )
        return untested_func_names

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
        ) in test_class_to_method_names.items():
            test_cls_skeleton = self.test_class_skeleton(test_class_name)
            test_cls_content = test_cls_skeleton
            for test_method_name in test_method_names:
                test_cls_content += self.test_method_skeleton(test_method_name)

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
                raise ValueError(msg)
            # we simply insert the new class content into the parts
            module_content_parts.insert(1, test_cls_content)
            test_module_content = "".join(module_content_parts)

        return test_module_content

    @classmethod
    @cache
    def untested_class_and_method_names(cls) -> dict[str, tuple[str, ...]]:
        """Identify source classes and methods lacking corresponding tests.

        Performs a comprehensive comparison between source and test modules:
        1. Extracts all classes and their methods from the source module
        2. Extracts all test classes and their methods from the test module
        3. Maps source class/method names to expected test names
        4. Identifies missing test classes and missing test methods within
           existing test classes

        Cached for performance - called multiple times during validation.

        If user wants to override they should overide _untested_class_and_method_names,
        not this method since this method is cached.

        Returns:
            Dictionary mapping test class names to tuples of missing test method
            names. If a test class is entirely missing, it maps to a tuple of
            all its expected test method names. Returns empty dict if all
            classes and methods have tests.

        Example:
            Return value structure::

                {
                    "TestMyClass": ("test_method_one", "test_method_two"),
                }

        Note:
            Only considers methods defined directly on the class, excluding
            inherited methods from parent classes.
        """
        return cls()._untested_class_and_method_names()  # noqa: SLF001

    def _untested_class_and_method_names(self) -> dict[str, tuple[str, ...]]:
        """Identify source classes and methods lacking corresponding tests.

        Performs a comprehensive comparison between source and test modules:
        1. Extracts all classes and their methods from the source module
        2. Extracts all test classes and their methods from the test module
        3. Maps source class/method names to expected test names
        4. Identifies missing test classes and missing test methods within
           existing test classes

        Returns:
            Dictionary mapping test class names to tuples of missing test method
            names. If a test class is entirely missing, it maps to a tuple of
            all its expected test method names. Returns empty dict if all
            classes and methods have tests.

        Example:
            Return value structure::

                {
                    "TestMyClass": ("test_method_one", "test_method_two"),
                }

        Note:
            Only considers methods defined directly on the class, excluding
            inherited methods from parent classes.
        """
        classes = all_cls_from_module(self.src_module())
        test_classes = all_cls_from_module(self.test_module())

        class_to_methods = {
            c: all_methods_from_cls(c, exclude_parent_methods=True) for c in classes
        }
        test_class_to_test_methods = {
            tc: all_methods_from_cls(tc, exclude_parent_methods=True)
            for tc in test_classes
        }

        supposed_test_class_to_test_methods_names = {
            self.test_name_for_obj(c): [self.test_name_for_obj(m) for m in ms]
            for c, ms in class_to_methods.items()
        }
        actual_test_class_to_test_methods_names = {
            isolated_obj_name(tc): [isolated_obj_name(tm) for tm in tms]
            for tc, tms in test_class_to_test_methods.items()
        }

        untested_test_class_to_test_methods_names: dict[str, tuple[str, ...]] = {}
        for (
            supposed_test_class_name,
            supposed_test_methods_names,
        ) in supposed_test_class_to_test_methods_names.items():
            actual_test_methods_names = actual_test_class_to_test_methods_names.get(
                supposed_test_class_name, []
            )
            untested_test_methods_names = tuple(
                tmn
                for tmn in supposed_test_methods_names
                if tmn not in actual_test_methods_names
            )
            # add the test class name to the dict if there are untested methods
            # or if the test class is not in the test module at all
            if untested_test_methods_names or (
                supposed_test_class_name not in actual_test_class_to_test_methods_names
            ):
                untested_test_class_to_test_methods_names[supposed_test_class_name] = (
                    untested_test_methods_names
                )

        logger.debug(
            "Found %d untested classes: %s",
            len(untested_test_class_to_test_methods_names),
            untested_test_class_to_test_methods_names,
        )
        return untested_test_class_to_test_methods_names

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

    def make_subclasses_for_modules(
        self, modules: list[ModuleType]
    ) -> list[type[Self]]:
        """Create config subclasses for multiple modules.

        Convenience method for batch processing: creates a subclass for each
        module in input order. Priority-based ordering is handled later by
        ``validate_subclasses``.

        Args:
            modules: List of source modules to create test configs for.

        Returns:
            List of dynamically created subclasses, in input order.

        See Also:
            make_subclass_for_module: Creates individual subclasses
            validate_subclasses: Orders by priority and validates
        """
        return list(map(self.make_subclass_for_module, modules))

    def make_subclass_for_module(self, module: ModuleType) -> type[Self]:
        """Dynamically create a config subclass for a specific source module.

        Creates a new class at runtime that:
        1. Inherits from the current class (MirrorTestConfigFile or subclass)
        2. Implements src_module() to return the specified module
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
                subclass = MirrorTestConfigFile.I.make_subclass_for_module(
                    myproject.utils
                )
                # subclass.__name__ == "TestUtilsMirrorTestConfigFile"
                subclass()  # Creates tests/test_myproject/test_utils.py
        """
        test_module_name = self.test_module_name_from_src_module(module).split(".")[-1]

        test_cls_name = (
            make_name_from_obj(
                test_module_name, split_on="_", join_on="", capitalize=True
            )
            + self.__class__.__name__
        )

        def src_module(self: type[Self]) -> ModuleType:  # noqa: ARG001
            return module

        subclass = type(
            test_cls_name,
            (self.__class__,),
            {self.src_module.__name__: src_module},
        )
        return cast("type[Self]", subclass)

    def create_test_modules(self, modules: list[ModuleType]) -> None:
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
                MirrorTestConfigFile.I.create_test_modules([core, utils, api])

        See Also:
            make_subclasses_for_modules: Creates and orders subclasses
            validate_subclasses: Inherited method that instantiates config subclasses
        """
        subclasses = self.make_subclasses_for_modules(modules)
        self.validate_subclasses(*subclasses)

    @overload
    def obj_from_test_obj(self, test_obj: type) -> type: ...

    @overload
    def obj_from_test_obj(self, test_obj: Callable[..., Any]) -> Callable[..., Any]: ...

    @overload
    def obj_from_test_obj(self, test_obj: ModuleType) -> ModuleType: ...

    def obj_from_test_obj(
        self, test_obj: Callable[..., Any] | type | ModuleType
    ) -> Callable[..., Any] | type | ModuleType:
        """Get original object corresponding to test object.

        Dynamically imports the source object by reversing the test naming
        conventions to reconstruct the original import path.

        Args:
            test_obj: Test object (module, class, or function).

        Returns:
            Corresponding original object (same type as input).

        Raises:
            ImportError: If source object doesn't exist or can't be imported.
            AttributeError: If source object path is invalid.

        Example:
            >>> from tests.test_myapp.test_utils import test_calculate_sum
            >>> source_func = obj_from_test_obj(test_calculate_sum)
            >>> source_func.__name__
            'calculate_sum'
        """
        obj_importpath = self.obj_importpath_from_test_obj(test_obj)
        return import_obj_from_importpath(obj_importpath)

    @overload
    def test_obj_from_obj(self, obj: type) -> type: ...

    @overload
    def test_obj_from_obj(self, obj: Callable[..., Any]) -> Callable[..., Any]: ...

    @overload
    def test_obj_from_obj(self, obj: ModuleType) -> ModuleType: ...

    def test_obj_from_obj(self, obj: Callable[..., Any] | type | ModuleType) -> Any:
        """Get test object corresponding to original object.

        Dynamically imports the test object by applying test naming conventions
        to reconstruct the test import path.

        Args:
            obj: Original object (module, class, or function).

        Returns:
            Corresponding test object (same type as input).

        Raises:
            ImportError: If test object doesn't exist or can't be imported.
            AttributeError: If test object path is invalid.

        Example:
            >>> from myapp.utils import calculate_sum
            >>> test_func = test_obj_from_obj(calculate_sum)
            >>> test_func.__name__
            'test_calculate_sum'
        """
        test_obj_path = self.test_obj_importpath_from_obj(obj)
        return import_obj_from_importpath(test_obj_path)

    def test_obj_importpath_from_obj(
        self, obj: Callable[..., Any] | type | ModuleType
    ) -> str:
        """Create test import path from original object.

        Converts source object's import path to test naming conventions:
        prepends "tests" package and adds test prefixes to all components.
        It assumes classes start with a capital letter and modules with a lowercase.

        Args:
            obj: Original object (module, class, or function).

        Returns:
            Test import path (e.g., "tests.test_myapp.test_utils.test_calculate").

        Example:
            >>> from myapp.utils import calculate_sum
            >>> test_obj_importpath_from_obj(calculate_sum)
            'tests.test_myapp.test_utils.test_calculate_sum'
        """
        parts = make_obj_importpath(obj).split(".")
        test_name = self.test_name_for_obj(obj)
        test_parts = [
            (
                self.test_module_prefix()
                if part[0].islower()
                else self.test_class_prefix()
            )
            + part
            for part in parts[:-1]
        ]
        test_parts.append(test_name)
        test_parts.insert(0, self.tests_package_name())
        return ".".join(test_parts)

    def obj_importpath_from_test_obj(
        self,
        test_obj: Callable[..., Any] | type | ModuleType,
    ) -> str:
        """Create original import path from test object.

        Reverses test_obj_importpath_from_obj by removing "tests" prefix
        and stripping test prefixes from all components.

        Args:
            test_obj: Test object (module, class, or function).

        Returns:
            Original import path (e.g., "myapp.utils.calculate").

        Example:
            >>> from tests.test_myapp.test_utils import test_calculate_sum
            >>> obj_importpath_from_test_obj(test_calculate_sum)
            'myapp.utils.calculate_sum'
        """
        test_importpath = make_obj_importpath(test_obj)
        # remove tests prefix
        test_importpath = test_importpath.removeprefix(self.tests_package_name() + ".")
        test_parts = test_importpath.split(".")
        parts = [
            self.remove_test_prefix_from_test_name(test_name)
            for test_name in test_parts
        ]
        return ".".join(parts)

    def test_name_for_obj(self, obj: Callable[..., Any] | type | ModuleType) -> str:
        """Get test name for object based on type.

        Args:
            obj: Object to get test name for (ModuleType, type, or Callable).

        Returns:
            Test name with appropriate prefix.

        Example:
            >>> def my_function(): pass
            >>> test_name_for_obj(my_function)
            'test_my_function'
        """
        prefix = self.test_prefix_for_obj(obj)
        name = isolated_obj_name(obj)
        return prefix + name

    def remove_test_prefix_from_test_name(self, test_name: str) -> str:
        """Remove test prefix from test name.

        Args:
            test_name: Test name to remove prefix from.

        Returns:
            Test name without prefix.

        Example:
            >>> remove_test_prefix_from_test_name("test_my_function")
            'my_function'
        """
        for prefix in self.test_prefixes():
            if test_name.startswith(prefix):
                return test_name.removeprefix(prefix)
        return test_name

    def test_prefix_for_obj(self, obj: Callable[..., Any] | type | ModuleType) -> str:
        """Get appropriate test prefix for object based on type.

        Args:
            obj: Object to get prefix for (ModuleType, type, or Callable).

        Returns:
            Test prefix: "test_" for modules/functions, "Test" for classes.

        Example:
            >>> class MyClass: pass
            >>> test_prefix_for_obj(MyClass)
            'Test'
        """
        if isinstance(obj, ModuleType):
            return self.test_module_prefix()
        if isinstance(obj, type):
            return self.test_class_prefix()
        return self.test_func_prefix()

    def test_prefixes(self) -> tuple[str, ...]:
        """Get all test prefixes.

        Returns:
            Tuple of all test prefixes (function, class, and module).
        """
        return (
            self.test_func_prefix(),
            self.test_class_prefix(),
            self.test_module_prefix(),
        )

    def test_func_prefix(self) -> str:
        """Get test function prefix.

        Returns:
            The ``"test_"`` prefix string.
        """
        return "test_"

    def test_class_prefix(self) -> str:
        """Get test class prefix.

        Returns:
            The ``"Test"`` prefix string.
        """
        return "Test"

    def test_module_prefix(self) -> str:
        """Get test module prefix.

        Returns:
            The ``"test_"`` prefix string.
        """
        return "test_"

    def tests_package_name(self) -> str:
        """Get tests package name.

        Returns:
            The ``"tests"`` package name string.
        """
        return "tests"
