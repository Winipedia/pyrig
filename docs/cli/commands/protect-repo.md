# protect-repo

Configures repository protection settings and branch protection rulesets on GitHub.

## Usage

```bash
uv run pyrig protect-repo
```

## What It Does

The `protect-repo` command applies pyrig's opinionated security defaults to your GitHub repository in two steps:

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

Creates or updates a ruleset named `main protection` with comprehensive protection rules:

#### Deletion Protection
Prevents deletion of the main branch.

#### Non-Fast-Forward Protection
Prevents force pushes that rewrite history.

#### Creation Protection
Controls branch creation patterns.

#### Update Protection
Requires pull requests for updates.

#### Pull Request Requirements
- **Required Approving Reviews**: 1 approval required
- **Dismiss Stale Reviews**: Reviews dismissed when new commits pushed
- **Code Owner Review**: Requires approval from code owners
- **Last Push Approval**: Requires approval after the last push
- **Review Thread Resolution**: All review threads must be resolved
- **Allowed Merge Methods**: Squash and rebase only

#### Linear History Requirement
Enforces linear commit history (no merge commits).

#### Signature Requirement
Requires signed commits for security.

#### Status Check Requirements
- **Strict Policy**: Branch must be up to date before merging
- **Do Not Enforce on Create**: Disabled
- **Required Checks**: Health Check workflow must pass

Note: The other workflows are not triggered by a passing helath chekc here because it is not running on main when doing a Pull Request.

#### Bypass Actors
Repository admins can bypass all rules (actor_id: 5, actor_type: RepositoryRole, bypass_mode: always).

## Environment Variables

Requires `REPO_TOKEN` environment variable with GitHub personal access token.

### Required Token Permissions

The token must have these permissions:
- `administration: read, write`

Not required by protect-repo but required for other pyrig commands:
- `contents: read, write`
- `pages: read, write`

## When to Use

You should not hav eto use it as it runs as part of the health check workflow.

But in case you want to run it manually you can use `protect-repo` when:
- Setting up a new repository
- Updating protection rules after changes
- Ensuring repository follows security best practices

## Autouse Fixture

This command **runs automatically** in the Health Check workflow during CI/CD. See [Health Check Workflow](../../configs/workflows/health_check.md) for details.

The command is called in the "Protect Repository" step to ensure protection rules are always up to date.

## Related

- [Health Check Workflow](../../configs/workflows/health_check.md) - Calls protect-repo in CI/CD
- [GitHub Rulesets API](https://docs.github.com/en/rest/repos/rules) - GitHub API documentation

