# Commands

pyrig provides CLI commands for project setup, testing, building, and repository
management.

## Available Commands

- **[init](init.md)** - Complete project initialization
- **[mkroot](mkroot.md)** - Create project structure and config files
- **[mktests](mktests.md)** - Generate test skeletons
- **[mkinits](mkinits.md)** - Create `__init__.py` files
- **[build](build.md)** - Build all artifacts
- **[protect-repo](protect-repo.md)** - Configure repository protection
- **version** - Display the current project's version (shared command)

## Quick Reference

```bash
# Complete project setup (first time)
uv run pyrig init

# Create/update project structure
uv run pyrig mkroot

# Generate test files
uv run pyrig mktests

# Create __init__.py files
uv run pyrig mkinits

# Build artifacts
uv run pyrig build

# Protect repository
uv run pyrig protect-repo

# Show version
uv run pyrig version
```

## Global Options

All commands support verbosity and quiet flags. See
[CLI Architecture - Global Options](../architecture.md#global-options) for
complete details on logging levels and usage.

## Command Discovery

Commands are automatically discovered from three sources:

1. **Main entry point**: `main()` from `<package>.main`
2. **Project-specific commands**: Public functions from
   `<package>.rig.cli.subcommands`
3. **Shared commands**: Public functions from
   `<package>.rig.cli.shared_subcommands` across the dependency chain

For packages depending on pyrig, you can define your own commands in
`myapp/rig/cli/subcommands.py` (project-specific) or
`myapp/rig/cli/shared_subcommands.py` (shared across dependents):

```bash
uv run myapp deploy    # Project-specific command
uv run myapp version   # Shared command from dependency chain
```
