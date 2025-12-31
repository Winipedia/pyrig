# mktests

Generates test skeletons for all functions and classes in the source package.

## Usage

```bash
uv run pyrig mktests

# With verbose output to see test creation details
uv run pyrig -v mktests
```

## What It Does

The `mktests` command:

1. **Discovers all functions and classes** in the source package
2. **Generates test files** with skeleton test functions for each (in parallel
   for performance)
3. **Creates test structure** mirroring the source package structure

### Generated Test Structure

For each source module, creates a corresponding test module:

- `src/myapp/foo.py` → `tests/test_myapp/test_foo.py`

For each function/class, creates a test function:

- `def my_func()` → `def test_my_func()`
- `class MyClass` → `class TestMyClass` with `def test_<method>()` for each
  method

## Behavior

- **Does not overwrite existing tests** - Only creates missing test files and
  functions
- **Idempotent** - Safe to run multiple times
- **Automatic** - Also runs automatically when pytest detects missing tests

## When to Use

Use `mktests` when:

- Adding new functions or classes to the codebase
- Ensuring all code has test coverage
- Generating test structure for a new module

## Autouse Fixture

This command **runs automatically** via the `assert_all_modules_tested`
session-scoped fixture, which ensures every source module has a corresponding
test module with tests for all functions, classes, and methods. See
[Autouse Fixtures](../../tests/autouse.md#assert_all_modules_tested).

The fixture uses `MirrorTestConfigFile` to generate test skeletons for any
missing tests.

## Related

- [Tests Documentation](../../tests/index.md) - Details on test structure
- [Autouse Fixtures](../../tests/autouse.md) - Automatic test generation
- [init](init.md) - Calls mktests as part of full project setup
