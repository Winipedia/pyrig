# Autouse Fixtures and Validation

This document describes pyrig's autouse fixture system — a set of automatic validations that run during every test session to enforce project consistency, code quality, and testing discipline.

## Overview

pyrig includes autouse fixtures at three scopes that automatically validate your project:

| Scope | Runs | Purpose |
|-------|------|---------|
| **Session** | Once per test run | Validates project structure, dependencies, and config files |
| **Module** | Once per test module | Ensures all functions/classes in source have corresponding tests |
| **Class** | Once per test class | Ensures all methods in source class have corresponding tests |

These fixtures run automatically — no configuration required. When they detect issues, they either:
1. **Auto-fix** the problem and fail with a message to verify changes
2. **Fail immediately** with instructions on how to fix

## Session-Scoped Fixtures

Session fixtures run once at the beginning of the test session. They validate project-wide settings.

### `assert_no_unstaged_changes`

**Purpose:** Ensures there are no uncommitted changes before and after the test session (GitHub Actions only).

**What it checks:**
- Before tests: Verifies no unstaged changes exist in the git repository
- After tests: Verifies no unstaged changes were introduced during the test session
- Only runs when `running_in_github_actions()` returns `True`

**Auto-fix behavior:** None — fails immediately if unstaged changes are detected.

**Example errors:**
```
AssertionError: Found unstaged changes before test session. Please commit or stash them.
```
```
AssertionError: Found unstaged changes after test session. Please commit or stash them.
```

**Why this matters:**
- Prevents accidental uncommitted changes in CI pipelines
- Ensures test runs don't modify files without committing them
- Catches auto-generated files that should be committed (e.g., updated resource files)
- Maintains clean git history in automated workflows

**How to fix:**
- Before tests: Commit or stash any uncommitted changes
- After tests: Investigate what files were modified during the test run and commit them if appropriate

**Implementation:**
```python
@autouse_session_fixture
def assert_no_unstaged_changes() -> Generator[None, None, None]:
    """Verify that there are no unstaged changes."""
    in_github_actions = running_in_github_actions()

    if in_github_actions:
        assert_with_msg(
            not git_has_unstaged_changes(),
            "Found unstaged changes before test session. Please commit or stash them.",
        )
    yield
    if in_github_actions:
        assert_with_msg(
            not git_has_unstaged_changes(),
            "Found unstaged changes after test session. Please commit or stash them.",
        )
```

---

### `assert_root_is_correct`

**Purpose:** Validates that all ConfigFile settings match the expected state.

**What it checks:**
- Every ConfigFile subclass returns `True` from `is_correct()`
- All generated config files exist and contain required settings

**Auto-fix behavior:**
- If any ConfigFile is incorrect, runs `make_project_root()` to regenerate configs
- Then fails so you can verify the changes

**Example error:**
```
AssertionError: Config files are not correct. Corrected the files. Please verify the changes.
```

**Common triggers:**
- Missing or modified config files
- Outdated settings that don't match pyrig's expected values
- New pyrig version with updated config requirements

---

### `assert_no_namespace_packages`

**Purpose:** Ensures all packages have `__init__.py` files (no implicit namespace packages).

**What it checks:**
- Compares packages found with and without namespace package inclusion
- Any difference indicates missing `__init__.py` files

**Auto-fix behavior:**
- Creates `__init__.py` files for all namespace packages
- Fails with a list of packages that were fixed

**Example error:**
```
AssertionError: Found 2 namespace packages.
    Created __init__.py files for them.
    Please verify the changes at the following paths:
        - your_project.src.utils
        - your_project.src.helpers
```

**Why this matters:**
- Namespace packages can cause import issues
- Explicit `__init__.py` files ensure predictable import behavior
- Required for proper test discovery

---

### `assert_all_src_code_in_one_package`

**Purpose:** Enforces pyrig's single-package project structure.

**What it checks:**
- Only two top-level packages exist: your source package and `tests`
- Source package contains exactly: `src/`, `dev/`, and `main.py`

**Auto-fix behavior:** None — fails immediately with instructions.

