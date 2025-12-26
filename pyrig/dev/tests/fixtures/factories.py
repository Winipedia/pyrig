"""Factory fixtures for creating test instances of ConfigFile and Builder classes.

This module provides factory fixtures that create test-safe versions of
ConfigFile and Builder classes by redirecting their file system operations to
pytest's temporary directories. This enables isolated testing without affecting
real configuration files or build artifacts.

The factories work by creating dynamic subclasses that override path-related
methods to use `tmp_path` instead of the actual file system locations. This
ensures that:

- Tests don't modify real configuration files
- Build artifacts are created in isolated temporary directories
- Tests can run in parallel without conflicts
- Test cleanup is automatic (pytest removes tmp_path after tests)

Fixtures:
    config_file_factory: Factory for creating test versions of ConfigFile
        subclasses that use tmp_path for file operations.

    builder_factory: Factory for creating test versions of Builder subclasses
        that use tmp_path for artifact output.

How It Works:
    Both factories use the same pattern:
    1. Accept a base class (ConfigFile or Builder subclass)
    2. Create a dynamic subclass that inherits from the base class
    3. Override the path-related method (get_path() or get_artifacts_dir())
    4. Return the test-safe subclass

    The returned subclass behaves identically to the original class except that
    all file operations are redirected to tmp_path.

Example:
    Testing a ConfigFile subclass::

        def test_my_config(config_file_factory):
            '''Test MyConfigFile without affecting real files.'''
            TestConfig = config_file_factory(MyConfigFile)

            # TestConfig.get_path() returns path in tmp_path
            config_path = TestConfig.get_path()
            assert "tmp" in str(config_path)

            # Safe to write without affecting real config
            TestConfig.write_content("test content")

    Testing a Builder subclass::

        def test_my_builder(builder_factory):
            '''Test MyBuilder without affecting real artifacts.'''
            TestBuilder = builder_factory(MyBuilder)

            # TestBuilder.get_artifacts_dir() returns path in tmp_path
            artifacts_dir = TestBuilder.get_artifacts_dir()
            assert "tmp" in str(artifacts_dir)

            # Safe to build without affecting real dist/
            TestBuilder()  # Builds to tmp_path

See Also:
    pyrig.dev.configs.base.base.ConfigFile: Base class for configuration files
    pyrig.dev.builders.base.base.Builder: Base class for artifact builders
    pytest.TempPathFactory: Pytest's temporary directory mechanism
"""

from collections.abc import Callable
from pathlib import Path

import pytest

from pyrig.dev.builders.base.base import Builder
from pyrig.dev.configs.base.base import ConfigFile


@pytest.fixture
def config_file_factory[T: ConfigFile](
    tmp_path: Path,
) -> Callable[[type[T]], type[T]]:
    """Provide a factory for creating test-safe ConfigFile subclasses.

    This function-scoped fixture returns a factory function that creates
    test-safe versions of ConfigFile subclasses. The factory wraps any
    ConfigFile subclass to redirect `get_path()` to pytest's tmp_path,
    enabling isolated testing without affecting real configuration files.

    The factory creates a dynamic subclass that:
    - Inherits all behavior from the original ConfigFile subclass
    - Overrides `get_path()` to return a path within tmp_path
    - Preserves the original path structure relative to tmp_path
    - Allows safe read/write operations without side effects

    Args:
        tmp_path: Pytest's temporary directory fixture. Automatically provided
            by pytest for each test function. The directory is unique per test
            and is automatically cleaned up after the test completes.

    Returns:
        A factory function with signature `(type[T]) -> type[T]` that takes a
        ConfigFile subclass and returns a test-safe subclass. The returned
        subclass can be used exactly like the original class, but all file
        operations are redirected to tmp_path.

    Example:
        Basic usage::

            def test_config_file(config_file_factory):
                '''Test PyprojectConfigFile safely.'''
                TestConfig = config_file_factory(PyprojectConfigFile)

                # Path is in tmp_path
                config_path = TestConfig.get_path()
                assert "tmp" in str(config_path)

                # Safe to write
                TestConfig.write_content("test content")
                assert TestConfig.get_path().exists()

        Testing multiple config files::

            def test_multiple_configs(config_file_factory):
                '''Test multiple config files in isolation.'''
                TestPyproject = config_file_factory(PyprojectConfigFile)
                TestMain = config_file_factory(MainConfigFile)

                # Each has its own path in tmp_path
                assert TestPyproject.get_path() != TestMain.get_path()

    Note:
        - The factory is function-scoped, so each test gets a fresh tmp_path
        - The returned subclass is a new class, not an instance
        - All class methods and attributes are preserved
        - The original ConfigFile subclass is not modified

    See Also:
        pyrig.dev.configs.base.base.ConfigFile: Base class for configuration files
        builder_factory: Similar factory for Builder subclasses
    """

    def _make_test_config(
        base_class: type[T],
    ) -> type[T]:
        """Create a test config class that uses tmp_path.

        Args:
            base_class: The ConfigFile subclass to wrap.

        Returns:
            A subclass with get_path() redirected to tmp_path.
        """

        class TestConfigFile(base_class):  # type: ignore [misc, valid-type]
            """Test config file with tmp_path override."""

            @classmethod
            def get_path(cls) -> Path:
                """Get the path to the config file in tmp_path.

                Returns:
                    Path within tmp_path.
                """
                path = super().get_path()
                return Path(tmp_path / path)

        return TestConfigFile  # ty:ignore[invalid-return-type]

    return _make_test_config


