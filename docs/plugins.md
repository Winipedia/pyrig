# Plugins

pyrig is extensible through plugins. A plugin is just a package that pyrig
discovers automatically — adding it as a dev dependency is all it takes for its
tools, config files, and workflow steps to be picked up by `pyrig init` and
`pyrig sync`, with no per-project configuration.

```bash
# Add a plugin to your project
uv add pyrig-plugin-name --dev
# apply the plugin to your project
uv run pyrig sync
```

After adding and syncing a plugin, please check all the files it affected
to ensure they are correct. The best way to add a plugin is before initializing
your project with `pyrig init`, this way each file is definitely correctly generated.
Syncing works correctly as well, but there might be some edge cases where the
deep merge logic may produce a slightly incorrect file. In that case you can
delete a file and re-run `pyrig sync` to regenerate it, then it will definitely
be correct as well.

---

## Some Useful Plugins

- **[pyrig-pypi](https://Winipedia.github.io/pyrig-pypi)** — Publishes your
  package to PyPI automatically from your CI/CD pipeline.
- **[pyrig-codecov](https://Winipedia.github.io/pyrig-codecov)** — Uploads your
  test coverage reports to Codecov during the health check workflow.
- **[pyrig-executables](https://Winipedia.github.io/pyrig-executables)** —
  Builds standalone, single-file executables of your project and attaches them
  to your GitHub releases.
- **[pyrig-resources](https://Winipedia.github.io/pyrig-resources)** — Adds a
  conventional resources package for bundling static assets that ship with your
  project.
- **[pyrig-env](https://Winipedia.github.io/pyrig-env)** — Adds a
  version-control-ignored `.env` file for local environment variables and
  secrets.

!!! note
    Inspecting these plugins to see how to create your own plugin can be very helpful.
    They are great examples of how to utilize pyrig's plugin system effectively.

## Example

Let's say we want to create a plugin that replaces the type-checker `ty` with `mypy`.
Let's name this plugin `pyrig-mypy`.

Here are the steps to create the `pyrig-mypy` plugin:

1. Start a new project

```bash
uv init pyrig-mypy --python 3.12
cd pyrig-mypy
uv add pyrig
uv run pyrig init
```

!!! note
    When creating a plugin pyrig is added as a runtime-dependency because we
    will later install the plugin as a dev-dependency.

2. Override behavior as needed for your plugin

We will need to create subclasses of all `Tool` and `ConfigFile` classes that
have functionality we want to adjust. In this case we want to replace the
type-checker `ty` with `mypy`.

```bash
# run this command
uv run pyrig mk subcls
```

The command will open an interactive fuzzy search, where you need to select the
class you want to create a subclass for.
Search for the name of the file or tool you want to adjust.
In our case search for `ty` and select the right option which looks like this:
`pyrig.rig.tools.typing.checker.TypeChecker (ty)`
We select it and once we hit enter this scaffold a new file with a subclass
skeleton for us to modify. The file path is printed to the terminal.

The scaffolded file lives at `src/pyrig_mypy/rig/tools/typing/checker.py` —
the same sub-path as the original, but rooted at our own package instead of
`pyrig`'s. It looks like this:

```python
"""Static type checker command construction and badge metadata."""

from pyrig.rig.tools.typing.checker import TypeChecker as BaseTypeChecker


class TypeChecker(BaseTypeChecker):
    """You can override methods from the base class to customize behavior."""
```

3. Implement the overrides

Fill in the skeleton with `mypy`'s own identity and commands.
With the help of any basic IDE it is very simple to
inspect the original class's methods to understand what needs to be overridden.

```python
"""Static type checker command construction and badge metadata."""

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.typing.checker import TypeChecker as BaseTypeChecker


class TypeChecker(BaseTypeChecker):
    """Type-safe wrapper for the `mypy` static type checker."""

    def image_url(self) -> str:
        """Return the badge image URL for `mypy`."""
        return "https://img.shields.io/badge/mypy-checked-2A6DB2"

    def link_url(self) -> str:
        """Return the URL of the `mypy` project page."""
        return "https://mypy-lang.org"

    def name(self) -> str:
        """Return `'mypy'`."""
        return "mypy"

    def check_args(self, *args: str) -> Args:
        """Build the command for running `mypy`.

        Args:
            *args: Additional arguments appended after the executable.

        Returns:
            Args for `mypy [args]`.
        """
        return self.args(*args)

    def version_control_ignore_patterns(self) -> tuple[str, ...]:
        """Return the path of `mypy`'s cache directory."""
        return (".mypy_cache/",)
```

mypy is best configured via the `pyproject.toml` file. pyrig's default is to
configure a tool in the `pyproject.toml` file if possible and sensible.
So we repeat the process above to declare the settings we want for `mypy` in
the `pyproject.toml` file.

```bash
uv run pyrig mk subcls
```

Search for `pyproject.toml` and select the appropriate option, which looks
like this: `pyrig.rig.configs.pyproject.PyprojectConfigFile (pyproject.toml)`.
This scaffolds `src/pyrig_mypy/rig/configs/pyproject.py`:

```python
"""Generation and validation of the project's `pyproject.toml` file."""

from pyrig.rig.configs.pyproject import PyprojectConfigFile as BasePyprojectConfigFile


class PyprojectConfigFile(BasePyprojectConfigFile):
    """You can override methods from the base class to customize behavior."""
```

`PyprojectConfigFile.tool_configs()` assembles the `[tool]` section from
every managed tool's `config_name()`, so we override it to merge in `mypy`'s
own settings on top of whatever the base class already provides.

!!! note
    Unlike `ty`, `mypy` doesn't check the current directory by default —
    with no CLI args and no `files`/`packages`/`modules` config it errors
    with `Missing target module, package, files, or command`.

```python
"""Generation and validation of the project's `pyproject.toml` file."""

from typing import Any

from pyrig.rig.configs.pyproject import PyprojectConfigFile as BasePyprojectConfigFile
from pyrig.rig.tools.packages.manager import PackageManager

from pyrig_mypy.rig.tools.typing.checker import TypeChecker


class PyprojectConfigFile(BasePyprojectConfigFile):
    """Adds `mypy`'s configuration to the `tool` section of `pyproject.toml`."""

    def tool_configs(self) -> dict[str, Any]:
        """Return `super().tool_configs()` with `mypy`'s settings added.

        Returns:
            The inherited `tool` section merged with `mypy`'s configuration.
        """
        return {
            **super().tool_configs(),
            TypeChecker.I.config_name(): {
                "files": [PackageManager.I.source_root().as_posix()],
                "strict": True,
                "show_error_code_links": True,
                "warn_unreachable": True,
                "enable_error_code": [],
            },
        }
```

We recommend setting up tools and files according to the
[philosophy of pyrig](philosophy.md), which we've attempted in this example —
though it may not be fully comprehensive here, since it is just an example.

We reuse our own `TypeChecker.I.config_name()` (from step 3, `"mypy"`) instead
of hardcoding the string, so the key stays in sync if the tool's `name()`
ever changes, and to keep the code as dynamic and DRY as possible in general.

!!! note
    Here we can see nicely how the `.I` classproperty is used to access the leaf
    instance of a class. In our case this will resolve to an instance of the
    `TypeChecker` class we defined above.

!!! note
    We recommend always inspecting the parent class's methods beforehand to see
    what you can and should override. This is very simple with any standard IDE
    like PyCharm or VSCode, or just by looking at the source code.

4. Synchronize the project

Now that we have overridden the necessary functionality, we run pyrig's
synchronization command.

```bash
uv run pyrig sync
```

This will first update all necessary files, like `pyproject.toml` and `prek.toml`,
automatically. It will also install `mypy` as a dev dependency for you, which will
show up in the `pyproject.toml` in the dev dependencies section.

Double check all affected files that are printed to the stdout or stderr to make
sure everything is as expected, sometimes the [merging process](config-files.md#how-merging-works)
generates a slightly incorrect result that needs to be manually adjusted once.

This command will also generate test files with skeletons under `tests/` for you
to implement. Now we can commit our changes and check that the new mypy pre-commit
hook works as intended and our code meets the new type checking requirements.

We recommend you implement the tests and then use the `pyrig-pypi`
plugin to publish your plugin package to PyPI via the CI/CD pipeline pyrig
generates for you. But for the sake of simplicity in this example, let's
publish this package directly with uv instead:

```bash
uv build
uv publish
```

Now in other projects you can simply add your plugin as a dependency in the
`pyproject.toml` and run `pyrig sync` to integrate it.

```bash
cd my-project
uv add pyrig-mypy  # or any plugin name
uv run pyrig sync
```