**Example errors:**
```
AssertionError: Expected only packages {'tests', 'your_project'}, but found ['tests', 'your_project', 'extra_package']
```
```
AssertionError: Expected subpackages {'src', 'dev'}, but found {'src', 'dev', 'utils'}
```

**How to fix:**
- Move extra packages under your main source package
- Move utility code into `src/` subpackage
- Keep `dev/` for development-only code

---

### `assert_src_package_correctly_named`

**Purpose:** Verifies consistent naming across the project folder, source package, and `pyproject.toml`.

**What it checks:**
1. Current working directory name matches the project name in `pyproject.toml`
2. Source package name matches the name derived from the cwd (via `get_pkg_name_from_project_name`)
3. Source package name equals `PyprojectConfigFile.get_package_name()`

**Auto-fix behavior:** None — fails immediately.

**Example errors:**
```
AssertionError: Expected cwd name to be my_project, but it is my-project
```
```
AssertionError: Expected source package to be named my_project, but it is named my_proj
```

**How to fix:**
- Ensure your project folder name matches the project name in `pyproject.toml`
- Rename your source package directory to match the expected name
- Or update `pyproject.toml` to match your package name

---

### `assert_all_modules_tested`

**Purpose:** Ensures every source module has a corresponding test module.

**What it checks:**
- For each package in source: `tests/test_{package}/` exists
- For each module in source: `tests/test_{package}/test_{module}.py` exists

**Auto-fix behavior:**
- Runs `make_test_skeletons()` to generate missing test modules
- Fails with a list of created test files

**Example error:**
```
AssertionError: Found missing tests. Tests skeletons were automatically created for:
    Found untested objects:
        - tests.test_your_project.test_src.test_utils
        - tests.test_your_project.test_src.test_helpers
```

**Why this matters:**
- Guarantees test structure mirrors source structure
- Makes it impossible to "forget" to test a module
- Generated skeletons provide a starting point

---

### `assert_no_unit_test_package_usage`

**Purpose:** Enforces pytest over the `unittest` module.

**What it checks:**
- Scans all `.py` files (excluding gitignored paths)
- Searches for "unittest" (case-sensitive) in file content

**Auto-fix behavior:** None — fails immediately.

**Example error:**
```
AssertionError: Found unit test package usage in tests/test_example.py. Use pytest instead.
```

**How to fix:**
- Convert `unittest.TestCase` classes to plain pytest test classes
- Replace `self.assertEqual()` with `assert` statements
- Remove `unittest` imports

---

### `assert_dependencies_are_up_to_date`

**Purpose:** Ensures all dependencies are at their latest versions.

**What it checks:**
1. Updates `uv` itself (outside GitHub Actions)
2. Runs `uv lock --upgrade` to update dependencies
3. Runs `uv sync` to install updates

**Auto-fix behavior:** Updates dependencies automatically, then verifies success.

**Example errors:**
```
AssertionError: Expected 'success: You're on the latest version of uv' in uv self update output, got ...
```
```
AssertionError: Expected 'Resolved' and 'packages' in uv update output, got ...
```

**Notes:**
- Skips `uv self update` in GitHub Actions (to avoid rate limits)
- Ensures CI and local environments stay in sync

---

### `assert_pre_commit_is_installed`

**Purpose:** Ensures pre-commit hooks are installed in the git repository.

**What it checks:**
- Runs `pre-commit install`
- Verifies output contains "pre-commit installed at"

**Auto-fix behavior:** Installs pre-commit hooks automatically.

**Example error:**
```
AssertionError: Expected 'pre-commit installed at' in pre-commit install output, got ...
```

**Why this matters:**
- Pre-commit hooks enforce code quality before commits
- Ensures linting, formatting, and type checking run automatically
- Prevents non-compliant code from entering the repository

---

### `assert_src_runs_without_dev_deps`

**Purpose:** Verifies the source code works without development dependencies.

**What it checks:**
1. Copies source package to a temporary directory
2. Runs `uv sync --no-dev` to install only production dependencies
3. Verifies `pytest` is NOT installed (dev-only)
4. Imports all source modules to catch accidental dev dependency imports
5. Verifies `main` module can be imported

**Auto-fix behavior:** None — fails immediately.

