# init

Sets up a new pyrig project from scratch through an automated process.

## Usage

```bash
uv run pyrig init

# With verbose output
uv run pyrig -v init
```

## What It Does

The `init` command transforms a basic Python project into a fully-configured
pyrig project. The following steps execute in order:

- **Initializing Version Control** - Initializes a git repository (`git init`)
- **Adding Dev Dependencies** - Adds pyrig's development dependencies
- **Syncing Venv** - Installs all dependencies
- **Creating Priority Config Files** - Creates essential files (LICENSE,
  pyproject.toml, package `__init__.py` files) that must exist before other
  steps
- **Syncing Venv (Again)** - Installs the project itself, making CLI commands
  available
- **Creating Project Root** - Generates all remaining config files via
  [mkroot](mkroot.md)
- **Creating Test Files** - Generates test skeletons via [mktests](mktests.md)
- **Installing Prek Hooks** - Installs prek hooks into the git
  repository
- **Adding All Files to Version Control** - Stages all files for commit
- **Running Prek Hooks** - Runs formatters/linters on all files
- **Running Tests** - Validates setup by running pytest
- **Committing Initial Changes** - Creates the initial git commit

## When to Use

Use `init` when starting a new project from scratch. This command is designed
for first-time setup, not repeated execution.

## Related

- [mkroot](mkroot.md) - Creates project structure and config files
- [mktests](mktests.md) - Generates test skeletons
- [Configs Documentation](../../configs/index.md) - Details on config files
  created
