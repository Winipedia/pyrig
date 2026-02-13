"""module."""

from pyrig.src.singleton import Singleton


class MyTestSingleton(Singleton):
    """Test class."""


class TestSingletonMeta:
    """Test class."""

    def test___call__(self) -> None:
        """Test method."""
        s1 = MyTestSingleton()
        s2 = MyTestSingleton()
        assert s1 is s2, "Expected both instances to be the same"

    def test_clear(self) -> None:
        """Test method."""
        s1 = MyTestSingleton()
        s1.__class__.clear()
        s2 = MyTestSingleton()
        assert s1 is not s2, "Expected cleared instance to be different"


class TestSingleton:
    """Test class."""