@pytest.fixture
def builder_factory[T: Builder](tmp_path: Path) -> Callable[[type[T]], type[T]]:
    """Provide a factory for creating test-safe Builder subclasses.

    This function-scoped fixture returns a factory function that creates
    test-safe versions of Builder subclasses. The factory wraps any Builder
    subclass to redirect `get_artifacts_dir()` to pytest's tmp_path, enabling
    isolated testing of artifact generation without affecting real build outputs.

    The factory creates a dynamic subclass that:
    - Inherits all behavior from the original Builder subclass
    - Overrides `get_artifacts_dir()` to return a path within tmp_path
    - Preserves the artifacts directory name (e.g., "dist")
    - Allows safe build operations without side effects

    Args:
        tmp_path: Pytest's temporary directory fixture. Automatically provided
            by pytest for each test function. The directory is unique per test
            and is automatically cleaned up after the test completes.

    Returns:
        A factory function with signature `(type[T]) -> type[T]` that takes a
        Builder subclass and returns a test-safe subclass. The returned subclass
        can be used exactly like the original class, but all artifact output is
        redirected to tmp_path.

    Example:
        Basic usage::

            def test_builder(builder_factory):
                '''Test MyBuilder safely.'''
                TestBuilder = builder_factory(MyBuilder)

                # Artifacts dir is in tmp_path
                artifacts_dir = TestBuilder.get_artifacts_dir()
                assert "tmp" in str(artifacts_dir)

                # Safe to build
                TestBuilder()  # Creates artifacts in tmp_path
                assert artifacts_dir.exists()

        Testing PyInstaller builder::

            def test_pyinstaller_builder(builder_factory):
                '''Test PyInstallerBuilder without affecting dist/.'''
                TestBuilder = builder_factory(MyPyInstallerBuilder)

                # Build to tmp_path
                TestBuilder()

                # Verify artifacts created
                artifacts = list(TestBuilder.get_artifacts_dir().iterdir())
                assert len(artifacts) > 0

    Note:
        - The factory is function-scoped, so each test gets a fresh tmp_path
        - The returned subclass is a new class, not an instance
        - All class methods and attributes are preserved
        - The original Builder subclass is not modified
        - Instantiating the returned class triggers the build process

    See Also:
        pyrig.dev.builders.base.base.Builder: Base class for artifact builders
        config_file_factory: Similar factory for ConfigFile subclasses
    """

    def _make_test_builder(base_class: type[T]) -> type[T]:
        """Create a test builder class that uses tmp_path.

        Args:
            base_class: The Builder subclass to wrap.

        Returns:
            A subclass with get_artifacts_dir() redirected to tmp_path.
        """

        class TestBuilder(base_class):  # type: ignore [misc, valid-type]
            """Test builder with tmp_path override."""

            @classmethod
            def get_artifacts_dir(cls) -> Path:
                """Get the artifacts directory in tmp_path.

                Returns:
                    Path within tmp_path.
                """
                return Path(tmp_path / cls.ARTIFACTS_DIR_NAME)

        return TestBuilder  # ty:ignore[invalid-return-type]

    return _make_test_builder
