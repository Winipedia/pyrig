"""CLI package for pyrig and projects that depend on pyrig.

Provides the command-line infrastructure built on Typer, where commands are
discovered and registered at runtime rather than declared statically. Each
project's own commands come from its `subcommands` module, while
`shared_subcommands` commands are gathered from pyrig and every package that
depends on it, letting dependent projects extend the CLI without modifying
pyrig directly.
"""
