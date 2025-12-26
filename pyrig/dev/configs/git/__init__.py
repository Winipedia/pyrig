"""Git-related configuration file management.

This subpackage provides configuration file managers for Git-related files that
help maintain code quality and prevent committing unwanted files.

The subpackage includes:
    - **GitIgnoreConfigFile**: Manages .gitignore patterns to exclude build
      artifacts, caches, secrets, and IDE files from version control
    - **PreCommitConfigConfigFile**: Manages .pre-commit-config.yaml to run
      automated checks (linting, formatting, type checking, security) before
      each commit

Key Features:
    - Fetches GitHub's standard Python .gitignore patterns
    - Adds pyrig-specific ignore patterns (.experiment, .env, caches)
    - Configures local pre-commit hooks for ruff, ty, bandit, and rumdl
    - Prevents committing secrets and build artifacts
    - Ensures code quality before commits

Modules:
    gitignore: .gitignore file configuration management
    pre_commit: .pre-commit-config.yaml file configuration management

See Also:
    GitHub gitignore templates: https://github.com/github/gitignore
    pre-commit framework: https://pre-commit.com/
"""
