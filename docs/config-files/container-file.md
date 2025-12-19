# ContainerfileConfigFile

## Overview

**File Location:** `Containerfile`
**ConfigFile Class:** `ContainerfileConfigFile`
**File Type:** Containerfile (Docker-compatible)
**Priority:** Standard

Defines how to build a container image for your Python application. Pyrig generates a production-ready, multi-stage Containerfile using Python slim images, uv for dependency management, and a non-root user for security.

## Purpose

The `Containerfile` enables containerized deployment of your application:

- **Reproducible Builds** - Same environment everywhere (dev, staging, prod)
- **Dependency Isolation** - All dependencies bundled in the image
- **Production Ready** - Slim base image, non-root user, minimal attack surface
- **uv Integration** - Fast dependency installation with uv
- **CLI Entry Point** - Container runs your CLI by default

### Why pyrig manages this file

pyrig creates a Containerfile to:
1. **Immediate containerization** - Projects are container-ready from day one
2. **Best practices** - Non-root user, slim images, layer optimization
3. **uv-native** - Uses uv for fast, reliable dependency installation
4. **Podman-compatible** - Works with both Podman and Docker
5. **CI integration** - Built automatically in the build workflow

The file is created during `pyrig init`. Running `pyrig mkroot` ensures all required layers are present.

## Containerfile vs Dockerfile

**Containerfile** is the OCI-standard name for container build instructions. It's identical to a Dockerfile in syntax and functionality.

**Why "Containerfile":**
- **OCI Standard** - Official Open Container Initiative naming
- **Podman Default** - Podman looks for `Containerfile` first
- **Docker Compatible** - Docker reads Containerfile just fine
- **User Preference** - Aligns with using Podman over Docker

Both `podman build` and `docker build` work with Containerfile.

## Container Architecture

### Base Image Strategy

Pyrig uses **Python slim images** for optimal size and security:

```dockerfile
FROM python:<latest>-slim
```

- **Slim variant** - Minimal Debian-based image (~50MB vs ~900MB for full)
- **Latest Python** - Uses the latest Python version from `requires-python` (currently 3.14)
- **Security** - Fewer packages = smaller attack surface
- **Performance** - Faster pulls and builds

### Multi-Stage Pattern

Pyrig uses a **single-stage build** with layer optimization:

1. **Base setup** - Python image + uv installation
2. **Metadata copy** - README, LICENSE, pyproject.toml, uv.lock
3. **User creation** - Non-root appuser
4. **Source copy** - Application code
5. **Dependency install** - Production dependencies only
6. **Cleanup** - Remove metadata files
7. **Entry point** - Configure CLI execution

### Security Features

- **Non-root user** - Runs as `appuser` (UID 1000)
- **Minimal base** - Slim image with fewer vulnerabilities
- **No dev dependencies** - Production image excludes dev tools
- **Proper ownership** - Files owned by appuser

## Containerfile Layers

Each layer in the Containerfile serves a specific purpose. Pyrig validates that all required layers are present.

### Layer 1: Base Image

```dockerfile
FROM python:<latest>-slim
```

- **Type:** Base image selection
- **Default:** `python:{latest}-slim` where latest is from `requires-python` (currently 3.14)
- **Required:** Yes
- **Purpose:** Provides Python runtime environment
- **Why pyrig sets it:** Uses the latest Python version your project supports for best compatibility

The version is determined by `PyprojectConfigFile.get_latest_possible_python_version()`, which reads the upper bound of `requires-python` in `pyproject.toml`.

### Layer 2: Working Directory

```dockerfile
WORKDIR /my-awesome-project
```

- **Type:** Directory setup
- **Default:** `/{project-name}` (e.g., `/my-awesome-project`)
- **Required:** Yes
- **Purpose:** Sets the working directory for subsequent commands
- **Why pyrig sets it:** Organizes files and provides a consistent path

All subsequent `COPY` and `RUN` commands execute relative to this directory.

### Layer 3: Install uv

```dockerfile
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
```

