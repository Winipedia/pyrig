"""Factory fixtures for testing pyrig components.

This module provides factory fixtures that wrap ConfigFile and Builder
classes to use temporary directories during testing. All fixtures defined
under the fixtures package are automatically registered via pytest_plugins.

Example:
    Using the config_file_factory::

        def test_my_config(config_file_factory):
            TestConfig = config_file_factory(MyConfigFile)
            # TestConfig.get_path() now returns a path in tmp_path
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
    """Create a factory for ConfigFile subclasses using temporary paths.

    This factory wraps any ConfigFile subclass to redirect get_path() to
    tmp_path, enabling isolated testing without affecting real config files.

    Args:
        tmp_path: Pytest's temporary directory fixture.

    Returns:
        A factory function that takes a ConfigFile subclass and returns
        a wrapped version using tmp_path.

    Example:
        TestConfig = config_file_factory(PyprojectConfigFile)
        assert str(tmp_path) in str(TestConfig.get_path())
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
    """Create a factory for Builder subclasses using temporary paths.

    This factory wraps any Builder subclass to redirect get_artifacts_dir()
    to tmp_path, enabling isolated testing of artifact generation.

    Args:
        tmp_path: Pytest's temporary directory fixture.

    Returns:
        A factory function that takes a Builder subclass and returns
        a wrapped version using tmp_path.

    Example:
        TestBuilder = builder_factory(MyBuilder)
        assert str(tmp_path) in str(TestBuilder.get_artifacts_dir())
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
