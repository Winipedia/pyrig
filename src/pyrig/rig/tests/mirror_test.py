"""Automatic generation of test skeletons that mirror the source code structure.

Ensures every module, class, function, and method in the project has a
corresponding test counterpart, without overwriting tests that already exist.
"""

import logging
import re
from abc import abstractmethod
from collections.abc import Iterable, Iterator
from importlib import import_module
from pathlib import Path
from types import FunctionType, MethodType, ModuleType
from typing import Any, Self

from pyrig_runtime.core.introspection.functions import (
    filter_module_functions,
)
from pyrig_runtime.core.introspection.inspection import obj_members, unwrap_obj

from pyrig.core.introspection.classes import (
    cls_methods,
    discard_parent_methods,
    filter_module_classes,
    generate_class,
)
from pyrig.core.introspection.inspection import (
    def_line_sorted,
)
from pyrig.core.introspection.modules import (
    import_module_with_file_fallback,
    leaf_module_name,
)
from pyrig.core.introspection.packages import discover_modules
from pyrig.core.introspection.paths import module_name_as_path
from pyrig.core.iterate import iterator_has_items
from pyrig.core.strings import reformat_name
from pyrig.rig import tests
from pyrig.rig.configs.base.package import PythonPackageConfigFile
from pyrig.rig.tools.package_manager import PackageManager
from pyrig.rig.tools.testers.project import ProjectTester

logger = logging.getLogger(__name__)