- **Type:** Binary copy from another image
- **Default:** Latest uv from official image
- **Required:** Yes
- **Purpose:** Installs uv package manager
- **Why pyrig sets it:** uv is required for dependency installation

This uses Docker's multi-stage build feature to copy just the `uv` binary without pulling the entire uv image.

### Layer 4: Copy Metadata Files

```dockerfile
COPY README.md LICENSE pyproject.toml uv.lock ./
```

- **Type:** File copy
- **Default:** README.md, LICENSE, pyproject.toml, uv.lock
- **Required:** Yes
- **Purpose:** Provides metadata for dependency installation
- **Why pyrig sets it:** uv needs pyproject.toml and uv.lock to install dependencies

**Why copy these first:**
- **Layer caching** - Dependencies change less often than source code
- **Faster rebuilds** - Source changes don't invalidate dependency layer
- **Best practice** - Standard Docker optimization pattern

### Layer 5: Create User

```dockerfile
RUN useradd -m -u 1000 appuser
```

- **Type:** User creation
- **Default:** `appuser` with UID 1000
- **Required:** Yes
- **Purpose:** Creates a non-root user for running the application
- **Why pyrig sets it:** Security best practice - don't run as root

**UID 1000:**
- Standard first user ID on Linux systems
- Matches typical developer UID for easier file permissions
- Consistent across environments

### Layer 6: Change Ownership

```dockerfile
RUN chown -R appuser:appuser .
```

- **Type:** Permission change
- **Default:** Recursively chown to appuser
- **Required:** Yes
- **Purpose:** Gives appuser ownership of all files
- **Why pyrig sets it:** Allows appuser to read/write files

This must happen before switching to the non-root user.

### Layer 7: Switch User

```dockerfile
USER appuser
```

- **Type:** User context switch
- **Default:** `appuser`
- **Required:** Yes
- **Purpose:** All subsequent commands run as appuser
- **Why pyrig sets it:** Security - application runs as non-root

**Security impact:**
- Limits damage from vulnerabilities
- Prevents privilege escalation
- Industry best practice

### Layer 8: Copy Source Code

```dockerfile
COPY --chown=appuser:appuser my_awesome_project my_awesome_project
```

- **Type:** File copy with ownership
- **Default:** `{package_name} {package_name}`
- **Required:** Yes
- **Purpose:** Copies application source code
- **Why pyrig sets it:** Application code needed to run

**Why copy source last:**
- **Layer caching** - Source changes frequently
- **Fast rebuilds** - Only this layer and later ones rebuild on code changes
- **Optimization** - Dependencies are cached in earlier layers

### Layer 9: Install Dependencies

```dockerfile
RUN uv sync --no-group dev
```

- **Type:** Dependency installation
- **Default:** `uv sync --no-group dev`
- **Required:** Yes
- **Purpose:** Installs production dependencies only
- **Why pyrig sets it:** Production image doesn't need dev tools

**`--no-group dev`:**
- Excludes development dependencies (pytest, ruff, mypy, etc.)
- Smaller image size
- Faster installation
- Security - fewer packages to maintain

### Layer 10: Cleanup Metadata

```dockerfile
RUN rm README.md LICENSE pyproject.toml uv.lock
```

- **Type:** File deletion
- **Default:** Removes metadata files
- **Required:** Yes
- **Purpose:** Reduces image size
- **Why pyrig sets it:** Metadata files not needed at runtime

**Why remove:**
- **Smaller image** - Every MB counts in production
- **Security** - Less information disclosure
- **Clean runtime** - Only necessary files remain

**Note:** The package metadata is still available via the installed package.

### Layer 11: Entry Point

```dockerfile
ENTRYPOINT ["uv", "run", "my-awesome-project"]
```

- **Type:** Container entry point
- **Default:** `["uv", "run", "{project-name}"]`
- **Required:** Yes
- **Purpose:** Defines how to run the application
- **Why pyrig sets it:** Runs your CLI when container starts

