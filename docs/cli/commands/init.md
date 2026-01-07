# init

Sets up a new pyrig project from scratch through an automated 9-step process.

## Usage

```bash
uv run pyrig init

# With verbose output
uv run pyrig -v init
```

## What It Does

The `init` command transforms a basic Python project into a fully-configured
pyrig project:

1. **Adding Dev Dependencies** - Adds pyrig's development dependencies
2. **Syncing Venv** - Installs all dependencies
3. **Creating Priority Config Files** - Creates essential files (LICENSE,
   pyproject.toml, package `__init__.py` files) that must exist before other
   steps
4. **Syncing Venv (Again)** - Installs the project itself, making CLI commands
   available
5. **Creating Project Root** - Generates all remaining config files via
   [mkroot](mkroot.md)
6. **Creating Test Files** - Generates test skeletons via [mktests](mktests.md)
7. **Running Pre-commit Hooks** - Installs hooks and runs formatters/linters
8. **Running Tests** - Validates setup by running pytest
9. **Committing Initial Changes** - Creates the initial git commit

## When to Use

Use `init` when starting a new project from scratch. This command is designed
for first-time setup, not repeated execution.

**Prerequisites**: A git repository must be initialized before running `init`.

## Related

- [mkroot](mkroot.md) - Creates project structure and config files
- [mktests](mktests.md) - Generates test skeletons
- [Configs Documentation](../../configs/index.md) - Details on config files
  created
