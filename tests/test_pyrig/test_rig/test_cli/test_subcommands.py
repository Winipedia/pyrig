"""module."""

from collections.abc import Callable
from typing import Any

from pyrig.rig.cli.commands.build_artifacts import build_artifacts
from pyrig.rig.cli.commands.init_project import init_project
from pyrig.rig.cli.commands.make_fixture import make_fixture
from pyrig.rig.cli.commands.make_inits import make_init_files
from pyrig.rig.cli.commands.make_resources import make_resources
from pyrig.rig.cli.commands.make_root import make_project_root
from pyrig.rig.cli.commands.make_subclass import make_subclass
from pyrig.rig.cli.commands.make_subcommand import make_subcommand
from pyrig.rig.cli.commands.make_tests import make_tests
from pyrig.rig.cli.commands.protect_repo import protect_repository
from pyrig.rig.cli.commands.remove_pycache import remove_pycache
from pyrig.rig.cli.commands.scratch import run_scratch_file
from pyrig.rig.cli.subcommands import (
    build,
    init,
    mkcmd,
    mkfixture,
    mkinits,
    mkroot,
    mktests,
    protect_repo,
    resources,
    rmpyc,
    scratch,
    subcls,
)


def test_mkroot(
    command_works: Callable[[Callable[..., Any]], None],
    command_calls_function: Callable[[Callable[..., Any], Callable[..., Any]], None],
) -> None:
    """Test function."""
    command_works(mkroot)
    command_calls_function(mkroot, make_project_root)


def test_mktests(
    command_works: Callable[[Callable[..., Any]], None],
    command_calls_function: Callable[[Callable[..., Any], Callable[..., Any]], None],
) -> None:
    """Test function."""
    command_works(mktests)
    command_calls_function(mktests, make_tests)


def test_mkinits(
    command_works: Callable[[Callable[..., Any]], None],
    command_calls_function: Callable[[Callable[..., Any], Callable[..., Any]], None],
) -> None:
    """Test function."""
    command_works(mkinits)
    command_calls_function(mkinits, make_init_files)


def test_init(
    command_works: Callable[[Callable[..., Any]], None],
    command_calls_function: Callable[[Callable[..., Any], Callable[..., Any]], None],
) -> None:
    """Test function."""
    command_works(init)
    command_calls_function(init, init_project)


def test_build(
    command_works: Callable[[Callable[..., Any]], None],
    command_calls_function: Callable[[Callable[..., Any], Callable[..., Any]], None],
) -> None:
    """Test function."""
    command_works(build)
    command_calls_function(build, build_artifacts)


def test_protect_repo(
    command_works: Callable[[Callable[..., Any]], None],
    command_calls_function: Callable[[Callable[..., Any], Callable[..., Any]], None],
) -> None:
    """Test function."""
    command_works(protect_repo)
    command_calls_function(protect_repo, protect_repository)


def test_scratch(
    command_works: Callable[[Callable[..., Any]], None],
    command_calls_function: Callable[[Callable[..., Any], Callable[..., Any]], None],
) -> None:
    """Test function."""
    command_works(scratch)
    command_calls_function(scratch, run_scratch_file)


def test_rmpyc(
    command_works: Callable[[Callable[..., Any]], None],
    command_calls_function: Callable[[Callable[..., Any], Callable[..., Any]], None],
) -> None:
    """Test function."""
    command_works(rmpyc)
    command_calls_function(rmpyc, remove_pycache)


def test_mkcmd(
    command_works: Callable[[Callable[..., Any]], None],
    command_calls_function: Callable[[Callable[..., Any], Callable[..., Any]], None],
) -> None:
    """Test function."""
    command_works(mkcmd)
    command_calls_function(mkcmd, make_subcommand)


def test_subcls(
    command_works: Callable[[Callable[..., Any]], None],
    command_calls_function: Callable[[Callable[..., Any], Callable[..., Any]], None],
) -> None:
    """Test function."""
    command_works(subcls)
    command_calls_function(subcls, make_subclass)


def test_mkfixture(
    command_works: Callable[[Callable[..., Any]], None],
    command_calls_function: Callable[[Callable[..., Any], Callable[..., Any]], None],
) -> None:
    """Test function."""
    command_works(mkfixture)
    command_calls_function(mkfixture, make_fixture)


def test_resources(
    command_works: Callable[[Callable[..., Any]], None],
    command_calls_function: Callable[[Callable[..., Any], Callable[..., Any]], None],
) -> None:
    """Test function."""
    command_works(resources)
    command_calls_function(resources, make_resources)