**Example errors:**
```
AssertionError: Expected pytest not to be installed
```
```
AssertionError: Expected 'ModuleNotFoundError' in stderr, got ...
```
```
AssertionError: Expected Success in stdout, got ... and ModuleNotFoundError: No module named 'pytest'
```

**Why this matters:**
- Ensures production code doesn't accidentally import dev tools
- Catches `import pytest` or similar in source files
- Validates the dependency separation in `pyproject.toml`

**How to fix:**
- Move dev-only imports behind `if TYPE_CHECKING:` guards
- Ensure dev dependencies are in `[tool.uv.dev-dependencies]`
- Check for accidental imports of pytest, mypy, ruff, etc. in source

---

### `assert_src_does_not_use_dev`

**Purpose:** Verifies that source code (`src/`) does not import any code from `dev/`.

**What it checks:**
- Scans all `.py` files in the `src/` directory
- Searches for imports of any `dev` module from packages depending on pyrig
- Uses regex pattern matching to detect `{package}.dev` imports

**Auto-fix behavior:** None — fails immediately.

**Example error:**
```
AssertionError: Found dev usage in src:
    - /path/to/your_project/src/utils.py: your_project.dev
```

**Why this matters:**
- Enforces clean separation between production (`src/`) and development (`dev/`) code
- Ensures `src/` code can run without dev dependencies installed
- Prevents accidental coupling between runtime and development tooling

**How to fix:**
- Remove imports of `dev` modules from `src/` files
- Move dev-dependent code to the `dev/` directory
- Use dependency injection or configuration instead of direct imports

---

## Module-Scoped Fixtures

Module fixtures run once per test module, before any tests in that module execute.

### `assert_all_funcs_and_classes_tested`

**Purpose:** Ensures every function and class in a source module has a corresponding test.

**What it checks:**
- Gets all functions and classes from the source module
- Gets all test functions and test classes from the test module
- Verifies each source object has a corresponding test object

**Auto-fix behavior:**
- Runs `make_test_skeletons()` to generate missing test skeletons
- Fails with a list of created tests

**Example error:**
```
AssertionError: Found missing tests. Tests skeletons were automatically created for:
    Found untested objects:
        - tests.test_your_project.test_src.test_utils.test_calculate
        - tests.test_your_project.test_src.test_utils.TestHelper
```

**How it works:**

The fixture receives `assert_no_untested_objs` as a fixture parameter (a session-scoped fixture that provides the validation function):

```python
@autouse_module_fixture
def assert_all_funcs_and_classes_tested(
    request: pytest.FixtureRequest,
    assert_no_untested_objs: Callable[[ModuleType | type | Callable[..., Any]], None],
) -> None:
    module: ModuleType = request.module
    assert_no_untested_objs(module)
```

---

## Class-Scoped Fixtures

Class fixtures run once per test class, before any test methods in that class execute.

### `assert_all_methods_tested`

**Purpose:** Ensures every method in a source class has a corresponding test method.

**What it checks:**
- Gets all methods from the source class
- Gets all test methods from the test class
- Verifies each source method has a corresponding test method

**Auto-fix behavior:**
- Runs `make_test_skeletons()` to generate missing test method skeletons
- Fails with a list of created test methods

**Example error:**
```
AssertionError: Found missing tests. Tests skeletons were automatically created for:
    Found untested objects:
        - tests.test_your_project.test_src.test_calculator.TestCalculator.test_divide
        - tests.test_your_project.test_src.test_calculator.TestCalculator.test_multiply
```

**How it works:**

The fixture receives `assert_no_untested_objs` as a fixture parameter:

```python
@autouse_class_fixture
def assert_all_methods_tested(
    request: pytest.FixtureRequest,
    assert_no_untested_objs: Callable[[ModuleType | type | Callable[..., Any]], None],
) -> None:
    class_ = request.node.cls
    if class_ is None:
        return
    assert_no_untested_objs(class_)
```

---

## The Assertion Utilities

pyrig provides custom assertion utilities in `pyrig.src.testing.assertions`:

### `assert_with_msg`

A wrapper around Python's `assert` that always includes a custom message:

