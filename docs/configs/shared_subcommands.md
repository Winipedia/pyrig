# shared_subcommands.py Configuration

The `SharedSubcommandsConfigFile` manages the `dev/cli/shared_subcommands.py`
file.

## Overview

Creates a shared_subcommands.py file that:

- Copies only the docstring from `pyrig.dev.cli.shared_subcommands`
- Provides a place to define CLI subcommands shared across all pyrig projects
- Automatically discovered by pyrig's CLI system
- Allows creating reusable commands available in all your pyrig-based projects

## Inheritance

```mermaid
graph TD
    A[ConfigFile] --> B[ListConfigFile]
    B --> C[StringConfigFile]
    C --> D[PythonConfigFile]
    D --> E[PythonPackageConfigFile]
    E --> F[CopyModuleConfigFile]
    F --> G[CopyModuleOnlyDocstringConfigFile]
    G --> H[SharedSubcommandsConfigFile]

    style A fill:#a8dadc,stroke:#333,stroke-width:2px,color:#000
    style B fill:#457b9d,stroke:#333,stroke-width:2px,color:#fff
    style C fill:#f4a261,stroke:#333,stroke-width:2px,color:#000
    style D fill:#e76f51,stroke:#333,stroke-width:2px,color:#000
    style E fill:#9d84b7,stroke:#333,stroke-width:2px,color:#000
    style F fill:#90be6d,stroke:#333,stroke-width:2px,color:#000
    style G fill:#a8dadc,stroke:#333,stroke-width:2px,color:#000
    style H fill:#f4a261,stroke:#333,stroke-width:2px,color:#000
```

**Inherits from**: `CopyModuleOnlyDocstringConfigFile`

**What this means**:

- Copies only the docstring from the source module
- Allows you to add custom implementation
- Automatically determines target path
- Ensures parent directory is a valid Python package

## File Location

**Path**: `{package_name}/dev/cli/shared_subcommands.py`

**Source module**: `pyrig.dev.cli.shared_subcommands`

**Path transformation**: `pyrig.dev.cli.shared_subcommands` →
`{package_name}.dev.cli.shared_subcommands` →
`{package_name}/dev/cli/shared_subcommands.py`

## How It Works

### Automatic Generation

When initialized via `uv run pyrig mkroot`, the file is created with:

1. **Docstring copy**: Only the docstring from
   `pyrig.dev.cli.shared_subcommands` is copied
2. **Package structure**: The `dev/cli/` directory is created
3. **Ready for customization**: You can add your own shared subcommand functions

The file contains only the docstring, allowing you to add shared CLI commands.

## Usage

### Automatic Creation

```bash
uv run pyrig mkroot
```

### Purpose

This file is where you define CLI subcommands that should be available across
all your pyrig-based projects. Commands defined here are shared and reusable.

See the [CLI Subcommands documentation](../cli/subcommands.md) for details on
creating custom commands.

## Best Practices

1. **Don't modify the docstring**: Keep the copied docstring intact
2. **Add shared commands**: Define functions that are useful across multiple
   projects
3. **Keep it generic**: Shared commands should work in any pyrig project
4. **Document thoroughly**: Add clear docstrings since these are reused
