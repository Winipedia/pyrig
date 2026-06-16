# Fixture Sharing System

pyrig provides a **fully inheritable pytest fixture library** that every project
built on pyrig gets automatically. Any fixture defined anywhere in the
`rig/tests/fixtures/` package tree of pyrig — or in any installed package that
depends on pyrig — is available in every test module of every downstream project
without explicit imports, plugin declarations, or `conftest.py` wiring.

---

## How Fixtures Are Discovered

The mechanism is driven by a single `conftest.py` at `pyrig.rig.tests.conftest`.
Which is registered as a pytest plugin in your generated `conftest.py` and
thus executed on every test run. When pytest starts, it executes this file, which:

1. Starts with pyrig's own `rig.tests.fixtures` package, then finds all
installed packages that depend on pyrig, including the current project itself
2. For each package in that chain, locates the equivalent of the
   `rig.tests.fixtures` package (e.g. `myproject.rig.tests.fixtures`).
3. Recursively collects every `.py` file in that package, skipping
   `__init__.py` files.
4. Converts each path to a dotted module name and adds it to `pytest_plugins`.

pytest treats every module in `pytest_plugins` as a plugin, which means all
fixtures defined in those modules become globally available. The effect is that
the fixture namespace of any pyrig-based project is the union of fixtures
contributed by every package in its dependency chain.
This can be very useful if you have a base package and want other projects
to share some common fixtures for their test suites.

---

## Where to Define Fixtures

The fixtures package is organised by purpose. Any `.py` file placed anywhere
inside `<package>/rig/tests/fixtures/` (at any depth) is picked up automatically.

pyrig ships a set of general-purpose fixtures of its own, organised by topic
into modules within this package. It also ships session-scoped autouse fixtures
in `autouse/session.py` that run on every test session to enforce project
health — verifying that every source module is mirror-tested, that all
version-controlled config files are correct, that there are no namespace
packages, and that no dev dependencies leak into source code.

Downstream projects follow the same structure. A project can add fixtures
either at the top level of its fixtures package or in subdirectories
for example, grouping fixtures by topics.

---

## Adding Fixtures to a Project

Defining a new fixture is as simple as writing a `@pytest.fixture`-decorated
function in any `.py` file under `<package>/rig/tests/fixtures/`. No
registration in a `conftest.py` is required. The fixture is available
project-wide on the next test run.

You can also generate a new fixture skeleton with the `mk fixture` command:

```text
uv run pyrig mk fixture my-fixture-name
```

This will create a new file `src/my_project/rig/tests/fixtures/fixtures.py` and
add a new fixture function skeleton named `my_fixture_name` to it with a
`@pytest.fixture` decorator. If the file already exists, the new fixture will be
added to it without affecting any existing content.

---

## Autouse Fixtures

pyrig defines a few autouse fixtures in `autouse/session.py`. These automatically
run at the beginning of every test run without being requested by any test.
They act as continuous project health checks, turning a passing test suite into
a guarantee that the project is structurally sound.

- **`all_modules_tested`** — checks that every source module has a fully
mirrored test module (either missing entirely or missing test coverage for one
or more functions, classes, or methods).
- **`all_config_files_correct`** — checks that all version-controlled config
files match their expected content.
- **`no_namespace_packages`** — all package directories have an `__init__.py`.
- **`no_dev_deps_in_source_code`** — source code can be imported and the CLI
  can run in an isolated environment that has no dev dependencies installed.

---