**ENTRYPOINT vs CMD:**
- **ENTRYPOINT** - Always runs, can't be overridden easily
- **CMD** - Default arguments, can be overridden

This means `podman run my-awesome-project` runs `uv run my-awesome-project`.

### Layer 12: Default Command

```dockerfile
CMD ["main"]
```

- **Type:** Default command arguments
- **Default:** `["main"]`
- **Required:** Yes
- **Purpose:** Default subcommand to run
- **Why pyrig sets it:** Provides sensible default behavior

**How it works:**
```bash
# Runs: uv run my-awesome-project main
podman run my-awesome-project

# Runs: uv run my-awesome-project other-command
podman run my-awesome-project other-command

# Runs: uv run my-awesome-project --help
podman run my-awesome-project --help
```

## Default Configuration

For a project named `my-awesome-project` with `requires-python = ">=3.12"`:

**File location:** `Containerfile`

**File contents:**
```dockerfile
FROM python:3.14-slim  # Latest version from requires-python

WORKDIR /my-awesome-project

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY README.md LICENSE pyproject.toml uv.lock ./

RUN useradd -m -u 1000 appuser

RUN chown -R appuser:appuser .

USER appuser

COPY --chown=appuser:appuser my_awesome_project my_awesome_project

RUN uv sync --no-group dev

RUN rm README.md LICENSE pyproject.toml uv.lock

ENTRYPOINT ["uv", "run", "my-awesome-project"]

CMD ["main"]
```

## Building the Container

### Using Podman (Recommended)

```bash
# Build the image
podman build -t my-awesome-project .

# Run the container
podman run my-awesome-project

# Run with custom command
podman run my-awesome-project --help

# Run interactively
podman run -it my-awesome-project bash
```

### Using Docker

```bash
# Build the image
docker build -t my-awesome-project .

# Run the container
docker run my-awesome-project

# Run with custom command
docker run my-awesome-project --help

# Run interactively
docker run -it my-awesome-project bash
```

### Build Arguments

You can pass build arguments to customize the build:

```bash
# Use a specific Python version
podman build --build-arg PYTHON_VERSION=3.12 -t my-awesome-project .

# Use a different base image
podman build --build-arg BASE_IMAGE=python:<version>-alpine -t my-awesome-project .
```

**Note:** Pyrig's default Containerfile doesn't use build args, but you can add them via customization.

## Running the Container

### Basic Usage

```bash
# Run with default command (main)
podman run my-awesome-project

# Run with custom command
podman run my-awesome-project subcommand --arg value

# Run with environment variables
podman run -e DATABASE_URL=postgres://... my-awesome-project

# Run with volume mount
podman run -v ./data:/data my-awesome-project

# Run with port mapping
podman run -p 8000:8000 my-awesome-project serve
```

### Interactive Shell

```bash
# Get a shell in the container
podman run -it my-awesome-project bash

# Or override the entrypoint
podman run -it --entrypoint bash my-awesome-project
```

### Debugging

```bash
# Run with verbose output
podman run my-awesome-project --verbose

# Check container logs
podman logs <container-id>

# Inspect the image
podman inspect my-awesome-project

# See image layers
podman history my-awesome-project
```

## Customization

You can customize the Containerfile by editing it directly or subclassing `ContainerfileConfigFile`.

### Adding System Dependencies

If your application needs system packages:

```dockerfile
FROM python:<latest>-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /my-awesome-project

# ... rest of the Containerfile
```

### Using Alpine Base

For smaller images, use Alpine Linux:

```dockerfile
FROM python:<latest>-alpine

# Alpine uses apk instead of apt
RUN apk add --no-cache gcc musl-dev

WORKDIR /my-awesome-project

# ... rest of the Containerfile
```

**Trade-offs:**
- **Smaller** - Alpine images are ~5MB vs ~50MB for slim
- **Slower builds** - Many Python packages need compilation on Alpine
- **Compatibility** - Some packages don't work well on Alpine (musl vs glibc)

### Multi-Stage Build

For even smaller images, use multi-stage builds:

