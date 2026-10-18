"""Generation of test skeletons for Python source modules.

Adds missing test functions and methods while preserving existing test code.
"""

import ast
from abc import abstractmethod
from collections.abc import Hashable, Iterator
from pathlib import Path
from types import ModuleType
from typing import Any, Self

from pyrig_runtime.core.introspection.classes import generate_cls

from pyrig.core.introspection.ast import cls_defs, func_defs, method_defs
from pyrig.core.iterate import deduplicate, iterator_has_items
from pyrig.core.strings import read_text_utf8, reformat_name
from pyrig.rig import tests
from pyrig.rig.configs.base.python import PythonPackageConfigFile
from pyrig.rig.tools.packages.manager import PackageManager
from pyrig.rig.tools.testing.project import ProjectTester


class MirrorTestConfigFile(PythonPackageConfigFile):
    """Configuration for a test module corresponding to one source module.

    Each subclass is bound to one source file. Its content includes tests for
    module-level functions and directly declared class methods, adding stubs
    for missing test names without replacing existing test implementations.

    Subclasses must implement:
        - `mirror_file`: Return the source file whose tests are managed.
    """

    @abstractmethod
    def mirror_file(self) -> Path:
        """Return the source file associated with this test configuration.

        Returns:
            Path to the source file whose test module is managed.
        """

    def mirror_tree(self) -> ast.Module:
        """Parse and return the source file's syntax tree."""
        return ast.parse(read_text_utf8(self.mirror_file()))

    def test_tree(self) -> ast.Module:
        """Parse and return the managed test file's syntax tree."""
        return ast.parse(self.read_content())

    @classmethod
    def merge_key(cls) -> Hashable:
        """Return the shared merge key for mirror-test configurations.

        Returns:
            The same key for every subclass.
        """
        return MirrorTestConfigFile.__name__

    def validate(self) -> bool:
        """Create the test file if it does not exist before validating.

        Returns:
            `True` if neither the file nor its dependencies needed updating once
            the file existed; otherwise `False`.
        """
        if not self.path().exists():
            self.create_file()
        return super().validate()

    def create_file(self) -> None:
        """Create the test file with its default module docstring."""
        super().create_file()
        self.write_content(self.test_module_docstring())

    def is_correct(self) -> bool:
        """Check whether each eligible source function and method has a test name.

        Returns:
            `True` if no expected test name is missing; otherwise `False`.
        """
        mirror_tree, test_tree = self.mirror_tree(), self.test_tree()
        return not (
            any(
                self.untested_func_names(
                    mirror_tree=mirror_tree,
                    test_tree=test_tree,
                ),
            )
            or any(
                self.untested_cls_and_method_names(
                    mirror_tree=mirror_tree,
                    test_tree=test_tree,
                ),
            )
        )

    def content(self) -> str:
        """Return the managed test content with missing test skeletons added.

        Returns:
            Test module source ready to be written to disk.
        """
        return self.test_file_content_with_skeletons()

    def merge_configs(self) -> list[Any]:
        """Return the required test module lines without merging in the file's lines.

        The required content already includes the existing test code, so no
        separate merge is performed.

        Returns:
            Lines of the test module to write.
        """
        return self.configs()

    def package_root(self) -> Path:
        """Return the root directory of the tests package."""
        return ProjectTester.I.package_root()

    def parent_path(self) -> Path:
        """Return the directory where the test file lives."""
        return self.test_path().parent

    def stem(self) -> str:
        """Return the test file's base name without its extension.

        Returns:
            Filename stem (e.g., `"test_utils"`).
        """
        return self.test_path().stem

    @classmethod
    def discovery_module(cls) -> ModuleType:
        """Return the `pyrig.rig.tests` package, scoping discovery to mirror tests.

        Returns:
            The `pyrig.rig.tests` package module.
        """
        return tests

    @classmethod
    def generate_subclass(cls, file: Path) -> type[Self]:
        """Create a config subclass bound to a source file.

        Args:
            file: Source file whose test module the subclass will manage.

        Returns:
            A subclass whose `mirror_file` method returns `file`.
        """
        test_cls_name = (
            reformat_name(
                file.stem,
                split_on="_",
                join_on="",
                capitalize=True,
            )
            + cls.__name__
        )

        def mirror_file(_self: Self) -> Path:
            """Return the source path captured when the subclass was created."""
            return file

        return generate_cls(
            name=test_cls_name,
            bases=(cls,),
            methods=(mirror_file,),
        )

    def test_path(self) -> Path:
        """Return the test file path corresponding to the source file.

        Returns:
            Path under the test package root.
        """
        return self.package_root() / Path(
            *(
                self.test_module_prefix() + part
                for part in self.mirror_file()
                .relative_to(PackageManager.I.source_root())
                .parts
            ),
        )

    def test_file_content_with_skeletons(self) -> str:
        """Add missing test skeletons to the existing test module content.

        Returns:
            Test module source with existing tests retained.
        """
        test_file_content = self.read_content()
        mirror_tree, test_tree = self.mirror_tree(), self.test_tree()
        test_file_content = self.test_file_content_with_func_skeletons(
            test_file_content,
            mirror_tree=mirror_tree,
            test_tree=test_tree,
        )
        return self.test_file_content_with_cls_skeletons(
            test_file_content,
            mirror_tree=mirror_tree,
            test_tree=test_tree,
        )

    def test_file_content_with_func_skeletons(
        self,
        test_file_content: str,
        mirror_tree: ast.Module,
        test_tree: ast.Module,
    ) -> str:
        """Append stubs for source functions without matching test names.

        Args:
            test_file_content: Existing test module content to extend.
            mirror_tree: Syntax tree of the source module.
            test_tree: Syntax tree of the test module.

        Returns:
            Test module content with the missing function stubs appended.
        """
        return test_file_content + "".join(
            self.test_func_skeleton(name)
            for name in self.untested_func_names(
                mirror_tree=mirror_tree,
                test_tree=test_tree,
            )
        )

    def untested_func_names(
        self,
        mirror_tree: ast.Module,
        test_tree: ast.Module,
    ) -> Iterator[str]:
        """Yield test names missing for module-level source functions.

        Args:
            mirror_tree: Syntax tree of the source module.
            test_tree: Syntax tree of the test module.

        Yields:
            Expected test function names in source definition order.
        """
        funcs = func_defs(mirror_tree)
        test_funcs = func_defs(test_tree)

        supposed_test_func_names = deduplicate(self.test_func_name(f) for f in funcs)
        actual_test_func_names = {f.name for f in test_funcs}

        return (f for f in supposed_test_func_names if f not in actual_test_func_names)

    def test_func_skeleton(self, test_func_name: str) -> str:
        """Build a test function stub that raises `NotImplementedError`.

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

    def test_file_content_with_cls_skeletons(
        self,
        test_file_content: str,
        mirror_tree: ast.Module,
        test_tree: ast.Module,
    ) -> str:
        """Add missing method stubs to existing or newly created test classes.

        Args:
            test_file_content: Existing test module content to extend.
            mirror_tree: Syntax tree of the source module.
            test_tree: Syntax tree of the test module.

        Returns:
            Test module content with the missing method stubs added.
        """
        for (
            test_cls_name,
            test_method_names,
            test_cls_source,
        ) in self.untested_cls_and_method_names(
            mirror_tree=mirror_tree,
            test_tree=test_tree,
        ):
            test_cls_source_exists = test_cls_source is not None

            test_cls_skeleton = (
                f"{test_cls_source}\n"
                if test_cls_source_exists
                else self.test_cls_skeleton(test_cls_name)
            )

            test_cls_content = test_cls_skeleton + "".join(
                self.test_method_skeleton(name) for name in test_method_names
            )
            if test_cls_source_exists:
                test_file_content = test_file_content.replace(
                    test_cls_source.strip(),
                    test_cls_content.strip(),
                    1,
                )
                continue
            test_file_content += test_cls_content

        return test_file_content

    def untested_cls_and_method_names(
        self,
        mirror_tree: ast.Module,
        test_tree: ast.Module,
    ) -> Iterator[tuple[str, Iterator[str], str | None]]:
        """Yield test classes and method names that are missing tests.

        Only methods defined directly on module-level classes are considered.
        Classes without missing method tests are omitted.

        Args:
            mirror_tree: Syntax tree of the source module.
            test_tree: Syntax tree of the test module.

        Yields:
            Tuples containing the expected test class name, its missing method
            test names, and the existing test class source or `None`.

        Note:
            Consume each tuple's method-name iterator before requesting the
            next tuple.
        """
        classes = cls_defs(mirror_tree)
        test_classes = cls_defs(test_tree)

        cls_to_methods = (
            (
                cls,
                method_defs(cls),
            )
            for cls in classes
        )
        test_cls_to_test_methods = (
            (
                test_cls,
                method_defs(test_cls),
            )
            for test_cls in test_classes
        )

        existing_test_cls_to_test_method_names = {
            test_cls.name: (test_cls, {method.name for method in methods})
            for test_cls, methods in test_cls_to_test_methods
        }

        for (
            mirror_cls,
            mirror_methods,
        ) in cls_to_methods:
            expected_test_cls_name = self.test_cls_name(mirror_cls)
            expected_test_method_names = deduplicate(
                self.test_func_name(m) for m in mirror_methods
            )

            test_cls, existing_test_method_names = (
                existing_test_cls_to_test_method_names.get(
                    expected_test_cls_name,
                    (None, ()),
                )
            )
            missing_test_method_names = (
                test_method_name
                for test_method_name in expected_test_method_names
                if test_method_name not in existing_test_method_names
            )
            has_missing_test_methods, missing_test_method_names = iterator_has_items(
                missing_test_method_names,
            )
            if not has_missing_test_methods:
                continue

            test_cls_source = (
                ast.get_source_segment(self.read_content(), test_cls)
                if test_cls is not None
                else None
            )

            yield (
                expected_test_cls_name,
                missing_test_method_names,
                test_cls_source,
            )

    def test_cls_skeleton(self, test_cls_name: str) -> str:
        """Build a test class stub.

        Args:
            test_cls_name: Name for the test class (e.g., `"TestMyClass"`).

        Returns:
            Python source code for the skeleton test class definition.
        """
        return f'''

class {test_cls_name}:
    """Test class."""
'''

    def test_method_skeleton(self, test_method_name: str) -> str:
        """Build a test method stub that raises `NotImplementedError`.

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

    def test_func_name(self, func: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
        """Return the expected test function name for a given source function.

        Args:
            func: Source function whose test name to derive.

        Returns:
            Test function name (e.g., `"test_my_func"` for `my_func`).
        """
        return self.test_func_prefix() + func.name

    def test_cls_name(self, cls: ast.ClassDef) -> str:
        """Return the expected test class name for a given source class.

        Args:
            cls: Source class whose test name to derive.

        Returns:
            Test class name (e.g., `"TestMyClass"` for `MyClass`).
        """
        return self.test_cls_prefix() + cls.name

    def test_func_prefix(self) -> str:
        """Return `"test_"`, the prefix used for test function names."""
        return "test_"

    def test_cls_prefix(self) -> str:
        """Return `"Test"`, the prefix used for test class names."""
        return "Test"

    def test_module_prefix(self) -> str:
        """Return `"test_"`, the prefix used for test module names."""
        return "test_"

    def test_module_docstring(self) -> str:
        """Return the default test module docstring with a trailing newline."""
        return '"""Test module."""\n'
