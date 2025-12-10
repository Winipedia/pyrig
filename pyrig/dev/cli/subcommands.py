"""Subcommands for the CLI.

They will be automatically imported and added to the CLI
IMPORTANT: All funcs in this file will be added as subcommands.
So best to define the logic elsewhere and just call it here in a wrapper.
"""

from pyrig.dev.artifacts.build import build_artifacts
from pyrig.src.git.github.repo.protect import protect_repository
from pyrig.src.project.create_root import make_project_root
from pyrig.src.project.init_project import init_project
from pyrig.src.project.make_inits import make_init_files
from pyrig.src.testing.create_tests import make_test_skeletons


def mkroot() -> None:
    """Creates the root of the project.

    This inits all ConfigFiles and creates __init__.py files for the src
    and tests package where they are missing. It does not overwrite any
    existing files.
    """
    make_project_root()


def mktests() -> None:
    """Create all test files for the project.

    This generates test skeletons for all functions and classes in the src
    package. It does not overwrite any existing tests.
    Tests are also automatically generated when missing by running pytest.
    """
    make_test_skeletons()


def mkinits() -> None:
    """Create all __init__.py files for the project.

    This creates __init__.py files for all packages and modules
    that are missing them. It does not overwrite any existing files.
    """
    make_init_files()


def init() -> None:
    """Set up the project.

    This is the setup command when you created the project from scratch.
    It will init all config files, create the root, create tests, and run
    all pre-commit hooks and tests.
    """
    init_project()


def build() -> None:
    """Build all artifacts.

    Invokes every subclass of Builder in the builder package.
    """
    build_artifacts()


def protect_repo() -> None:
    """Protect the repository.

    This will set secure repo settings and add a branch protection rulesets.
    """
    protect_repository()
