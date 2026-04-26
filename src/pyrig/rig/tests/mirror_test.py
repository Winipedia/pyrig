"""Mirror test configuration management for automatic test skeleton generation.

Ensures every source module, class, function and method has a test counterpart.
"""

import logging
from abc import abstractmethod
from collections.abc import Callable, Generator, Iterable
from importlib import import_module
from pathlib import Path
from types import ModuleType
from typing import Any, Self, cast

from pyrig.core.introspection.classes import (
    cls_methods,
    discard_parent_methods,
    module_classes,
)
from pyrig.core.introspection.functions import all_functions_from_module
from pyrig.core.introspection.inspection import (
    obj_qualname,
    sorted_by_def_line,
    unwrapped_obj,
)
from pyrig.core.introspection.modules import (
    import_module_with_file_fallback,
    module_has_docstring,
    reimport_module,
)
from pyrig.core.introspection.packages import all_modules_from_package
from pyrig.core.iterate import generator_has_items
from pyrig.core.strings import make_name_from_obj
from pyrig.rig import tests
from pyrig.rig.configs.base.config_file import ConfigList
from pyrig.rig.configs.base.package import PythonPackageConfigFile
from pyrig.rig.tools.package_manager import PackageManager
from pyrig.rig.tools.project_tester import ProjectTester
from pyrig.rig.utils.paths import module_name_as_root_path

logger = logging.getLogger(__name__)


