# mkroot

Creates the project root structure by initializing all config files (including
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

The `mkroot` command:

1. **Discovers all ConfigFile subclasses** across the project and its
   dependencies
2. **Initializes config files** in two phases by calling
   `ConfigFile.init_all_subclasses()`:
   - **Priority files** (priority > 0) - Essential files required by other
     configs, initialized sequentially in order of priority (highest first)
   - **Non-priority files** (priority <= 0) - Independent files, initialized in
     parallel using ThreadPoolExecutor for performance

When using `--priority`, only the priority files are created.

### Priority Config Files

When using `--priority`, only files with `get_priority() > 0` are created, in
sequential order by priority:

**Current priority files in pyrig**:

- **LicenceConfigFile** (`LICENSE`) - Priority 30 (highest - must exist before
  pyproject.toml for license auto-detection)
- **PyprojectConfigFile** (`pyproject.toml`) - Priority 20 (project metadata and
  dependencies)
- **ConfigsInitConfigFile** (`dev/configs/__init__.py`) - Priority 10 (configs
  package initialization)
- **FixturesInitConfigFile** (`dev/tests/fixtures/__init__.py`) - Priority 10
  (must exist before conftest.py)

These files are required before installing dependencies or running other
initialization steps.

### All Config Files Created

Without `--priority`, all config files defined in the project are created or
updated. This includes:

- **Python configs**: `pyproject.toml`, `__init__.py` files, `main.py`,
  `.experiment.py`
- **Container configs**: `Containerfile`
- **Documentation configs**: `mkdocs.yaml`, `README.md`, documentation structure
- **Environment configs**: `.env`, `.python-version`, `LICENSE`, `py.typed`
- **Git configs**: `.gitignore`, `.pre-commit-config.yaml`
- **Workflow configs**: GitHub Actions workflows (health check, build, release,
  publish)
- **Test configs**: `conftest.py`, test fixtures, test skeletons

See [Configs Documentation](../../configs/index.md) for complete details on all
config files.

## Behavior

### Without `--priority` flag

All config files are initialized using a hybrid approach:

1. **Group by priority** - Files are grouped by their `get_priority()` value
2. **Sequential group processing** - Priority groups processed in order (highest
   first)
3. **Parallel within groups** - Files in the same priority group initialize
   concurrently

This ensures:

- **Correct ordering** - Dependencies respected through priority values
- **Fast initialization** - Independent files (same priority) run in parallel

### With `--priority` flag

Only files with `get_priority() > 0` are initialized, using the same grouped
approach (groups processed sequentially, files within each group in parallel).

### General Behavior

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

This command **runs automatically** in the `assert_root_is_correct` autouse
fixture at session scope. See
[Autouse Fixtures](../../tests/autouse.md#assert_root_is_correct) for details.

The fixture checks if any config files are incorrect and automatically runs
`mkroot` to fix them before tests run.

## Implementation

The command delegates to:

- `ConfigFile.init_all_subclasses()` when called without `--priority`
- `ConfigFile.init_priority_subclasses()` when called with `--priority`

See [Configuration Architecture](../../configs/architecture.md) for details on
the priority system and parallel initialization.

## Examples

```bash
# Create all config files
uv run pyrig mkroot

# Create only priority files (during initial setup)
uv run pyrig mkroot --priority
```

## Related

- [Configs Documentation](../../configs/index.md) - Details on all config files
- [mkinits](mkinits.md) - Creates only `__init__.py` files
- [init](init.md) - Calls `pyrig mkroot` as part of full project setup
