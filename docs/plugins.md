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

The plugins maintained alongside pyrig are listed below. Each links to its own
documentation.

---

## Available Plugins

- **[pyrig-pypi](https://Winipedia.github.io/pyrig-pypi)** — Publishes your
  package to PyPI automatically from your CI/CD pipeline.
- **[pyrig-codecov](https://Winipedia.github.io/pyrig-codecov)** — Uploads your
  test coverage reports to Codecov during the health check workflow.
- **[pyrig-executables](https://Winipedia.github.io/pyrig-executables)** —
  Builds standalone, single-file executables of your project and attaches them
  to your GitHub releases.
- **[pyrig-containers](https://Winipedia.github.io/pyrig-containers)** — Builds
  a container image of your project and publishes it to a container registry
  from CI/CD.
- **[pyrig-containers-pypi](https://Winipedia.github.io/pyrig-containers-pypi)**
  — Combines pyrig-containers and pyrig-pypi so a single project can publish both
  a container image and a PyPI package without the two plugins conflicting.
- **[pyrig-resources](https://Winipedia.github.io/pyrig-resources)** — Adds a
  conventional resources package for bundling static assets that ship with your
  project.
- **[pyrig-fixtures](https://Winipedia.github.io/pyrig-fixtures)** — Provides a
  library of reusable pytest fixtures, plus a `pyrig mk fixture` scaffolder, for
  testing pyrig-based projects.
