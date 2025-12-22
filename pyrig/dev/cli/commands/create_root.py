"""Project structure creation utilities.

This module provides the `create_root` function which generates all
configuration files and directory structure for a pyrig project.
It delegates to the ConfigFile system to discover and initialize
all registered config file types.
"""

from pyrig.dev.configs.base.base import ConfigFile
from pyrig.dev.configs.git.gitignore import GitIgnoreConfigFile
from pyrig.dev.configs.licence import LicenceConfigFile
from pyrig.dev.configs.pyproject import PyprojectConfigFile
from pyrig.dev.configs.python.builders_init import BuildersInitConfigFile
from pyrig.dev.configs.python.configs_init import ConfigsInitConfigFile
from pyrig.dev.configs.python.main import MainConfigFile
from pyrig.dev.configs.testing.fixtures_init import FixturesInitConfigFile
from pyrig.dev.configs.testing.zero_test import ZeroTestConfigFile


def make_project_root(*, priority: bool = False) -> None:
    """Create all configuration files and project structure.

    Discovers all ConfigFile subclasses and initializes each one,
    creating the complete project structure including:
        - pyproject.toml
        - GitHub workflows
        - Pre-commit configuration
        - Ruff/mypy configuration
        - Source and test directory structure

    This is the implementation for the `pyrig create-root` command.
    """
    if priority:
        init_config_files(get_priority_config_files())
        return
    init_all_config_files()


def init_all_config_files() -> None:
    """Initialize all discovered ConfigFile subclasses.

    Initializes files in order: priority files first, then ordered
    files, then all remaining files.
    """
    init_config_files(get_priority_config_files())
    init_config_files(get_ordered_config_files())
    init_config_files(get_unordered_config_files())


def init_config_files(config_files: list[type[ConfigFile]]) -> None:
    """Initialize the given config files."""
    for config_file in config_files:
        config_file()


def get_priority_config_files() -> list[type[ConfigFile]]:
    """Get config files that must be initialized first.

    These files are required by other config files or the build
    process and must exist before other initialization can proceed.

    Returns:
        List of ConfigFile types in priority order.
    """
    return [
        GitIgnoreConfigFile,
        PyprojectConfigFile,
        LicenceConfigFile,
        MainConfigFile,
        ConfigsInitConfigFile,
        BuildersInitConfigFile,
        ZeroTestConfigFile,
        FixturesInitConfigFile,
    ]


def get_ordered_config_files() -> list[type[ConfigFile]]:
    """Get config files that must be initialized in a specific order.

    These files have dependencies on each other and must be
    initialized after priority files but before general files.

    Returns:
        List of ConfigFile types in initialization order.
    """
    return []


def get_unordered_config_files() -> list[type[ConfigFile]]:
    """Get all remaining config files.

    These files have no dependencies on each other and can be
    initialized in any order after priority and ordered files.

    Returns:
        List of ConfigFile types.
    """
    all_config_files = ConfigFile.get_all_subclasses()
    priority_and_ordered = get_priority_config_files() + get_ordered_config_files()
    return [cf for cf in all_config_files if cf not in priority_and_ordered]
