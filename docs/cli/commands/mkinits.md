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

1. **Scans the project** for namespace packages (excluding `docs/` and
   `.gitignore` patterns)
2. **Identifies namespace packages** (directories without `__init__.py` that
   can be imported as packages)
3. **Creates `__init__.py` files** for packages that don't have them

### Why `__init__.py` Files Matter

Without `__init__.py` files, directories become PEP 420 namespace packages.
While valid Python, this can cause:

- Unexpected import behavior
- Package discovery issues with some tools

pyrig enforces regular packages (with `__init__.py`) over namespace packages for
consistency and reliability.

## Behavior

- **Does not overwrite existing files** - Only creates missing `__init__.py`
  files
- **Creates minimal files** - Generated files contain a minimal docstring
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
