"""Container configuration file management.

This subpackage provides configuration file managers for container-related files,
specifically Containerfile (Docker-compatible container build files).

The ContainerfileConfigFile class generates production-ready container images with:
    - Python slim base image (latest supported version)
    - uv package manager for fast dependency installation
    - Non-root user for security
    - Optimized layer caching
    - Proper file permissions
    - Configurable entrypoint and command

Modules:
    container_file: Containerfile configuration management

See Also:
    pyrig.dev.configs.containers.container_file.ContainerfileConfigFile
        Main class for Containerfile generation
"""