```python
def assert_with_msg(expr: bool, msg: str) -> None:
    assert expr, msg
```

**Usage:**
```python
assert_with_msg(
    package_name == expected_name,
    f"Expected package {expected_name}, but found {package_name}"
)
```

### `assert_with_info`

Extends `assert_with_msg` with expected/actual value formatting:

```python
def assert_with_info(expr: bool, expected: Any, actual: Any, msg: str = "") -> None:
    msg = f"""
Expected: {expected}
Actual: {actual}
{msg}
"""
    assert_with_msg(expr, msg)
```

### `assert_no_untested_objs` (Session Fixture)

A session-scoped fixture that provides the core validation function used by module and class fixtures. Located in `pyrig.dev.tests.fixtures.assertions`.

```python
@session_fixture
def assert_no_untested_objs() -> Callable[
    [ModuleType | type | Callable[..., Any]], None
]:
    """Fixture that provides a function to assert all objects have tests."""

    def _assert_no_untested_objs(
        test_obj: ModuleType | type | Callable[..., Any],
    ) -> None:
        # Get test objects
        test_objs = get_objs_from_obj(test_obj)
        test_objs_paths = {make_obj_importpath(obj) for obj in test_objs}

        # Get source objects
        obj = get_obj_from_test_obj(test_obj)
        objs = get_objs_from_obj(obj)

        # Find missing tests
        missing_test_obj_path_to_obj = {
            test_path: obj
            for test_path, obj in test_obj_path_to_obj.items()
            if test_path not in test_objs_paths
        }

        # Auto-fix: generate skeletons
        if missing_test_obj_path_to_obj:
            make_test_skeletons()

        # Fail with message
        assert_with_msg(not missing_test_obj_path_to_obj, msg)

    return _assert_no_untested_objs
```

This fixture is injected into the module and class fixtures, allowing them to call the validation function.

---

## Execution Order

The fixtures execute in a specific order based on scope:

```
Test Session Start
│
├── Session Fixtures (run once)
│   ├── assert_no_unstaged_changes (before tests, GitHub Actions only)
│   ├── assert_root_is_correct
│   ├── assert_no_namespace_packages
│   ├── assert_all_src_code_in_one_package
│   ├── assert_src_package_correctly_named
│   ├── assert_all_modules_tested
│   ├── assert_no_unit_test_package_usage
│   ├── assert_dependencies_are_up_to_date
│   ├── assert_pre_commit_is_installed
│   ├── assert_src_runs_without_dev_deps
│   └── assert_src_does_not_use_dev
│
├── For Each Test Module:
│   ├── Module Fixture: assert_all_funcs_and_classes_tested
│   │
│   └── For Each Test Class:
│       ├── Class Fixture: assert_all_methods_tested
│       │
│       └── Test Methods Execute
│
└── Test Session End
    └── assert_no_unstaged_changes (after tests, GitHub Actions only)
```

---

## Troubleshooting

### Temporarily Disabling Fixtures

To debug a specific issue, you can skip autouse fixtures by running pytest with specific markers:

```bash
# Run only a specific test file, bypassing session fixtures after first run
uv run pytest tests/test_specific.py -x

# Run with verbose output to see which fixtures execute
uv run pytest -v --setup-show
```

**Note:** You cannot fully disable autouse fixtures without modifying the code. This is by design — pyrig enforces quality gates.

### Common Issues and Solutions

#### "Config files are not correct"

**Cause:** A ConfigFile has been manually modified or is outdated.

**Solution:**
1. Review the diff in your version control
2. Decide whether to keep your changes or accept pyrig's regeneration
3. If keeping changes, ensure your modifications satisfy pyrig's subset validation

#### "Found namespace packages"

**Cause:** A directory is missing `__init__.py`.

**Solution:**
1. pyrig auto-creates the files
2. Verify the created files are correct
3. Commit them to your repository

#### "Expected only packages {'tests', 'your_project'}"

**Cause:** Extra packages exist at the root level.

**Solution:**
1. Move extra packages under your main source package
2. Or delete them if they're unused
3. pyrig enforces a single-package structure for consistency

#### "Found missing tests"

**Cause:** New functions/classes were added without corresponding tests.

