"""Python source file configuration management.

This subpackage provides configuration file managers for Python source files
that form the structure of a pyrig-based project.

The subpackage includes managers for:
    - **Package __init__.py files**: builders_init, configs_init, resources_init,
      src_init - Create package structure mirroring pyrig's layout
    - **Entry points**: main.py - CLI entry point with argument parsing
    - **Subcommands**: subcommands.py, shared_subcommands.py - CLI command structure
    - **Scratch files**: dot_experiment.py - Local experimentation file (.experiment.py)

Key Features:
    - Automatic package structure generation
    - CLI scaffolding with subcommands
    - Module copying and mirroring from pyrig
    - Gitignored scratch file for experiments
    - Proper Python package initialization

Modules:
    builders_init: dev/artifacts/builders/__init__.py configuration
    configs_init: dev/configs/__init__.py configuration
    resources_init: resources/__init__.py configuration
    src_init: src/__init__.py configuration
    main: main.py CLI entry point configuration
    subcommands: subcommands.py CLI commands configuration
    shared_subcommands: shared_subcommands.py shared CLI commands configuration
    dot_experiment: .experiment.py scratch file configuration

See Also:
    pyrig.dev.configs.base.init.InitConfigFile
        Base class for __init__.py files
    pyrig.dev.configs.base.copy_module.CopyModuleConfigFile
        Base class for copying Python modules
"""
