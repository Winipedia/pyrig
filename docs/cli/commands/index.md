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

All commands support verbosity and quiet flags:

```bash
# Increase verbosity (specify before command)
uv run pyrig -v init           # DEBUG level
uv run pyrig -vv build         # DEBUG with module names
uv run pyrig -vvv mktests      # DEBUG with timestamps

# Quiet mode
uv run pyrig -q build          # Only warnings and errors
```

See [CLI Architecture](../architecture.md#global-options) for details on logging levels.

## Command Discovery

All commands are automatically discovered from `dev/cli/subcommands.py`. Each function in this module becomes a CLI command.

For packages depending on pyrig, you can define your own commands in `myapp/dev/cli/subcommands.py`:
```bash
uv run myapp deploy    # Custom command defined in myapp
uv run myapp status    # Custom command defined in myapp
uv run myapp version   # Shared command available in all packages
```

