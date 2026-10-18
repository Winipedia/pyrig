# Mirror Tests

pyrig enforces a structural mapping between Python source files and tests.
Source files other than `__init__.py` have a corresponding test module, and
module-level functions and methods defined directly on module-level classes
have corresponding test names. This is not a coverage metric — it is a
structural guarantee enforced by the `pyrig sync` pre-commit hook.

---

## The Convention

The test tree mirrors the source tree:

| Source | Expected test counterpart |
|--------|--------------------------|
| `src/my_project/utils.py` | `tests/test_my_project/test_utils.py` |
| `def do_something()` | `def test_do_something()` |
| `def MyHelper.process()` | `def TestMyHelper.test_process()` |

---

## How It Works

`MirrorTestConfigFile` is a `ConfigFile` subclass. Instead of managing a config
file like `pyproject.toml`, it manages test files. Its `content()` returns the
existing test module content with stubs added for any module-level function or
directly declared class method whose expected test name is missing.

`validate()` writes the result when the file is missing or stubs are absent —
it never removes or modifies existing test implementations.

At sync time, `MirrorTestConfigFile` dynamically generates one subclass per
source file via `generate_subclass()`, so the set of managed test files
matches the current source package — no registration or manifest needed.

### Generated Stubs

Each missing test gets a minimal stub:

```python
def test_do_something() -> None:
    """Test function."""
    raise NotImplementedError
```

```python
class TestMyHelper:
    """Test class."""

    def test_process(self) -> None:
        """Test method."""
        raise NotImplementedError
```

Stubs raise `NotImplementedError` so unimplemented tests fail explicitly rather
than passing silently.

---

## Enforcement

`pyrig sync` is run as a pre-commit hook. If any test stubs are missing it
creates them, the hook fails, and the developer stages the new files before
recommitting. The check verifies expected test names, not whether tests exercise
or adequately cover the corresponding code.

---

## Customizing

`MirrorTestConfigFile` is a `DependencySubclass`. Run `pyrig mk subcls` and
select it to generate a subclass skeleton. Override methods to change naming conventions,
adjust what counts as tested, or customize the stub format.
