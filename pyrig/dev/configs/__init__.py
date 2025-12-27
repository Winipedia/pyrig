"""Declarative configuration file management system.

Provides the ConfigFile system for automatic discovery, creation, validation,
and updating of project configuration files.
Uses subset validation to preserve user customizations while
ensuring required configuration exists.

Architecture:
    - Automatic subclass discovery across packages
    - Priority-based initialization (parallel within priority groups)
    - Subset validation (only adds missing values, never removes)
    - Multiple formats: YAML, TOML, JSON, Python, Markdown, text

Base Classes:
    base.base.ConfigFile: Abstract base
    base.toml.TomlConfigFile: TOML files
    base.yaml.YamlConfigFile: YAML files
    base.python.PythonConfigFile: Python files
    base.markdown.MarkdownConfigFile: Markdown files

Core Config Files:
    pyproject.PyprojectConfigFile: pyproject.toml
    git.gitignore.GitIgnoreConfigFile: .gitignore
    git.pre_commit.PreCommitConfigFile: .pre-commit-config.yaml
    docs.mkdocs.MkDocsConfigFile: mkdocs.yml
    workflows.*: GitHub Actions workflows

How It Works:
    1. Run `pyrig mkroot` or `ConfigFile.init_all_subclasses()`
    2. Discover all ConfigFile subclasses
    3. Group by priority, initialize in parallel
    4. For each file: create if missing, validate, add missing configs

Subset Validation:
    Files are correct if empty (opt-out) OR expected config ⊆ actual config.
    Users can add extra keys, extend lists, override values.
"""
