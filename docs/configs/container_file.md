# Containerfile Configuration

The `ContainerfileConfigFile` manages the project's Containerfile for building container images with Podman or Docker.

## Overview

Creates a production-ready Containerfile in the project root that:

- Uses the latest compatible Python slim image
- Installs dependencies with uv
- Runs as non-root user for security
- Sets up proper entrypoint and command
- Optimizes for layer caching

## Inheritance

```mermaid
graph TD
    A[ConfigFile] --> B[TextConfigFile]
    B --> C[ContainerfileConfigFile]

    style A fill:#a8dadc,stroke:#333,stroke-width:2px,color:#000
    style B fill:#f4a261,stroke:#333,stroke-width:2px,color:#000
    style C fill:#90be6d,stroke:#333,stroke-width:2px,color:#000
```

**Inherits from**: `TextConfigFile`

**What this means**:

- File is plain text (not YAML/TOML/JSON)
- Validation checks if required content is present
- Users can add custom content before or after required layers
- File is considered correct if all required layers exist in the file

## File Location

**Path**: `Containerfile` (project root)

**No extension**: The file is named exactly `Containerfile` with no extension, following Podman/Buildah conventions.

## How It Works

### Automatic Generation

When initialized via `uv run pyrig mkroot`, the Containerfile is automatically created with all required layers:

1. **Base image**: Uses Python slim image matching your `requires-python` constraint
2. **Working directory**: Sets up workspace named after your project
3. **UV installation**: Copies uv binary from official image
4. **Dependency files**: Copies metadata files for dependency installation
5. **User setup**: Creates non-root `appuser` for security
6. **Source code**: Copies your package with proper ownership
7. **Dependencies**: Installs runtime dependencies (excludes dev group)
8. **Cleanup**: Removes unnecessary files to reduce image size
9. **Entrypoint**: Sets up `uv run <project>` as entrypoint
10. **Default command**: Runs your main module by default

### Layer Structure

The Containerfile is built from discrete layers returned by `get_layers()`:

```python
[
    "FROM python:3.12-slim",
    "WORKDIR /my-project",
    "COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv",
    "COPY README.md LICENSE pyproject.toml uv.lock ./",
    "RUN useradd -m -u 1000 appuser",
    "RUN chown -R appuser:appuser .",
    "USER appuser",
    "COPY --chown=appuser:appuser my_project my_project",
    "RUN uv sync --no-group dev",
    "RUN rm README.md LICENSE pyproject.toml uv.lock",
    'ENTRYPOINT ["uv", "run", "my-project"]',
    'CMD ["main"]'
]
```

Each layer is joined with double newlines for readability.

### Validation Logic

The `is_correct()` method checks that all required layers are present in the file:

```python
all_layers_in_file = all(
    layer in cls.get_file_content() for layer in cls.get_layers()
)
return super().is_correct() or all_layers_in_file
```

This allows you to:

- Add comments between layers
- Add custom layers before or after required ones
- Modify layer order (though not recommended)
- Add build arguments or environment variables
- Also simplifies subclassing for customization

As long as all required layers exist somewhere in the file, validation passes.

## Dynamic Configuration

The Containerfile adapts to your project automatically:

### Python Version

```python
latest_python_version = PyprojectConfigFile.get_latest_possible_python_version()
# Uses the highest Python version allowed by requires-python
```

If `requires-python = ">=3.10"`, it uses the latest 3.x version available at python.org.

### Project Names

```python
project_name = PyprojectConfigFile.get_project_name()  # "my-project"
package_name = PyprojectConfigFile.get_package_name()  # "my_project"
```

Automatically uses your project name from `pyproject.toml`.

### Entrypoint

```python
entrypoint_args = list(PackageManager.get_run_args(project_name))
# ["uv", "run", "my-project"]
```

Uses uv's run command to execute your project in the container environment.

## Usage

### Building the Image

```bash
# With Podman (recommended)
podman build -t my-project .
```

We suppose all this works with docker as well. However we strongly recommend podman for security and performance reasons. It is deamonless and rootless, which makes it simply better than docker.

### Running the Container

because we define an entrypoint and a default command, you can run the container directly and are not stuck with the main command. The main command is just the default command that is run when you do not provide any arguments to the container.

```bash
# Run with default command (main module)
podman run my-project

# Run with custom command
podman run my-project --help

# Run with custom subcommand
podman run my-project mysubcommand --option value
```

### Customization

You can add custom layers while keeping pyrig's required layers:

```dockerfile
# Custom build argument
ARG BUILD_DATE

# Required pyrig layers...
FROM python:3.12-slim
WORKDIR /myproject
# ... rest of required layers ...

# Custom copy
COPY my_custom_file.txt ./
```

As long as all required layers are present, validation passes.

## Security Features

- **Non-root user**: Runs as `appuser` (UID 1000) instead of root
- **Minimal base**: Uses slim Python image to reduce attack surface and keep container size small and lightweight
- **No dev dependencies**: Only installs runtime dependencies
- **Proper ownership**: Files owned by appuser, not root

## Best Practices

1. **Keep required layers**: Don't remove pyrig's generated layers
2. **Add custom layers after**: Append your customizations at the end
3. **Do not use .containerignore**: Should not be necessary as we only copy the package folder and not the entire project. All copied config file are deleted in the last layer.
