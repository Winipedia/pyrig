"""CLI package for pyrig and projects that depend on pyrig.

Provides the complete command-line infrastructure built on Typer, with dynamic
command discovery and registration across the package dependency chain. Commands
are automatically discovered from project-specific and shared subcommand modules,
enabling dependent projects to extend the CLI without modifying pyrig directly.
"""
