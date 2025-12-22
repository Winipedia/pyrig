# mkroot

Creates the project root structure by initializing all config files and creating missing `__init__.py` files.

## Usage

```bash
# Create all config files
uv run pyrig mkroot

# Create only priority config files
uv run pyrig mkroot --priority
```

## Options

- `--priority` - Only create priority config files (essential files needed before dependency installation)

## What It Does

The `mkroot` command:

1. **Discovers all ConfigFile subclasses** across the project and its dependencies
2. **Initializes config files** in three phases by calling `make_project_root()`:
   - **Priority files** - Essential files required by other configs or the build process
   - **Ordered files** - Files with specific ordering dependencies
   - **Unordered files** - All remaining config files

When using `--priority`, only the priority files are created.

### Priority Config Files

When using `--priority`, only these essential files are created:

1. **GitIgnoreConfigFile** (`.gitignore`) - Git ignore patterns
2. **PyprojectConfigFile** (`pyproject.toml`) - Project metadata and dependencies
3. **LicenceConfigFile** (`LICENSE`) - Project license
4. **MainConfigFile** (`main.py`) - CLI entry point
5. **ConfigsInitConfigFile** (`dev/configs/__init__.py`) - Configs package initialization
6. **BuildersInitConfigFile** (`dev/builders/__init__.py`) - Builders package initialization
7. **ZeroTestConfigFile** (`tests/test_zero.py`) - Initial test file
8. **FixturesInitConfigFile** (`dev/tests/fixtures/__init__.py`) - Fixtures package initialization

These files are required before installing dependencies or running other initialization steps.

### All Config Files Created

Without `--priority`, all config files defined in the project are created or updated. This includes:

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

Use `mkroot --priority` when:
- During initial project setup (before installing dependencies)
- You only need essential config files to proceed with setup
- It is already running as part of the `pyrig init` process

## Autouse Fixture

This command **runs automatically** in the `assert_root_is_correct` autouse fixture at session scope. See [Autouse Fixtures](../../tests/autouse.md#assert_root_is_correct) for details.

The fixture checks if any config files are incorrect and automatically runs `mkroot` to fix them before tests run.

## Related

- [Configs Documentation](../../configs/index.md) - Details on all config files
- [mkinits](mkinits.md) - Creates only `__init__.py` files
- [init](init.md) - Calls `pyrig mkroot` as part of full project setup

