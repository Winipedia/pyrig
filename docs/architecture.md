# Architecture Overview

This document provides a comprehensive overview of pyrig's architecture, including visual diagrams of key systems and data flows.

## System Architecture

### High-Level Architecture

```mermaid
graph TB
    subgraph "User Interface"
        CLI[CLI Commands]
        Init[pyrig init]
        Build[pyrig build]
        MkTests[pyrig mktests]
    end

    subgraph "Core Systems"
        DepGraph[Dependency Graph]
        Discovery[Cross-Package Discovery]
        ConfigSys[ConfigFile System]
        BuildSys[Builder System]
        TestGen[Test Generator]
    end

    subgraph "Package Ecosystem"
        Pyrig[pyrig]
        Base[Base Package]
        App[Your Application]
    end

    subgraph "Outputs"
        Configs[Config Files]
        Tests[Test Files]
        Artifacts[Build Artifacts]
        CI[CI/CD Workflows]
    end

    CLI --> Init
    CLI --> Build
    CLI --> MkTests

    Init --> ConfigSys
    Build --> BuildSys
    MkTests --> TestGen

    ConfigSys --> Discovery
    BuildSys --> Discovery
    TestGen --> Discovery

    Discovery --> DepGraph

    DepGraph --> Pyrig
    DepGraph --> Base
    DepGraph --> App

    ConfigSys --> Configs
    BuildSys --> Artifacts
    TestGen --> Tests
    ConfigSys --> CI

    style Pyrig fill:#3776AB
    style Base fill:#FF8C00
    style App fill:#646464
```

### Dependency Graph System

The dependency graph is the foundation of pyrig's multi-package architecture:

```mermaid
graph LR
    subgraph "Dependency Graph Construction"
        A[Scan Installed Packages] --> B[Build Graph]
        B --> C[Find Dependents]
        C --> D[Topological Sort]
    end

    subgraph "Package Hierarchy"
        P[pyrig] --> BP[base-package]
        BP --> A1[app-1]
        BP --> A2[app-2]
        P --> A3[app-3]
    end

    D --> P

    style P fill:#3776AB
    style BP fill:#FF8C00
    style A1 fill:#646464
    style A2 fill:#646464
    style A3 fill:#646464
```

### ConfigFile Lifecycle

```mermaid
sequenceDiagram
    participant User
    participant CLI
    participant Discovery
    participant ConfigFile
    participant Filesystem

    User->>CLI: pyrig init / mkroot
    CLI->>Discovery: Find all ConfigFile subclasses
    Discovery->>Discovery: Scan dependency graph
    Discovery-->>CLI: Return ConfigFile classes
    
    loop For each ConfigFile
        CLI->>ConfigFile: Initialize
        ConfigFile->>ConfigFile: get_configs()
        ConfigFile->>Filesystem: Check if file exists
        
        alt File doesn't exist
            ConfigFile->>Filesystem: Create file with configs
        else File exists
            ConfigFile->>Filesystem: Load existing config
            ConfigFile->>ConfigFile: Validate (subset check)
            alt Missing required values
                ConfigFile->>Filesystem: Add missing values
            end
        end
    end
    
    CLI-->>User: Project initialized
```

## Data Flow Diagrams

### Initialization Flow

```mermaid
flowchart TD
    Start([uv run pyrig init]) --> AddDeps[Add dev dependencies]
    AddDeps --> Sync1[Sync venv]
    Sync1 --> Priority[Create priority configs]
    Priority --> Sync2[Sync venv again]
    Sync2 --> MkRoot[Create project root]
    MkRoot --> MkTests[Create test files]
    MkTests --> PreCommit[Run pre-commit hooks]
    PreCommit --> RunTests[Run tests]
    RunTests --> Commit[Commit changes]
    Commit --> End([Initialized Project])

    style Start fill:#3776AB
    style End fill:#2E7D32
```

### Build Flow

```mermaid
flowchart TD
    Start([uv run pyrig build]) --> Discover[Discover Builder subclasses]
    Discover --> Sort[Sort by dependency order]

    Sort --> Loop{For each Builder}
    Loop --> TempDir[Create temp directory]
    TempDir --> Create[Builder.create_artifacts]
    Create --> Move[Move to dist/]
    Move --> Rename[Add platform suffix]
    Rename --> Loop

    Loop --> End([Artifacts in dist/])

    style Start fill:#3776AB
    style End fill:#2E7D32
```

### Test Generation Flow

```mermaid
flowchart TD
    Start([uv run pyrig mktests]) --> Scan[Scan source code]
    Scan --> FindMissing[Find missing tests]

    FindMissing --> Loop{For each missing test}
    Loop --> CheckType{Type?}

    CheckType -->|Function| GenFunc[Generate test function]
    CheckType -->|Class| GenClass[Generate test class]
    CheckType -->|Method| GenMethod[Generate test method]

    GenFunc --> Write[Write to test file]
    GenClass --> Write
    GenMethod --> Write

    Write --> Loop
    Loop --> End([Test skeletons created])

    style Start fill:#3776AB
    style End fill:#2E7D32
```

