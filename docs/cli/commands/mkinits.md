# mkinits

Creates `__init__.py` files for all packages and modules that are missing them.

## Usage

```bash
uv run pyrig mkinits

# With verbose output to see which __init__.py files are created
uv run pyrig -v mkinits
```

## What It Does

The `mkinits` command:

1. **Scans all directories** in the project (src and tests packages)
2. **Identifies packages** (directories containing Python files)
3. **Creates `__init__.py` files** for packages that don't have them

### Why `__init__.py` Files Matter

Python packages require `__init__.py` files to be importable. Without them:

- Directories become namespace packages (not recommended)
- Imports may fail or behave unexpectedly
- Package discovery tools may not work correctly

pyrig enforces regular packages (with `__init__.py`) over namespace packages for
consistency and reliability.

## Behavior

- **Does not overwrite existing files** - Only creates missing `__init__.py`
  files
- **Creates minimal files** - `__init__.py` files are created with a minimal
  docstring (`"""__init__ module."""`)
- **Idempotent** - Safe to run multiple times

## When to Use

Use `mkinits` when:

- Creating new packages or modules
- Converting namespace packages to regular packages
- Ensuring all packages have `__init__.py` files

## Autouse Fixture

This command **runs automatically** in the `assert_no_namespace_packages`
autouse fixture at session scope. See
[Autouse Fixtures](../../tests/autouse.md#assert_no_namespace_packages) for
details.

The fixture checks for namespace packages and automatically runs `mkinits` to
create missing `__init__.py` files before tests run.

## Related

- [mkroot](mkroot.md) - Also creates `__init__.py` files as part of project
  structure
- [Autouse Fixtures](../../tests/autouse.md) - Automatic `__init__.py` creation
