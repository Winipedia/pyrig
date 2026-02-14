# mkroot

Creates the project root structure by validating all config files (including
`__init__.py` files for package structure).

## Usage

```bash
# Create all config files
uv run pyrig mkroot

# Create only priority config files
uv run pyrig mkroot --priority

# With verbose output to see which files are created/updated
uv run pyrig -v mkroot
```

## Options

- `--priority` - Only create priority config files (essential files needed
  before dependency installation)

## What It Does

The `mkroot` command discovers and initializes all `ConfigFile` subclasses
across the project and its dependencies. Config files are processed in priority
order to ensure dependencies between files are respected.

### Priority Config Files

When using `--priority`, only essential config files are created—those required
before installing dependencies or running other initialization steps (e.g.,
`LICENSE`, `pyproject.toml`, package `__init__.py` files).

### All Config Files

Without `--priority`, all config files are created or updated, including project
metadata, workflows, git configuration, documentation structure, and test setup.

See [Configs Documentation](../../configs/index.md) for the complete list.

## Behavior

- **Idempotent** - Safe to run multiple times
- **Creates files** that do not exist
- **Updates existing files** - Adds missing configuration and overwrites
incorrect values to match expected configuration
- **Respects opt-out** - Empty files are skipped (user opted out)

## When to Use

Use `mkroot` when:

- Regenerating config files after updates
- Adding new `ConfigFile` subclasses to a project
- Ensuring project structure is up to date

Use `mkroot --priority` when:

- During initial project setup (before installing dependencies)
- As part of `pyrig init` (runs automatically)

## Autouse Fixture

The `assert_root_is_correct` autouse fixture runs before tests and triggers this
command if any config files are incorrect. See
[Autouse Fixtures](../../tests/autouse.md#assert_root_is_correct) for details.

## Related

- [Configuration Architecture](../../configs/architecture.md) - Priority system
  and initialization details
- [Configs Documentation](../../configs/index.md) - All config files
- [mkinits](mkinits.md) - Creates only `__init__.py` files
- [init](init.md) - Calls `mkroot` as part of full project setup
