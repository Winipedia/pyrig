# CLI Documentation

The pyrig CLI system uses dynamic command discovery to automatically register commands from module functions, enabling both built-in commands and project-specific commands in packages that depend on pyrig.

## Documentation Pages

### [Commands](commands/index.md)
Documentation for all built-in pyrig commands:
- init - Complete project initialization
- mkroot - Create project structure
- mktests - Generate test skeletons
- mkinits - Create `__init__.py` files
- build - Build all artifacts
- protect-repo - Configure repository protection

### [Architecture](architecture.md)
Learn how the CLI system works internally, including:
- Entry point configuration and command registration flow
- Module name replacement for multi-package support
- Dependency graph for ecosystem-wide discovery
- Function discovery and import strategies

### [Subcommands](subcommands.md)
Define project-specific CLI commands:
- How to create new commands
- Command patterns and best practices
- Multi-package support
- Built-in commands reference

### [Shared Subcommands](shared-subcommands.md)
Create commands available across all packages in the pyrig ecosystem:
- Cross-package functionality
- Discovery through dependency graph
- Context-aware command implementation
- Command inheritance

## Quick Start

Run any pyrig command:
```bash
uv run pyrig init        # Complete project setup
uv run pyrig mkroot      # Create project structure
uv run pyrig build       # Build all artifacts
uv run pyrig version     # Display version
```

For packages that depend on pyrig:
```bash
uv run myapp <command>   # Run myapp-specific commands
uv run myapp version     # Shared commands work too
```

See [Commands](commands/index.md) for detailed documentation on each command.

## Global Options

All commands support global verbosity and quiet flags:

```bash
# Increase verbosity (can be repeated)
uv run pyrig -v build          # DEBUG level with level prefix
uv run pyrig -vv build         # DEBUG level with module names
uv run pyrig -vvv build        # DEBUG level with timestamps

# Quiet mode (only warnings and errors)
uv run pyrig -q build          # Suppress info messages
```

**Note**: Global options must come **before** the command name (e.g., `pyrig -v build`, not `pyrig build -v`).

See [Architecture](architecture.md) for technical details on how global options are implemented.