class MirrorTestConfigFile(PythonPackageConfigFile):
    """Base class for creating test files that mirror source module structure.

    Analyzes a source module, identifies all functions, classes, and methods, then
    generates corresponding test skeletons in the appropriate test module. Detects
    which source elements lack tests and appends skeleton code without modifying
    existing test code.

    The complete workflow on instantiation:

    1. Derive the test file path from the source module's import path.
    2. Analyze the source module for all functions, classes, and methods.
    3. Compare against existing tests to find untested elements.
    4. Generate skeleton code for each missing test.
    5. Write the merged content (existing tests + new skeletons) to the test file.

    Subclasses must implement:
        mirror_module: Return the source module whose structure should be mirrored.

    Examples:
        Subclass for a specific module::

            class MyModuleMirrorTest(MirrorTestConfigFile):

                def mirror_module(self) -> ModuleType:
                    return my_module

        Dynamic subclass creation::

            subclass = MirrorTestConfigFile.L.generate_subclass(my_module)
            subclass()  # Creates the test file
    """

    @abstractmethod
    def mirror_module(self) -> ModuleType:
        """Return the source module whose structure will be mirrored in the test file.

        Must be implemented by every subclass. The returned module's functions,
        classes, and methods are inspected to determine which test skeletons to
        generate.

        Returns:
            The source module to mirror.
        """

    @classmethod
    def definition_package(cls) -> ModuleType:
        """Return the package where this ConfigFile subclass hierarchy is defined.

        Overrides the default (``pyrig.rig.configs``) to ``pyrig.rig.tests``,
        placing mirror-test subclasses in the testing infrastructure rather than in
        the configuration infrastructure.

        Returns:
            The ``pyrig.rig.tests`` package.
        """
        return tests

    @classmethod
    def concrete_subclasses(cls) -> Generator[type[Self], None, None]:
        """Yield dynamically generated subclasses for all source modules.

        Overrides the default discovery mechanism: instead of scanning for manually
        defined subclasses, creates one subclass per module returned by
        ``all_mirror_modules()``.

        Returns:
            Generator of dynamically created subclasses, one per source module.
        """
        return cls.generate_subclasses(cls.all_mirror_modules())

    def _dump(self, configs: ConfigList) -> None:
        """Write the test file and reimport the test module to pick up the new content.

        Extends the parent dump by reimporting the test module after writing. This
        clears the module cache so that subsequent introspection (e.g., by
        ``is_correct()``) reflects the newly written skeletons rather than the stale
        cached version.

        Args:
            configs: Lines of content to write to the test file.
        """
        super()._dump(configs)
        reimport_module(self.test_module())

    def stem(self) -> str:
        """Return the test file's base name without its extension.

        Returns:
            Filename stem (e.g., ``"test_utils"``).
        """
        return self.test_path().stem  # filename without extension

    def parent_path(self) -> Path:
        """Return the directory where the test file lives.

        Returns:
            Parent directory of the test file path.
        """
        return self.test_path().parent

    def lines(self) -> ConfigList:
        """Return the complete test module content as a list of lines.

        Delegates to ``test_module_content_with_skeletons()`` to produce the full
        content, which includes both existing tests and newly generated skeletons.

        Returns:
            All lines of the test module source, ready to be written to disk.
        """
        return self.split_lines(self.test_module_content_with_skeletons())

    def should_override_content(self) -> bool:
        """Instruct the parent class to replace file content entirely on each write.

        Returns ``True`` so that the parent's ``merge_configs()`` discards the raw
        file content and instead uses the output of ``lines()``, which already
        incorporates the existing tests plus new skeletons.

        Returns:
            Always ``True``.
        """
        return True

    def create_file(self) -> None:
        """Create the test file on disk and register it in ``sys.modules``."""
        super().create_file()
        import_module_with_file_fallback(self.path(), name=self.test_module_name())

    def is_correct(self) -> bool:
        """Return whether every source function and method has a corresponding test.

        Checks the source module for untested functions and classes with untested
        methods. Returns ``True`` only when both generators are empty.

        Returns:
            ``True`` if all functions and methods are covered; ``False`` otherwise.
        """
        return not (
            any(self.untested_func_names())
            or any(self.untested_class_and_method_names())
        )

    def merge_configs(self) -> ConfigList:
        """Return the full test module content without additional merging.

        The content returned by ``configs()`` (via ``lines()``) already integrates
        the existing file content with new skeletons, so no further merging is needed.

        Returns:
            The test module lines as produced by ``lines()``.
        """
        return self.configs()

    def test_module_name(self) -> str:
        """Return the fully qualified import name of the test module.

        Constructs the name by prepending the tests package name and prefixing each
        component of the source module's dotted name with the test module prefix.

        Returns:
            Dotted import path (e.g., ``"tests.test_mypackage.test_mymodule"``).
        """
        return ".".join(
            [ProjectTester.I.tests_package_name()]
            + [
                ProjectTester.I.test_module_prefix() + part
                for part in self.mirror_module().__name__.split(".")
            ]
        )

    def test_path(self) -> Path:
        """Return the filesystem path of the test module file.

        Converts the test module's import name to a relative filesystem path.

        Returns:
            Relative path to the test file
            (e.g., ``Path("tests/test_package/test_mod.py")``).
        """
        return module_name_as_root_path(self.test_module_name())

    def test_module(self) -> ModuleType:
        """Import and return the test module object.

        Uses a file-path fallback for modules that have not yet been added to
        ``sys.modules`` (e.g., immediately after the file is created).

        Returns:
            The imported test module.
        """
        return import_module_with_file_fallback(
            self.test_path(), name=self.test_module_name()
        )

    def test_module_content(self) -> str:
        """Return the current on-disk content of the test file as a string.

        Returns:
            Source code of the test file, or an empty string if the file does not
            exist yet.
        """
        return self.read_content()

    def test_module_content_with_skeletons(self) -> str:
        """Build the complete test module content with skeletons for untested code.

        Combines the existing file content with newly generated skeletons in four steps:

        1. Read the existing test module content from disk.
        2. Prepend a default module docstring if the module has none.
        3. Append function skeletons for every untested source function.
        4. Insert class and method skeletons for every untested source class.

        Returns:
            Full test module source ready to write to disk, preserving all existing
            test implementations.
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
        """Append function skeletons for all untested source functions.

        Args:
            test_module_content: Existing test module content to extend.

        Returns:
            Test module content with new function skeletons appended at the end.
        """
        return test_module_content + "".join(
            self.test_func_skeleton(name) for name in self.untested_func_names()
        )

    def untested_func_names(self) -> Generator[str, None, None]:
        """Yield test function names for functions that have no corresponding test.

        Compares the source module's functions against the test module's functions.
        Functions are sorted by their definition line so skeletons are appended in
        source order.

        Returns:
            Generator of expected test function names (e.g., ``"test_foo"``) for each
            source function that does not have a matching test function.
        """
        funcs = sorted_by_def_line(all_functions_from_module(self.mirror_module()))
        test_funcs = all_functions_from_module(self.test_module())

        supposed_test_func_names = (self.test_func_name(f) for f in funcs)
        actual_test_func_names = {obj_qualname(f) for f in test_funcs}

        return (f for f in supposed_test_func_names if f not in actual_test_func_names)

    def test_func_skeleton(self, test_func_name: str) -> str:
        '''Generate skeleton code for a test function.

        Creates a minimal test function that raises ``NotImplementedError``,
        marking it as pending implementation.

        Args:
            test_func_name: Name for the test function (e.g., ``"test_my_func"``).

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
        """Insert class and method skeletons for untested source classes.

        For each untested source class, either appends a full new test class with
        method skeletons, or inserts missing method skeletons into an existing test
        class body.

        The insertion uses string splitting on the class definition line. When the
        test class already exists in the content, new method skeletons are placed
        immediately after the class header. When the class does not exist yet, the
        full skeleton (header and methods) is appended to the content.

        Args:
            test_module_content: Existing test module content to extend.

        Returns:
            Test module content with all missing class and method skeletons inserted.
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
            # we simply insert the new class content into the parts
            module_content_parts.insert(1, test_cls_content)
            test_module_content = "".join(module_content_parts)

        return test_module_content

    def untested_class_and_method_names(
        self,
    ) -> Generator[tuple[str, Generator[str, None, None]], None, None]:
        """Yield test class/method pairs for source classes that have untested elements.

        Compares source classes and their methods against the test module. For each
        source class, computes the expected test class name and the expected test
        method names. A tuple is yielded when the test class is entirely absent or
        when at least one method is missing from an existing test class.

        Classes and their methods are processed in source definition order. Only
        methods defined directly on the class are considered; inherited methods are
        excluded.

        Returns:
            Generator of ``(test_class_name, missing_test_methods)`` tuples, where
            ``missing_test_methods`` is itself a generator of method name strings.
            Only classes with at least one untested element are included.
        """
        classes = sorted_by_def_line(module_classes(self.mirror_module()))
        test_classes = module_classes(self.test_module())

        class_to_methods = (
            (
                c,
                sorted_by_def_line(discard_parent_methods(c, cls_methods(c))),
            )
            for c in classes
        )
        test_class_to_test_methods = (
            (tc, (discard_parent_methods(tc, cls_methods(tc)))) for tc in test_classes
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
            test_class_name: Name for the test class (e.g., ``"TestMyClass"``).

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

        Creates a minimal test method that raises ``NotImplementedError``,
        marking it as pending implementation.

        Args:
            test_method_name: Name for the test method (e.g., ``"test_my_method"``).

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
        """Yield a dynamically created config subclass for each module.

        Convenience wrapper around ``generate_subclass()`` for batch processing.

        Args:
            modules: Source modules to create test config subclasses for.

        Returns:
            Generator yielding one subclass per module, in input order.
        """
        return (cls.generate_subclass(m) for m in modules)

    @classmethod
    def generate_subclass(cls, module: ModuleType) -> type[Self]:
        """Dynamically create a config subclass for a specific source module.

        Creates a new class at runtime that:

        1. Inherits from the current class (``MirrorTestConfigFile`` or a subclass).
        2. Implements ``mirror_module()`` to return the given module.
        3. Has a descriptive class name derived from the module name.

        This enables the config file machinery to be used without manually defining
        a subclass for each source module.

        Args:
            module: Source module that the new subclass will create tests for.

        Returns:
            Dynamically created subclass configured for the given module.

        Example:
            ::

                import myproject.utils
                subclass = MirrorTestConfigFile.L.generate_subclass(myproject.utils)
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
    def all_mirror_modules(cls) -> Generator[ModuleType, None, None]:
        """Yield all modules from the project's source package.

        Returns:
            Generator of every module in the package declared by the active
            ``PackageManager``.
        """
        package = import_module(PackageManager.I.package_name())
        return all_modules_from_package(package)

    def test_func_name(self, func: Callable[..., Any]) -> str:
        """Return the expected test function name for a given source function.

        Args:
            func: Source function whose test name to derive.

        Returns:
            Test function name with the ``"test_"`` prefix applied to the
            unwrapped function's ``__name__``
            (e.g., ``"test_my_function"`` for ``my_function``).
        """
        return self.test_func_prefix() + unwrapped_obj(func).__name__

    def test_cls_name(self, cls: type) -> str:
        """Return the expected test class name for a given source class.

        Args:
            cls: Source class whose test name to derive.

        Returns:
            Test class name with the ``"Test"`` prefix applied to the class's
            ``__name__`` (e.g., ``"TestMyClass"`` for ``MyClass``).
        """
        return self.test_cls_prefix() + cls.__name__

    def test_func_prefix(self) -> str:
        """Return the prefix used for test function names.

        Returns:
            ``"test_"``
        """
        return "test_"

    def test_cls_prefix(self) -> str:
        """Return the prefix used for test class names.

        Returns:
            ``"Test"``
        """
        return "Test"

    def test_module_docstring(self) -> str:
        """Return the default docstring used for newly created test modules.

        Returns:
            A minimal module docstring string, ready to prepend to an empty file.
        """
        return '"""Test module."""\n'