class MirrorTestConfigFile(PythonPackageConfigFile):
    """Config file for a test module that mirrors one source module's structure.

    Each concrete subclass is bound to a single source module. Its content
    appends test skeletons for any function, class, or method in that source
    module that has no corresponding test yet, leaving existing test code
    untouched.

    Subclasses must implement:
        - `mirror_module`: Return the source module whose structure should be
          mirrored.
    """

    @abstractmethod
    def mirror_module(self) -> ModuleType:
        """Return the source module whose structure will be mirrored in the test file.

        Returns:
            The source module to mirror.
        """

    def create_file(self) -> None:
        """Create the test file on disk and register it in `sys.modules`."""
        super().create_file()
        self.write_content(self.test_module_docstring())
        import_module_with_file_fallback(self.path(), name=self.test_module_name())

    def is_correct(self) -> bool:
        """Check whether every source function and method has a corresponding test.

        Returns:
            `True` if no source function or method is missing a test; `False`
            otherwise.
        """
        module, test_module, module_members, test_module_members = (
            self.modules_and_members()
        )
        return not (
            any(
                self.untested_func_names(
                    module=module,
                    test_module=test_module,
                    module_members=module_members,
                    test_module_members=test_module_members,
                )
            )
            or any(
                self.untested_class_and_method_names(
                    module=module,
                    test_module=test_module,
                    module_members=module_members,
                    test_module_members=test_module_members,
                )
            )
        )

    def lines(self) -> list[Any]:
        """Return the complete test module content as a list of lines.

        Returns:
            All lines of the test module source, ready to be written to disk.
        """
        return self.split_lines(self.test_module_content_with_skeletons())

    def merge_configs(self) -> list[Any]:
        """Return the full test module content, already merged with existing content.

        Returns:
            The complete test module lines, ready to write to disk.
        """
        return self.configs()

    def package_root(self) -> Path:
        """Return the root directory of the tests package."""
        return ProjectTester.I.package_root()

    def parent_path(self) -> Path:
        """Return the directory where the test file lives.

        Returns:
            Parent directory of the test file path.
        """
        return self.test_path().parent

    def stem(self) -> str:
        """Return the test file's base name without its extension.

        Returns:
            Filename stem (e.g., `"test_utils"`).
        """
        return self.test_path().stem

    @classmethod
    def concrete_subclasses(cls) -> Iterator[type[Self]]:
        """Yield a dynamically generated subclass for every module in the project.

        Yields:
            One dynamically created subclass per source module.
        """
        return cls.generate_subclasses(cls.mirror_modules())

    @classmethod
    def discovery_module(cls) -> ModuleType:
        """Return the `pyrig.rig.tests` package, scoping discovery to mirror tests.

        Returns:
            The `pyrig.rig.tests` package module.
        """
        return tests

    @classmethod
    def generate_subclass(cls, module: ModuleType) -> type[Self]:
        """Dynamically create a config subclass bound to a specific source module.

        The new subclass inherits from `cls` and implements `mirror_module` to
        return `module`. Its class name is `cls`'s name prefixed with the last
        component of `module`'s dotted name, converted from snake_case to
        PascalCase.

        Args:
            module: Source module that the new subclass will create tests for.

        Returns:
            Dynamically created subclass configured for the given module.

        Example:
            Given a module named `myproject.utils`, calling this on
            `MirrorTestConfigFile` produces a subclass named
            `"UtilsMirrorTestConfigFile"`.
        """
        test_cls_name = (
            reformat_name(
                leaf_module_name(module),
                split_on="_",
                join_on="",
                capitalize=True,
            )
            + cls.__name__
        )

        def mirror_module(_self: Self) -> ModuleType:
            """Return the source module captured at subclass creation time."""
            return module

        return generate_class(
            name=test_cls_name,
            bases=(cls,),
            methods=(mirror_module,),
        )

    @classmethod
    def generate_subclasses(cls, modules: Iterable[ModuleType]) -> Iterator[type[Self]]:
        """Yield a dynamically created config subclass for each module.

        Args:
            modules: Source modules to create test config subclasses for.

        Yields:
            One subclass per module, in input order.
        """
        return (cls.generate_subclass(m) for m in modules)

    @classmethod
    def mirror_modules(cls) -> Iterator[ModuleType]:
        """Yield every module in the project's source package.

        Yields:
            Each module in the package declared by the active `PackageManager`.
        """
        return discover_modules(import_module(PackageManager.I.package_name()))

    def test_path(self) -> Path:
        """Return the filesystem path of the test module file.

        Returns:
            Path to the test file, relative to the project root
            (e.g., `Path("tests/test_package/test_mod.py")`).
        """
        return self.source_root() / module_name_as_path(self.test_module_name())

    def test_module_name(self) -> str:
        """Return the fully qualified import name of the test module.

        Each component of the source module's dotted name is individually
        prefixed, and the result is nested under the tests package.

        Returns:
            Dotted import path (e.g., `"tests.test_mypackage.test_mymodule"`).
        """
        return ".".join(
            [ProjectTester.I.package_name()]
            + [
                self.test_module_prefix() + part
                for part in self.mirror_module().__name__.split(".")
            ]
        )

    def test_module_content_with_skeletons(self) -> str:
        """Build the complete test module content with skeletons for untested code.

        Returns:
            Full test module source ready to write to disk, preserving all existing
            test implementations.
        """
        test_module_content = self.read_content()
        module, test_module, module_members, test_module_members = (
            self.modules_and_members()
        )
        test_module_content = self.test_module_content_with_func_skeletons(
            test_module_content,
            module=module,
            test_module=test_module,
            module_members=module_members,
            test_module_members=test_module_members,
        )
        return self.test_module_content_with_class_skeletons(
            test_module_content,
            module=module,
            test_module=test_module,
            module_members=module_members,
            test_module_members=test_module_members,
        )

    def modules_and_members(
        self,
    ) -> tuple[ModuleType, ModuleType, tuple[Any], tuple[Any]]:
        """Return the source and test modules along with their members.

        Returns:
            A tuple containing:
                - The source module to mirror.
                - The test module corresponding to the source module.
                - Tuple of members of the source module.
                - Tuple of members of the test module.
        """
        module, test_module = self.mirror_module(), self.module()
        return (
            module,
            test_module,
            tuple(obj_members(module)),
            tuple(obj_members(test_module)),
        )

    def test_module_content_with_func_skeletons(
        self,
        test_module_content: str,
        module: ModuleType,
        test_module: ModuleType,
        module_members: Iterable[Any],
        test_module_members: Iterable[Any],
    ) -> str:
        """Append function skeletons for all untested source functions.

        Args:
            test_module_content: Existing test module content to extend.
            module: The source module to mirror.
            test_module: The test module corresponding to the source module.
            module_members: Members of the source module.
            test_module_members: Members of the test module.

        Returns:
            Test module content with new function skeletons appended at the end.
        """
        return test_module_content + "".join(
            self.test_func_skeleton(name)
            for name in self.untested_func_names(
                module=module,
                test_module=test_module,
                module_members=module_members,
                test_module_members=test_module_members,
            )
        )

    def untested_func_names(
        self,
        module: ModuleType,
        test_module: ModuleType,
        module_members: Iterable[Any],
        test_module_members: Iterable[Any],
    ) -> Iterator[str]:
        """Yield test function names for functions that have no corresponding test.

        Names are yielded in the source function's definition order.

        Args:
            module: The source module to mirror.
            test_module: The test module corresponding to the source module.
            module_members: Members of the source module.
            test_module_members: Members of the test module.

        Yields:
            Expected test function name (e.g., `"test_foo"`) for each source
            function that has no matching test function.
        """
        funcs = def_line_sorted(filter_module_functions(module, module_members))
        test_funcs = filter_module_functions(test_module, test_module_members)

        supposed_test_func_names = (self.test_func_name(unwrap_obj(f)) for f in funcs)
        actual_test_func_names = {unwrap_obj(f).__name__ for f in test_funcs}

        return (f for f in supposed_test_func_names if f not in actual_test_func_names)

    def test_func_skeleton(self, test_func_name: str) -> str:
        """Generate skeleton code for a test function.

        The skeleton is a standalone function that raises `NotImplementedError`,
        marking it as pending implementation.

        Args:
            test_func_name: Name for the test function (e.g., `"test_my_func"`).

        Returns:
            Python source code for the skeleton test function.
        """
        return f'''

def {test_func_name}() -> None:
    """Test function."""
    raise {NotImplementedError.__name__}
'''

    def test_module_content_with_class_skeletons(
        self,
        test_module_content: str,
        module: ModuleType,
        test_module: ModuleType,
        module_members: Iterable[Any],
        test_module_members: Iterable[Any],
    ) -> str:
        """Insert class and method skeletons for untested source classes.

        For each untested source class, method skeletons are placed inside the
        existing test class body if one is already present in the content, or
        into a newly appended test class otherwise.

        Args:
            test_module_content: Existing test module content to extend.
            module: The source module to mirror.
            test_module: The test module corresponding to the source module.
            module_members: Members of the source module.
            test_module_members: Members of the test module.

        Returns:
            Test module content with all missing class and method skeletons inserted.
        """
        for (
            test_class_name,
            test_method_names,
        ) in self.untested_class_and_method_names(
            module=module,
            test_module=test_module,
            module_members=module_members,
            test_module_members=test_module_members,
        ):
            test_cls_skeleton = self.extract_test_class_skeleton_from_content(
                test_module_content,
                test_class_name=test_class_name,
                default=self.test_class_skeleton(test_class_name),
            )
            test_cls_content = test_cls_skeleton + "".join(
                self.test_method_skeleton(name) for name in test_method_names
            )
            parts = test_module_content.split(test_cls_skeleton)
            parts.insert(1, test_cls_content)
            test_module_content = "".join(parts)

        return test_module_content

    def extract_test_class_skeleton_from_content(
        self, test_module_content: str, test_class_name: str, default: str
    ) -> str:
        """Extract the skeleton of a specific test class from the test module content.

        Args:
            test_module_content: The full test module content to search.
            test_class_name: The name of the test class whose skeleton to extract.
            default: The value to return if the class skeleton is not found.

        Returns:
            The matched class skeleton string if found; `default` otherwise.
        """
        pattern = self.class_skeleton_pattern(test_class_name)
        match = pattern.search(test_module_content)
        return match.group(0) if match is not None else default

    def class_skeleton_pattern(self, test_class_name: str) -> re.Pattern[str]:
        """Return a regex pattern that matches the skeleton of a specific test class.

        The pattern matches the class definition line followed by any
        triple-quoted docstring, using either quote style, in place of the
        default skeleton docstring.

        Args:
            test_class_name: The name of the test class whose skeleton to build a
                pattern for.

        Returns:
            Compiled regex pattern matching the class skeleton.
        """
        cls_skeleton = self.test_class_skeleton(test_class_name)
        pattern_str = cls_skeleton.replace(
            self.test_class_skeleton_docstring(),
            r"(?:\"\"\".*?\"\"\"|\'\'\'.*?\'\'\')",
        )
        return re.compile(pattern_str, flags=re.DOTALL)

    def untested_class_and_method_names(
        self,
        module: ModuleType,
        test_module: ModuleType,
        module_members: Iterable[Any],
        test_module_members: Iterable[Any],
    ) -> Iterator[tuple[str, Iterator[str]]]:
        """Yield test class/method pairs for source classes that have untested methods.

        Only methods defined directly on a source class are considered; inherited
        methods are excluded. A source class is omitted entirely if it has no
        methods of its own or if every one of its methods already has a test.

        Classes are yielded in source definition order.

        Args:
            module: The source module to mirror.
            test_module: The test module corresponding to the source module.
            module_members: Members of the source module.
            test_module_members: Members of the test module.

        Yields:
            `(test_class_name, missing_test_methods)` tuples, where
            `missing_test_methods` is itself an iterator of method name strings.

        Note:
            Each yielded inner iterator must be fully consumed before advancing
            to the next tuple; otherwise its remaining items are filtered
            against a later class's methods instead of its own.
        """
        classes = def_line_sorted(filter_module_classes(module, module_members))
        test_classes = filter_module_classes(test_module, test_module_members)

        class_to_methods = (
            (
                c,
                def_line_sorted(discard_parent_methods(c, cls_methods(c))),
            )
            for c in classes
        )
        test_class_to_test_methods = (
            (tc, (discard_parent_methods(tc, cls_methods(tc)))) for tc in test_classes
        )

        supposed_test_class_to_test_methods_names = (
            (
                self.test_cls_name(unwrap_obj(c)),
                (self.test_func_name(unwrap_obj(m)) for m in ms),
            )
            for c, ms in class_to_methods
        )
        actual_test_class_to_test_methods_names = {
            unwrap_obj(tc).__name__: {unwrap_obj(tm).__name__ for tm in tms}
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
            has_untested_methods, untested_test_methods_names = iterator_has_items(
                untested_test_methods_names
            )
            if has_untested_methods:
                logger.debug("Class %s has untested methods", supposed_test_class_name)
                yield supposed_test_class_name, untested_test_methods_names

    def test_class_skeleton(self, test_class_name: str) -> str:
        """Generate skeleton code for a test class.

        The skeleton is a standalone class definition with a docstring and no
        methods.

        Args:
            test_class_name: Name for the test class (e.g., `"TestMyClass"`).

        Returns:
            Python source code for the skeleton test class definition.
        """
        return f"""

class {test_class_name}:
    {self.test_class_skeleton_docstring()}
"""

    def test_class_skeleton_docstring(self) -> str:
        """Return the default docstring for a skeleton test class.

        Returns:
            A minimal test class docstring string.
        """
        return '"""Test class."""'

    def test_method_skeleton(self, test_method_name: str) -> str:
        """Generate skeleton code for a test method.

        The skeleton is an instance method that raises `NotImplementedError`,
        marking it as pending implementation.

        Args:
            test_method_name: Name for the test method (e.g., `"test_my_method"`).

        Returns:
            Python source code for the skeleton test method, indented for
            placement inside a class body.
        """
        return f'''
    def {test_method_name}(self) -> None:
        """Test method."""
        raise {NotImplementedError.__name__}
'''

    def test_func_name(self, func: FunctionType | MethodType) -> str:
        """Return the expected test function name for a given source function.

        Args:
            func: Source function whose test name to derive.

        Returns:
            Test function name (e.g., `"test_my_function"` for `my_function`).
        """
        return self.test_func_prefix() + func.__name__

    def test_cls_name(self, cls: type) -> str:
        """Return the expected test class name for a given source class.

        Args:
            cls: Source class whose test name to derive.

        Returns:
            Test class name (e.g., `"TestMyClass"` for `MyClass`).
        """
        return self.test_cls_prefix() + cls.__name__

    def test_func_prefix(self) -> str:
        """Return the prefix used for test function names.

        Returns:
            `"test_"`.
        """
        return "test_"

    def test_cls_prefix(self) -> str:
        """Return the prefix used for test class names.

        Returns:
            `"Test"`.
        """
        return "Test"

    def test_module_prefix(self) -> str:
        """Return the prefix used for test module names.

        Returns:
            `"test_"`.
        """
        return "test_"

    def test_module_docstring(self) -> str:
        """Return the default docstring used for newly created test modules.

        Returns:
            A minimal module docstring string, ready to prepend to an empty file.
        """
        return '"""Test module."""\n'
