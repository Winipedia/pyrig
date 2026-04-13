"""Git-related configuration file management.

Provides .gitignore (GitHub Python patterns + pyrig-specific),
prek.toml (local hooks for ruff, ty, bandit, rumdl), and
branch-protection.json (GitHub rulesets) to maintain code quality,
prevent committing unwanted files, and enforce branch protections.

Modules:
    branch_protection: GitHub branch protection ruleset management.
    gitignore: .gitignore file configuration management.
    pre_commit: prek.toml file configuration management.

See Also:
    GitHub gitignore templates: https://github.com/github/gitignore
    prek: https://github.com/j178/prek
"""
