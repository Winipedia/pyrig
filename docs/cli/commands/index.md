# Commands

pyrig provides CLI commands for project setup, testing, building, and repository management.

## Available Commands

- **[init](init.md)** - Complete project initialization
- **[mkroot](mkroot.md)** - Create project structure and config files
- **[mktests](mktests.md)** - Generate test skeletons
- **[mkinits](mkinits.md)** - Create `__init__.py` files
- **[build](build.md)** - Build all artifacts
- **[protect-repo](protect-repo.md)** - Configure repository protection

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
```

## Global Options

All commands support verbosity and quiet flags. See [CLI Architecture - Global Options](../architecture.md#global-options) for complete details on logging levels and usage.

## Command Discovery

All commands are automatically discovered from `dev/cli/subcommands.py`. Each function in this module becomes a CLI command.

For packages depending on pyrig, you can define your own commands in `myapp/dev/cli/subcommands.py`:

```bash
uv run myapp deploy    # Custom command defined in myapp
uv run myapp status    # Custom command defined in myapp
uv run myapp version   # Shared command available in all packages
```