## Plugin Architecture

### ConfigFile Plugin System

```mermaid
classDiagram
    class ConfigFile {
        <<abstract>>
        +get_configs() dict
        +get_filename() str
        +get_parent_path() Path
        +init() None
        +validate() bool
    }

    class YamlConfigFile {
        <<abstract>>
        +write_to_file()
        +read_from_file()
    }

    class TomlConfigFile {
        <<abstract>>
        +write_to_file()
        +read_from_file()
    }

    class PyprojectConfigFile {
        +get_configs() dict
        +get_filename() str
    }

    class PreCommitConfigFile {
        +get_configs() dict
        +get_filename() str
    }

    class CustomConfigFile {
        +get_configs() dict
        +get_filename() str
    }

    ConfigFile <|-- YamlConfigFile
    ConfigFile <|-- TomlConfigFile
    YamlConfigFile <|-- PreCommitConfigFile
    TomlConfigFile <|-- PyprojectConfigFile
    ConfigFile <|-- CustomConfigFile

    note for ConfigFile "Base class for all config files\nAutomatically discovered across packages"
    note for CustomConfigFile "User-defined config files\nin custom packages"
```

### Builder Plugin System

```mermaid
classDiagram
    class Builder {
        <<abstract>>
        +create_artifacts(temp_dir) None
        +get_app_name() str
        +get_non_abstract_subclasses() list
    }

    class PyInstallerBuilder {
        +create_artifacts(temp_dir) None
    }

    class CustomBuilder {
        +create_artifacts(temp_dir) None
    }

    class OpenAPIBuilder {
        +create_artifacts(temp_dir) None
    }

    class K8sManifestBuilder {
        +create_artifacts(temp_dir) None
    }

    Builder <|-- PyInstallerBuilder
    Builder <|-- CustomBuilder
    Builder <|-- OpenAPIBuilder
    Builder <|-- K8sManifestBuilder

    note for Builder "Base class for all builders\nAutomatically discovered across packages"
    note for CustomBuilder "User-defined builders\nin custom packages"
```

## Multi-Package Discovery

### Cross-Package Module Discovery

```mermaid
graph TB
    subgraph "Discovery Process"
        A[Start: Find all packages depending on pyrig] --> B[For each package]
        B --> C{Has module pattern?}
        C -->|Yes| D[Import module]
        C -->|No| E[Skip package]
        D --> F[Find all subclasses]
        F --> G[Add to collection]
        G --> B
        E --> B
        B --> H[Return all discovered classes]
    end

    subgraph "Example: ConfigFile Discovery"
        P1[pyrig.dev.configs] --> D1[PyprojectConfigFile]
        P1 --> D2[GitignoreConfigFile]
        P2[base_pkg.dev.configs] --> D3[CompanyStandardsConfigFile]
        P3[my_app.dev.configs] --> D4[AppSpecificConfigFile]

        D1 --> Result[All ConfigFiles]
        D2 --> Result
        D3 --> Result
        D4 --> Result
    end

    H --> Result

    style P1 fill:#3776AB
    style P2 fill:#FF8C00
    style P3 fill:#646464
```

### Fixture Discovery and Registration

```mermaid
sequenceDiagram
    participant Pytest
    participant Conftest
    participant Discovery
    participant DepGraph
    participant Fixtures

    Pytest->>Conftest: Load tests/conftest.py
    Conftest->>Discovery: Register pyrig.dev.tests.conftest
    Discovery->>DepGraph: Get all packages depending on pyrig
    DepGraph-->>Discovery: [pyrig, base_pkg, my_app]

    loop For each package
        Discovery->>Discovery: Look for pkg.dev.tests.fixtures
        Discovery->>Fixtures: Find all .py files
        Fixtures-->>Discovery: [fixture1.py, fixture2.py, ...]
        Discovery->>Discovery: Convert to module names
    end

    Discovery->>Pytest: Register as pytest_plugins
    Pytest->>Pytest: Load all fixtures
    Pytest-->>Conftest: Fixtures available globally
```

## Component Interaction

### CLI Command Flow

```mermaid
graph LR
    subgraph "User Input"
        CMD[uv run my-app deploy]
    end

    subgraph "CLI System"
        Parse[Parse command]
        Discover[Discover shared_subcommands]
        Register[Register commands]
        Execute[Execute command]
    end

    subgraph "Discovery Chain"
        P[pyrig.dev.cli.shared_subcommands]
        B[base.dev.cli.shared_subcommands]
        A[my_app.dev.cli.shared_subcommands]
    end

    CMD --> Parse
    Parse --> Discover
    Discover --> P
    Discover --> B
    Discover --> A
    P --> Register
    B --> Register
    A --> Register
    Register --> Execute

    style P fill:#3776AB
    style B fill:#FF8C00
    style A fill:#646464
```

## See Also

- [Getting Started Guide](getting-started.md) - Initial project setup
- [Multi-Package Architecture](multi-package-architecture.md) - Detailed multi-package guide
- [Configuration Files Reference](config-files/) - All config file documentation