```dockerfile
# Build stage
FROM python:<latest>-slim as builder

WORKDIR /build

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY README.md LICENSE pyproject.toml uv.lock ./
COPY my_awesome_project my_awesome_project

RUN uv sync --no-group dev

# Runtime stage
FROM python:<latest>-slim

WORKDIR /my-awesome-project

RUN useradd -m -u 1000 appuser

# Copy only the installed packages
COPY --from=builder --chown=appuser:appuser /build/.venv /my-awesome-project/.venv
COPY --from=builder --chown=appuser:appuser /build/my_awesome_project /my-awesome-project/my_awesome_project

USER appuser

ENTRYPOINT ["/my-awesome-project/.venv/bin/python", "-m", "my_awesome_project"]

CMD ["main"]
```

### Adding Health Checks

```dockerfile
# ... existing layers ...

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD uv run my-awesome-project health || exit 1
```

### Subclassing ContainerfileConfigFile

```python
from pyrig.dev.configs.containers.container_file import ContainerfileConfigFile


class CustomContainerfileConfigFile(ContainerfileConfigFile):
    @classmethod
    def get_layers(cls) -> list[str]:
        """Add custom layers."""
        layers = super().get_layers()

        # Insert system dependencies after FROM
        layers.insert(1, "RUN apt-get update && apt-get install -y gcc")

        # Add health check at the end
        layers.append('HEALTHCHECK CMD uv run my-app health')

        return layers
```

## CI Integration

The Containerfile is built automatically in the Build Workflow:

```yaml
# .github/workflows/build.yaml
- name: Install Container Engine
  uses: redhat-actions/podman-install@main

- name: Build Container Image
  run: podman build -t my-awesome-project .

- name: Save Container Image
  run: podman save -o dist/my-awesome-project.tar my-awesome-project
```

The built image is saved as an artifact and can be used in the Release Workflow.

## Related Files

- **`pyproject.toml`** - Determines Python version and project name ([pyproject.toml](pyproject.md))
- **`uv.lock`** - Locked dependencies for reproducible builds
- **`README.md`** - Copied into image (then removed)
- **`LICENSE`** - Copied into image (then removed)
- **`.github/workflows/build.yaml`** - Builds the container image ([build-workflow.md](build-workflow.md))
- **`.dockerignore`** - Files to exclude from build context (you create this)

## Common Issues

### Issue: Build fails with "COPY failed"

**Symptom:** `COPY README.md LICENSE pyproject.toml uv.lock ./` fails

**Cause:** Missing required files

**Solution:**
```bash
# Ensure all files exist
ls README.md LICENSE pyproject.toml uv.lock

# If missing, create them
uv run pyrig mkroot
```

### Issue: Image is too large

**Symptom:** Image is hundreds of MB or GB

**Cause:** Including unnecessary files or using full Python image

**Solution:**

**1. Use .dockerignore:**
```bash
# Create .dockerignore
cat > .dockerignore << EOF
.git
.venv
__pycache__
*.pyc
.pytest_cache
.mypy_cache
.ruff_cache
dist
*.egg-info
EOF
```

**2. Use slim base:**
```dockerfile
FROM python:<version>-slim  # Not python:<version>
```

**3. Clean up in same layer:**
```dockerfile
RUN apt-get update && apt-get install -y gcc \
    && uv sync --no-group dev \
    && apt-get remove -y gcc \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*
```

### Issue: Permission denied errors

**Symptom:** Container fails with permission errors

**Cause:** Files not owned by appuser

**Solution:**
```dockerfile
# Ensure proper ownership
COPY --chown=appuser:appuser my_awesome_project my_awesome_project

# Or chown after copy
RUN chown -R appuser:appuser /my-awesome-project
```

### Issue: uv not found

**Symptom:** `uv: command not found`

**Cause:** uv not copied correctly

**Solution:**
```dockerfile
# Ensure uv is copied
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Verify it's executable
RUN uv --version
```

### Issue: Dependencies not installing

