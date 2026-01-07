# protect-repo

Configures repository protection settings and branch protection rulesets on
GitHub.

## Usage

```bash
uv run pyrig protect-repo

# With verbose output to see API requests and responses
uv run pyrig -v protect-repo

# With detailed debug logging
uv run pyrig -vv protect-repo
```

## What It Does

The `protect-repo` command applies pyrig's opinionated security defaults to your
GitHub repository in two steps:

### 1. Repository Settings

Configures repository-level settings:

- **Description**: Sets from `pyproject.toml` project description
- **Default Branch**: Sets to `main`
- **Delete Branch on Merge**: Enabled (keeps repository clean)
- **Allow Update Branch**: Enabled (allows updating PR branches)
- **Merge Commits**: Disabled (enforces squash or rebase for linear history)
- **Rebase Merge**: Enabled
- **Squash Merge**: Enabled

### 2. Branch Protection Ruleset

Creates or updates a ruleset named `main-protection` with comprehensive
protection rules loaded from `branch-protection.json`. Key protections include:

- Required pull request reviews with code owner approval
- Required status checks (health check workflow must pass)
- Linear commit history enforcement
- Signed commits requirement
- Force push and branch deletion prevention

Repository administrators can bypass these rules when necessary.

See [branch-protection.json documentation](../../configs/branch_protection.md)
for the complete list of protection rules and their configuration.

## Configuration File

The branch protection rules are defined in `branch-protection.json`, which is
automatically generated when you run `uv run pyrig mkroot`.

This approach provides:

- **Version control**: Protection rules are tracked in git
- **Transparency**: Rules are visible in a standard JSON format
- **Portability**: File can be manually uploaded to GitHub if needed
- **Customization**: Override the configuration class to modify rules

## Environment Variables

Requires `REPO_TOKEN` environment variable with GitHub personal access token.

### Required Token Permissions

The token must have these permissions:

- `administration: read, write`

Not required by protect-repo but required for other pyrig commands:

- `contents: read, write`
- `pages: read, write`

## When to Use

You should not have to use it as it runs as part of the health check workflow.

But in case you want to run it manually you can use `protect-repo` when:

- Setting up a new repository
- Updating protection rules after changes
- Ensuring repository follows security best practices

## Automatic Execution

This command **runs automatically** in the Health Check workflow during CI/CD.
See [Health Check Workflow](../../configs/workflows/health_check.md) for
details.

The command is called in the "Protect Repository" step to ensure protection
rules are always up to date.

## Related

- [branch-protection.json](../../configs/branch_protection.md) - Configuration
  file used by this command
- [Health Check Workflow](../../configs/workflows/health_check.md) - Calls
  protect-repo in CI/CD
- [GitHub Rulesets API](https://docs.github.com/en/rest/repos/rules) - GitHub
  API documentation
