# Resources Documentation

pyrig provides a resource management system for bundling static files (images, configs, templates) that works seamlessly in both development and PyInstaller executables.

## Documentation Pages

### [Resource Management](resources.md)
Learn how to manage and access static resources:
- Resource package structure
- Accessing resources with `get_resource_path`
- PyInstaller compatibility
- Multi-package resource inheritance
- Common use cases

## Quick Overview

The resource system provides:
- **Unified access** to static files in development and production
- **Automatic PyInstaller support** via `importlib.resources`
- **Multi-package inheritance** - resources from all dependencies available
- **Type-safe access** with Path objects
- **Transparent MEIPASS handling** for frozen executables
