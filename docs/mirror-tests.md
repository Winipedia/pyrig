# Mirror Test System

pyrig enforces a strict structural rule: every source module, class, function
and method must have a corresponding test counterpart. This is not a coverage
metric — it is a structural guarantee. The system that implements it is
called the **mirror test framework**, and it is built on top of the same
`ConfigFile` machinery that manages all other project files.

---

## The Core Idea

The test tree mirrors the source tree, one file for one file, one test class for
one source class, one test function/method for every source function/method. The
expected test module for `src/my_project/utils.py` is always
`tests/test_my_project/test_utils.py`. The expected test class for `MyHelper` is
`TestMyHelper`. The expected test function for `do_something` is `test_do_something`.

This naming convention is not configurable by default — it is the contract the
system enforces. Downstream projects can override the prefix strings
(`test_` / `Test`) by subclassing `MirrorTestConfigFile`, but the structure is
always a 1:1 mirror.

---

## `MirrorTestConfigFile`

`MirrorTestConfigFile` is a `ConfigFile` subclass that treats test files the same
way pyrig treats any other managed file: as a file with a required minimum content
that must be present and correct.

The "required content" for a test file is the full test module: the existing
implementations plus new stubs for every source symbol that does not yet have a
test. `lines()` builds and returns that full content by reading the existing
file and appending skeletons for any untested symbols. `test_module_content()`
reads the existing test file. `validate()` writes the result when the file is
missing or incorrect — it never removes existing test implementations.

Each stub is a minimal placeholder:

- **Functions** become:

  ```python
  def test_<name>() -> None:
      """Test function."""
      raise NotImplementedError
  ```

- **Classes** become:

  ```python
  class Test<Name>:
      """Test class."""
  ```

- **Methods** become:

  ```python
  def test_<name>(self) -> None:
      """Test method."""
      raise NotImplementedError
  ```

  inserted into the matching test class

Stubs signal intent — they mark code that needs a test without pretending the
test is implemented. Running the suite with an unimplemented stub fails that
specific test, not the whole suite silently.

---

## Dynamic Subclass Generation

Unlike most `ConfigFile` subclasses, which are written by hand for a specific file,
`MirrorTestConfigFile` is never subclassed manually for individual source modules.
Instead, `MirrorTestConfigFile` dynamically generates one subclass per source module
at runtime.

When `mktests` asks for all concrete subclasses during validation, the system:

1. Enumerates every module in the project's source package via `discover_modules`.
2. Generates dynamically a subclass for each one using `type()`, wiring
   `mirror_module()` to return that specific module.
3. Yields those subclasses to the validation machinery, which validates each one
   in turn — creating or updating the test file as needed by adding skeleton stubs
   for any missing tests.

This means the set of managed test files is always derived from the current state
of the source package. No registration, no manifest, no manual bookkeeping.

---

## Extending the Mirror Test System

The mirror test system is itself overridable via the standard `RigDependencySubclass`
mechanism. A downstream project can subclass `MirrorTestConfigFile` to change
naming conventions, adjust what counts as "tested", or customise the skeleton
format. The `mktests` command and the `all_modules_tested` fixture both use
`MirrorTestConfigFile.L` — the leaf subclass — so a downstream override is picked
up automatically everywhere the system is used.

The `mktests` command is the recommended way to trigger generation:

```text
uv run pyrig mktests
```
