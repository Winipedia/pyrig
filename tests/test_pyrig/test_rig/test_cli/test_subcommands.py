"""module."""

from collections.abc import Callable
from typing import Any

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


def test_mkroot(command_works: Callable[[Callable[..., Any]], None]) -> None:
    """Test function."""
    command_works(mkroot)


def test_mktests(command_works: Callable[[Callable[..., Any]], None]) -> None:
    """Test function."""
    command_works(mktests)


def test_mkinits(command_works: Callable[[Callable[..., Any]], None]) -> None:
    """Test function."""
    command_works(mkinits)


def test_init(command_works: Callable[[Callable[..., Any]], None]) -> None:
    """Test function."""
    command_works(init)


def test_build(command_works: Callable[[Callable[..., Any]], None]) -> None:
    """Test function."""
    command_works(build)


def test_protect_repo(command_works: Callable[[Callable[..., Any]], None]) -> None:
    """Test function."""
    command_works(protect_repo)


def test_scratch(command_works: Callable[[Callable[..., Any]], None]) -> None:
    """Test function."""
    command_works(scratch)


def test_rmpyc(command_works: Callable[[Callable[..., Any]], None]) -> None:
    """Test function."""
    command_works(rmpyc)


def test_mkcmd(command_works: Callable[[Callable[..., Any]], None]) -> None:
    """Test function."""
    command_works(mkcmd)


def test_subcls(command_works: Callable[[Callable[..., Any]], None]) -> None:
    """Test function."""
    command_works(subcls)


def test_mkfixture(command_works: Callable[[Callable[..., Any]], None]) -> None:
    """Test function."""
    command_works(mkfixture)


def test_resources(command_works: Callable[[Callable[..., Any]], None]) -> None:
    """Test function."""
    command_works(resources)
