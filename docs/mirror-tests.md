# Mirror Tests

pyrig enforces a 1:1 structural mapping between source code and tests. Every
source module, class, function, and method must have a corresponding test
counterpart. This is not a coverage metric — it is a structural guarantee
enforced by the `pyrig sync` pre-commit hook.

---

## The Convention

The test tree mirrors the source tree exactly:

| Source | Expected test counterpart |
|--------|--------------------------|
| `src/my_project/utils.py` | `tests/test_my_project/test_utils.py` |
| `def do_something()` | `def test_do_something()` |
| `class MyHelper` | `class TestMyHelper` |
| `def MyHelper.process()` | `def TestMyHelper.test_process()` |

---

## How It Works

`MirrorTestConfigFile` is a `ConfigFile` subclass. Instead of managing a config
file like `pyproject.toml`, it manages test files. Its `_configs()` returns the
complete expected test module content: existing tests merged with new stubs for
every source symbol that has no test yet.

`validate()` (inherited from `ConfigFile`) writes the result when the file is
missing or stubs are absent — it never removes or modifies existing test
implementations.

At sync time, `MirrorTestConfigFile` dynamically generates one subclass per
source module via `concrete_subclasses()`, so the set of managed test files
always matches the current source package — no registration or manifest needed.

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
recommitting. This means a commit can never introduce untested code.

---

## Customising

`MirrorTestConfigFile` is a `DependencySubclass`. Run `pyrig mk subcls` and
select it to generate a skeleton. Override methods to change naming conventions,
adjust what counts as tested, or customise the stub format. All sync operations
use `MirrorTestConfigFile.L` (the leaf subclass), so overrides are picked up
automatically.
