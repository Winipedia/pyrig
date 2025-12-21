# mkroot

Creates the project root structure by initializing all config files and creating missing `__init__.py` files.

## Usage

```bash
uv run pyrig mkroot
```

## What It Does

The `mkroot` command:

1. **Discovers all ConfigFile subclasses** across the project and its dependencies
2. **Initializes each config file** by calling `ConfigFile.init_config_files()`

### Config Files Created

All config files defined in the project are created or updated. This includes:

- **Python configs**: `pyproject.toml`, `__init__.py` files, `main.py`, `.experiment.py`
- **Container configs**: `Containerfile`
- **Documentation configs**: `mkdocs.yaml`, `README.md`, documentation structure
- **Environment configs**: `.env`, `.python-version`, `LICENSE`, `py.typed`
- **Git configs**: `.gitignore`, `.pre-commit-config.yaml`
- **Workflow configs**: GitHub Actions workflows (health check, build, release, publish)
- **Test configs**: `conftest.py`, test fixtures, test skeletons

See [Configs Documentation](../../configs/index.md) for complete details on all config files.

## Behavior

- **Creates files that do not exist yet**
- **Does overwrite existing files if they are not correct**
- **Idempotent** - Safe to run multiple times
- **Respects opt-out** - Files with opt-out markers are skipped

## When to Use

Use `mkroot` when:
- Adding new config files subclassing `ConfigFile` to an existing project
- Regenerating config files after updates
- Ensuring project structure is up to date

## Autouse Fixture

This command **runs automatically** in the `assert_root_is_correct` autouse fixture at session scope. See [Autouse Fixtures](../../tests/autouse.md#assert_root_is_correct) for details.

The fixture checks if any config files are incorrect and automatically runs `mkroot` to fix them before tests run.

## Related

- [Configs Documentation](../../configs/index.md) - Details on all config files
- [mkinits](mkinits.md) - Creates only `__init__.py` files
- [init](init.md) - Calls mkroot as part of full project setup

