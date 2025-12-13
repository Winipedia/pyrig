"""Subcommands for the CLI.

They will be automatically imported and added to the CLI
IMPORTANT: All funcs in this file will be added as subcommands.
So best to define the logic elsewhere and just call it here in a wrapper.
"""


def mkroot() -> None:
    """Creates the root of the project.

    This inits all ConfigFiles and creates __init__.py files for the src
    and tests package where they are missing. It does not overwrite any
    existing files.
    """
    from pyrig.dev.cli.commands.create_root import make_project_root  # noqa: PLC0415

    make_project_root()


def mktests() -> None:
    """Create all test files for the project.

    This generates test skeletons for all functions and classes in the src
    package. It does not overwrite any existing tests.
    Tests are also automatically generated when missing by running pytest.
    """
    from pyrig.dev.cli.commands.create_tests import make_test_skeletons  # noqa: PLC0415

    make_test_skeletons()


def mkinits() -> None:
    """Create all __init__.py files for the project.

    This creates __init__.py files for all packages and modules
    that are missing them. It does not overwrite any existing files.
    """
    from pyrig.dev.cli.commands.make_inits import make_init_files  # noqa: PLC0415

    make_init_files()


def init() -> None:
    """Set up the project.

    This is the setup command when you created the project from scratch.
    It will init all config files, create the root, create tests, and run
    all pre-commit hooks and tests.
    """
    from pyrig.dev.cli.commands.init_project import init_project  # noqa: PLC0415

    init_project()


def build() -> None:
    """Build all artifacts.

    Invokes every subclass of Builder in the builder package.
    """
    from pyrig.dev.cli.commands.build_artifacts import build_artifacts  # noqa: PLC0415

    build_artifacts()


def protect_repo() -> None:
    """Protect the repository.

    This will set secure repo settings and add a branch protection rulesets.
    """
    from pyrig.dev.cli.commands.protect_repo import protect_repository  # noqa: PLC0415

    protect_repository()