**Symptom:** `uv sync` fails

**Cause:** Missing system dependencies

**Solution:**
```dockerfile
# Install required system packages
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*
```

### Issue: Container exits immediately

**Symptom:** Container starts then stops

**Cause:** No long-running process

**Solution:**

**If your app is a CLI:**
```bash
# Run with a command
podman run my-awesome-project serve

# Or keep it running
podman run -it my-awesome-project bash
```

**If your app is a server:**
```python
# In your main.py
def main() -> None:
    """Start the server."""
    import uvicorn
    uvicorn.run("my_awesome_project.app:app", host="0.0.0.0", port=8000)
```

### Issue: Can't connect to containerized service

**Symptom:** Service runs but can't connect from host

**Cause:** Port not exposed or mapped

**Solution:**
```dockerfile
# Expose the port in Containerfile
EXPOSE 8000
```

```bash
# Map the port when running
podman run -p 8000:8000 my-awesome-project
```

### Issue: Build is slow

**Symptom:** Builds take a long time

**Cause:** Poor layer caching or large context

**Solution:**

**1. Use .dockerignore:**
```bash
# Exclude large directories
.git
.venv
node_modules
```

**2. Order layers correctly:**
```dockerfile
# Copy dependencies first (changes less often)
COPY pyproject.toml uv.lock ./
RUN uv sync --no-group dev

# Copy source last (changes frequently)
COPY my_awesome_project my_awesome_project
```

**3. Use build cache:**
```bash
# Podman caches layers automatically
podman build -t my-awesome-project .
```

## Best Practices

### ✅ DO

- **Use slim images** - Smaller and more secure
- **Run as non-root** - Security best practice
- **Order layers by change frequency** - Dependencies before source
- **Use .dockerignore** - Exclude unnecessary files
- **Pin base image versions** - For reproducibility (in production)
- **Clean up in same layer** - Reduces image size

### ❌ DON'T

- **Don't run as root** - Security risk
- **Don't use latest tag in production** - Use specific versions
- **Don't include secrets** - Use environment variables or secrets management
- **Don't install dev dependencies** - Production image should be minimal
- **Don't copy .git directory** - Adds unnecessary size
- **Don't use full Python image** - Use slim or alpine

## Advanced Usage

### Building for Multiple Architectures

```bash
# Build for ARM64 (Apple Silicon, AWS Graviton)
podman build --platform linux/arm64 -t my-awesome-project:arm64 .

# Build for AMD64 (Intel/AMD)
podman build --platform linux/amd64 -t my-awesome-project:amd64 .

# Build multi-arch manifest
podman manifest create my-awesome-project:latest
podman manifest add my-awesome-project:latest my-awesome-project:arm64
podman manifest add my-awesome-project:latest my-awesome-project:amd64
```

### Using Build Secrets

```dockerfile
# Mount secrets during build (not stored in image)
RUN --mount=type=secret,id=pip_token \
    PIP_INDEX_URL=$(cat /run/secrets/pip_token) uv sync
```

```bash
# Build with secret
podman build --secret id=pip_token,src=./token.txt -t my-awesome-project .
```

### Optimizing Layer Caching

```dockerfile
# Bad: Changes to source invalidate dependency layer
COPY . .
RUN uv sync

# Good: Dependencies cached separately
COPY pyproject.toml uv.lock ./
RUN uv sync
COPY my_awesome_project my_awesome_project
```

## See Also

- [Podman Documentation](https://docs.podman.io/) - Container engine docs
- [Docker Documentation](https://docs.docker.com/) - Alternative container engine
- [OCI Image Spec](https://github.com/opencontainers/image-spec) - Container image standard
- [Best Practices for Writing Dockerfiles](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/) - Official Docker guide
- [uv Documentation](https://docs.astral.sh/uv/) - Package manager
- [Build Workflow](build-workflow.md) - CI container builds
- [pyproject.toml](pyproject.md) - Project configuration
- [Getting Started Guide](../getting-started.md) - Initial project setup


