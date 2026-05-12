# Build System

pyrig provides a lightweight build framework for producing distributable
artifacts — standalone executables, archives, or any other output that the
project needs to ship. It is built on the same `ConfigFile` plugin architecture
that manages every other part of the project, so builders are discovered and run
automatically without any explicit registration.

---

## How It Works

`BuilderConfigFile` is an abstract base class that **repurposes the `ListConfigFile`
interface for build operations** instead of configuration file management. The
key insight is that a build artifact can be modelled as a "config file" whose
required content is simply its own existence on disk:

- `is_correct()` returns `True` when the artifact file already exists in `dist/`.
- `validate()` runs the build when the artifact is absent, and skips it when it
  is already present.
- `pyrig build` command delegates to `BuilderConfigFile.validate_all_subclasses()`,
  which discovers all concrete builder subclasses and validates each one.

This means the `pyrig build` command is inherently **incremental** — it only
builds what is missing. Delete an artifact from `dist/` to force a rebuild.

---

## Artifact Naming

Every artifact gets a platform-specific filename composed of three parts:

```text
<non_platform_stem>-<platform.system()><separator><extension>
```

For example, a builder with stem `myapp` produces:

- `myapp-Linux` on Linux
- `myapp-Windows.exe` on Windows
- `myapp-Darwin` on macOS

The platform suffix ensures that builds for different operating systems can
coexist in the same `dist/` directory, which is important for CI pipelines that
build across multiple platforms in parallel and unify the output artifacts
in a single place later on.

---

## Build Lifecycle

When a builder runs, the framework:

1. Creates a temporary directory.
2. Calls `create_artifact(tmp_path)` — the subclass writes the artifact there,
   named exactly `self.filename()`.
3. Moves the artifact from the temp directory into `dist/`.
4. Cleans up the temporary directory automatically.

The temp-then-move approach keeps `dist/` clean: a failed or interrupted build
never leaves a partial artifact in the output directory.

---

## `ExecutableBuilder`

pyrig ships one ready-to-use abstract base: `ExecutableBuilder`, which produces
**single-file standalone executables** using
[PyInstaller](https://pyinstaller.org). It handles all PyInstaller configuration
automatically:

- Single-file mode, no console window.
- Platform-appropriate icon (ICO on Windows, ICNS on macOS, PNG on Linux).
- Automatic bundling of resource packages from packages that depend on pyrig,
  so that every `rig/resources/` package in the project's dependencies is
  included and accessible at runtime via `importlib.resources`. Pyrig's own
  resources are intentionally excluded.

To create an executable builder, subclass `ExecutableBuilder` and implement two
methods:

- `entry_point_module()` — the module PyInstaller uses as its main script.
- `app_icon_png_location()` — the file stem (without extension) and resource
package of the PNG icon.

---

## Adding a Custom Builder

Any build target can be supported by subclassing `BuilderConfigFile` and
placing the subclass anywhere under `<package>/rig/builders/`. The framework
discovers it automatically via the same cross-package subclass discovery used
everywhere else in pyrig.

Some methods must be implemented:

- `non_platform_stem()` — the base name of the artifact (without the platform
  suffix).
- `extension()` — the file extension of the artifact (without the leading dot).
- `create_artifact(tmp_path)` — writes the finished artifact to
  `tmp_path / self.filename()`.

Everything else — output path, platform suffix, temp directory lifecycle, and
skip-if-exists logic — is handled by the framework.

Simply run `pyrig subcls` and select `ExecutableBuilder` to generate a
ready-to-edit subclass skeleton for a new executable.

---

## Discovery Across the Dependency Chain

Builder discovery follows the same pattern as `ConfigFile` and `Tool` discovery.
The `pyrig build` command calls `BuilderConfigFile.validate_all_subclasses()`,
which walks every installed package that depends on pyrig, imports
`<package>.rig.builders`, and collects all non-abstract `BuilderConfigFile`
subclasses. There is no manifest, no entry-point declaration, and no import
required — placing a concrete subclass in the right package is sufficient.
