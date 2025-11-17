"""module for the following module path (maybe truncated).

tests.test_py_dev.test_modules.test_class_
"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from functools import wraps
from typing import Any, ClassVar

from pytest_mock import MockFixture

from py_dev.utils.modules.class_ import (
    get_all_cls_from_module,
    get_all_methods_from_cls,
    get_all_nonabstract_subclasses,
    get_all_subclasses,
    init_all_nonabstract_subclasses,
)
from py_dev.utils.testing.assertions import assert_with_msg


def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorate a function for testing purposes."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        """Execute the wrapped function."""
        return func(*args, **kwargs)

    return wrapper


# Test classes for get_all_methods_from_cls
class ParentClass:
    """Parent class for testing inheritance."""

    class_var: ClassVar[str] = "parent_class_var"

    def parent_method(self) -> str:
        """Parent method."""
        return "parent_method"

    @staticmethod
    def parent_static_method() -> str:
        """Parent static method."""
        return "parent_static_method"

    @classmethod
    def parent_class_method(cls) -> str:
        """Parent class method."""
        return "parent_class_method"

    @property
    def parent_property(self) -> str:
        """Parent property."""
        return "parent_property"


class TestClass(ParentClass):
    """Test class for method extraction."""

    class_var: ClassVar[str] = "test_class_var"

    def instance_method(self) -> str:
        """Instance method."""
        return "instance_method"

    @staticmethod
    def static_method() -> str:
        """Return a static method value."""
        return "static_method"

    @classmethod
    def class_method(cls) -> str:
        """Class method."""
        return "class_method"

    @property
    def prop(self) -> str:
        """Property method."""
        return "property"

    def _private_method(self) -> str:
        """Private method."""
        return "private_method"

    @decorator
    def decorated_method(self) -> str:
        """Decorate with @decorator."""
        return "decorated_method"


class DecoratedClass:
    """Class with decorated methods for testing."""

    @decorator
    def decorated_method(self) -> str:
        """Return a decorated method value."""
        return "decorated_method"


class AbstractParent(ABC):
    """Abstract parent class for testing."""

    @abstractmethod
    def abstract_method(self) -> str:
        """Abstract method that must be implemented."""


class ConcreteChild(AbstractParent):
    """Concrete implementation of AbstractParent."""

    def __init__(self) -> None:
        """Initialize ConcreteChild."""
        super().__init__()

    def abstract_method(self) -> str:
        """Implement the abstract method."""
        return "concrete_implementation"


class AnotherAbstractChild(AbstractParent):
    """Another abstract child that doesn't implement the method."""

    @abstractmethod
    def another_abstract_method(self) -> str:
        """Another abstract method."""


def test_get_all_methods_from_cls() -> None:
    """Test func for get_all_methods_from_cls."""
    # Test case 1: Get all methods excluding inherited methods
    methods = get_all_methods_from_cls(TestClass, exclude_parent_methods=True)

    # assert __annotate__ is not considered a method (3.14 introduces this injection)
    assert_with_msg(
        "__annotate__" not in [m.__name__ for m in methods if hasattr(m, "__name__")],
        "Expected __annotate__ not to be considered a method",
    )

    # expected methods in order of definition
    expected_methods = [
        TestClass.instance_method,
        TestClass.static_method,
        TestClass.class_method,
        TestClass.prop,
        TestClass._private_method,  # noqa: SLF001
        TestClass.decorated_method,
    ]
    assert_with_msg(
        methods == expected_methods,
        f"Expected methods {expected_methods}, got {methods}",
    )

    # Test case 2: Get all methods including inherited methods
    methods = get_all_methods_from_cls(TestClass, exclude_parent_methods=False)

    # expected methods in order of definition
    expected_methods = [
        ParentClass.parent_method,
        ParentClass.parent_static_method,
        TestClass.parent_class_method,  # bound by accessed class
        ParentClass.parent_property,
        TestClass.instance_method,
        TestClass.static_method,
        TestClass.class_method,
        TestClass.prop,
        TestClass._private_method,  # noqa: SLF001
        TestClass.decorated_method,
    ]
    assert_with_msg(
        methods == expected_methods,
        f"Expected methods {expected_methods}, got {methods}",
    )


def test_get_all_cls_from_module() -> None:
    """Test func for get_all_cls_from_module."""
    # use this file as the module
    module = test_get_all_cls_from_module.__module__

    classes = get_all_cls_from_module(module)

    # expected classes in order of definition
    expected_classes: list[type] = [
        ParentClass,
        TestClass,
        DecoratedClass,
        AbstractParent,
        ConcreteChild,
        AnotherAbstractChild,
    ]
    expected_classes_names: list[str] = [c.__name__ for c in expected_classes]
    classes_names = [c.__name__ for c in classes]
    assert_with_msg(
        classes_names == expected_classes_names,
        f"Expected classes {expected_classes_names}, got {classes_names}",
    )


def test_get_all_subclasses() -> None:
    """Test func for get_all_subclasses."""
    # Test with ParentClass - should find TestClass as subclass
    subclasses = get_all_subclasses(ParentClass)

    assert_with_msg(
        TestClass in subclasses,
        f"Expected TestClass to be in subclasses of ParentClass, got {subclasses}",
    )

    # Test with TestClass - should have no subclasses
    subclasses = get_all_subclasses(TestClass)

    assert_with_msg(
        len(subclasses) == 0,
        f"Expected no subclasses for TestClass, got {subclasses}",
    )


def test_get_all_nonabstract_subclasses() -> None:
    """Test func for get_all_nonabstract_subclasses."""
    # Test with ParentClass - should find TestClass as non-abstract subclass
    subclasses = get_all_nonabstract_subclasses(ParentClass)

    assert_with_msg(
        TestClass in subclasses,
        f"Expected TestClass to be in non-abstract subclasses, got {subclasses}",
    )

    # Test with TestClass - should have no subclasses
    subclasses = get_all_nonabstract_subclasses(TestClass)

    assert_with_msg(
        len(subclasses) == 0,
        f"Expected no non-abstract subclasses for TestClass, got {subclasses}",
    )

    # Test with abstract class - should only find concrete implementations
    subclasses = get_all_nonabstract_subclasses(AbstractParent)

    assert_with_msg(
        ConcreteChild in subclasses,
        f"Expected ConcreteChild in non-abstract subclasses, got {subclasses}",
    )

    assert_with_msg(
        AnotherAbstractChild not in subclasses,
        f"Expected AnotherAbstractChild NOT in non-abstract subclasses, "
        f"got {subclasses}",
    )


def test_init_all_nonabstract_subclasses(mocker: MockFixture) -> None:
    """Test func for init_all_nonabstract_subclasses."""
    # spy on __init__ of ConcreteChild
    spy = mocker.spy(ConcreteChild, ConcreteChild.__init__.__name__)

    init_all_nonabstract_subclasses(AbstractParent)

    assert_with_msg(
        spy.call_count == 1,
        f"Expected __init__ of ConcreteChild to be called once, got {spy.call_count}",
    )
