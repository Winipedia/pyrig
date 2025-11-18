"""Subcommands for the CLI.

They will be automatically imported and added to the CLI
IMPORTANT: All funcs in this file will be added as subcommands.
So best to define the logic elsewhere and just call it here in a wrapper.
"""

from pyrig.dev.artifacts.build import build as build_cmd
from pyrig.src.git.github.repo.protect import (
    protect_repository as protect_repo_cmd,
)
from pyrig.src.project.create_root import create_root as create_root_cmd
from pyrig.src.project.init import init as init_cmd
from pyrig.src.testing.create_tests import create_tests as create_tests_cmd


def create_root() -> None:
    """Creates the root of the project.

    This inits all ConfigFiles and creates __init__.py files for the src
    and tests package where they are missing. It does not overwrite any
    existing files.
    """
    create_root_cmd()


def create_tests() -> None:
    """Create all test files for the project.

    This generates test skeletons for all functions and classes in the src
    package. It does not overwrite any existing tests.
    Tests are also automatically generated when missing by running pytest.
    """
    create_tests_cmd()


def init() -> None:
    """Set up the project.

    This is the setup command when you created the project from scratch.
    It will init all config files, create the root, create tests, and run
    all pre-commit hooks and tests.
    """
    init_cmd()


def build() -> None:
    """Build all artifacts.

    Invokes every subclass of Builder in the builder package.
    """
    build_cmd()


def protect_repo() -> None:
    """Protect the repository.

    This will set secure repo settings and add a branch protection rulesets.
    """
    protect_repo_cmd()