**Solution:**
1. pyrig auto-generates test skeletons
2. Fill in the `raise NotImplementedError` placeholders
3. Run tests again to verify

#### "Found unit test package usage"

**Cause:** Code uses Python's `unittest` module.

**Solution:**
1. Convert `unittest.TestCase` classes to regular pytest classes
2. Replace `self.assertEqual(a, b)` with `assert a == b`
3. Remove `import unittest` statements

#### "Expected pytest not to be installed"

**Cause:** The `assert_src_runs_without_dev_deps` fixture detected that dev dependencies leaked into production code.

**Solution:**
1. Check for `import pytest` or similar in your source files
2. Move dev imports behind `if TYPE_CHECKING:` guards
3. Ensure dev dependencies are listed under `[tool.uv.dev-dependencies]`

### Understanding the Auto-Fix Pattern

Most autouse fixtures follow this pattern:

```python
@autouse_session_fixture
def assert_something() -> None:
    # 1. Check the condition
    is_correct = check_something()

    # 2. Auto-fix if possible
    if not is_correct:
        fix_the_issue()

    # 3. Fail with message (even after fix)
    assert_with_msg(
        is_correct,
        "Description of what was wrong and what was fixed"
    )
```

This pattern means:
- The fix happens automatically
- But the test still fails to alert you
- You must verify the changes and re-run tests

### Debugging Fixture Failures

1. **Read the error message carefully** — it explains what was checked and what was fixed

2. **Check your version control** — see what files were created or modified

3. **Re-run tests** — after verifying changes, the fixture should pass

4. **Check fixture order** — earlier fixtures may cause later fixtures to fail

5. **Run with verbose output:**
   ```bash
   uv run pytest -v --tb=long
   ```

---

## Creating Custom Autouse Fixtures

You can add your own autouse fixtures following pyrig's patterns:

```python
# your_project/dev/tests/fixtures/my_fixtures.py
from pyrig.dev.tests.utils.decorators import autouse_session_fixture
from pyrig.src.testing.assertions import assert_with_msg

@autouse_session_fixture
def assert_custom_validation() -> None:
    """Validate something project-specific."""
    is_valid = check_something()

    if not is_valid:
        fix_something()  # Optional auto-fix

    assert_with_msg(
        is_valid,
        "Description of what was wrong and how to fix it"
    )
```

### Best Practices for Custom Fixtures

1. **Use descriptive names** starting with `assert_`
2. **Document what the fixture checks** in the docstring
3. **Provide clear error messages** explaining the issue and fix
4. **Auto-fix when possible** but still fail to alert the developer
5. **Choose the right scope:**
   - Session: project-wide validations (run once)
   - Module: per-module validations (run per test file)
   - Class: per-class validations (run per test class)
   - Function: per-test validations (run for every test)

---

## Summary

pyrig's autouse fixtures provide automatic quality gates:

| Fixture | Scope | Auto-Fix | Purpose |
|---------|-------|----------|---------|
| `assert_no_unstaged_changes` | Session | No | No uncommitted changes (GitHub Actions only) |
| `assert_root_is_correct` | Session | Yes | Config files match expected state |
| `assert_no_namespace_packages` | Session | Yes | All packages have `__init__.py` |
| `assert_all_src_code_in_one_package` | Session | No | Single source package structure |
| `assert_src_package_correctly_named` | Session | No | Consistent naming across folder, package, and config |
| `assert_all_modules_tested` | Session | Yes | All modules have test modules |
| `assert_no_unit_test_package_usage` | Session | No | No unittest usage |
| `assert_dependencies_are_up_to_date` | Session | Yes | Dependencies are current |
| `assert_pre_commit_is_installed` | Session | Yes | Pre-commit hooks installed |
| `assert_src_runs_without_dev_deps` | Session | No | No dev deps in prod code |
| `assert_src_does_not_use_dev` | Session | No | No dev imports in src code |
| `assert_all_funcs_and_classes_tested` | Module | Yes | All functions/classes tested |
| `assert_all_methods_tested` | Class | Yes | All methods tested |

These fixtures ensure consistent project structure, complete test coverage, and up-to-date dependencies across all pyrig projects.
