# Security

pyrig implements a comprehensive security-first approach through automated scanning, branch protection, and enforced code review policies. This document covers all security features and how to configure them.

## Overview

pyrig's security model includes:

- **Bandit** — Static security analysis for Python code
- **Branch Protection** — GitHub rulesets preventing unauthorized changes
- **Signed Commits** — Cryptographic verification of commit authorship
- **Required Status Checks** — CI must pass before merging
- **Code Review** — Mandatory pull request reviews
- **Pre-commit Hooks** — Security checks run before every commit

## Security Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Security Pipeline                                  │
└─────────────────────────────────────────────────────────────────────────────┘

  Developer writes code
           │
           ▼
  ┌─────────────────────┐
  │   Pre-commit Hooks  │
  │  • Ruff linting     │
  │  • Ruff formatting  │
  │  • Ty type check    │
  │  • Mypy type check  │
  │  • Bandit security  │◄── Security scan before commit
  └─────────────────────┘
           │
           ▼
  ┌─────────────────────┐
  │   Push to Branch    │
  └─────────────────────┘
           │
           ▼
  ┌─────────────────────┐
  │   Pull Request      │
  │  • Code review      │◄── Required approving review
  │  • Status checks    │◄── CI must pass
  │  • Signed commits   │◄── Verified signatures
  └─────────────────────┘
           │
           ▼
  ┌─────────────────────┐
  │   Health Check CI   │
  │  • Run pre-commit   │◄── Bandit runs again in CI
  │  • Run tests        │
  │  • Protect repo     │◄── Update branch protection
  └─────────────────────┘
           │
           ▼
  ┌─────────────────────┐
  │   Merge to main     │
  │  (squash or rebase) │◄── Linear history enforced
  └─────────────────────┘
```

## Bandit Security Scanning

[Bandit](https://bandit.readthedocs.io/) is a static analysis tool that finds common security issues in Python code.

### Configuration

Bandit is configured in `pyproject.toml`:

```toml
[tool.bandit]
exclude_dirs = [
    ".*",    # Exclude hidden directories
]

[tool.bandit.assert_used]
skips = [
    "*test_*.py",    # Allow assert in test files
]
```

### Pre-commit Integration

Bandit runs automatically before every commit:

```yaml
# .pre-commit-config.yaml
- id: check-security
  name: check-security
  entry: bandit -c pyproject.toml -r .
  language: system
  always_run: true
  pass_filenames: false
```

### What Bandit Detects

| Issue ID | Description | Severity |
|----------|-------------|----------|
| B101 | Use of assert detected | Low |
| B102 | Use of exec detected | Medium |
| B103 | Hardcoded password in function argument | High |
| B104 | Hardcoded bind all interfaces | Medium |
| B105 | Hardcoded password string | Low |
| B106 | Hardcoded password in function call | Low |
| B107 | Hardcoded password as default value | Low |
| B108 | Probable insecure temp file/directory usage | Medium |
| B110 | Try/except/pass detected | Low |
| B201 | Flask app with debug=True | High |
| B301-B320 | Pickle/marshal/yaml/xml vulnerabilities | Medium-High |
| B501-B509 | SSL/TLS verification issues | High |
| B601-B610 | Shell injection risks | High |
| B701-B703 | Jinja2 template issues | Medium |

### Running Bandit Manually

```bash
# Run on entire project
bandit -c pyproject.toml -r .

# Run on specific file
bandit -c pyproject.toml path/to/file.py

# Run with verbose output
bandit -c pyproject.toml -r . -v

# Generate JSON report
bandit -c pyproject.toml -r . -f json -o bandit-report.json
```

### Suppressing False Positives

Use `# nosec` comments to suppress specific warnings:

```python
# Suppress specific check
password = "example"  # nosec: B105

# Suppress with reason
subprocess.run(cmd, shell=True)  # nosec: B602 - Input is validated
```

## Branch Protection

pyrig automatically configures GitHub branch protection via the `protect-repo` command.

### Running Protection

```bash
# Apply all protection rules
uv run pyrig protect-repo
```

This command:
1. Configures repository settings
2. Creates or updates the branch ruleset

### Repository Settings

The following settings are applied:

```python
repo.edit(
    name=repo_name,
    description=toml_description,      # From pyproject.toml
    default_branch="main",
    delete_branch_on_merge=True,       # Auto-delete merged branches
    allow_update_branch=True,          # Enable "Update branch" button
    allow_merge_commit=False,          # Disable merge commits
    allow_rebase_merge=True,           # Allow rebase merging
    allow_squash_merge=True,           # Allow squash merging
)
```

| Setting | Value | Purpose |
|---------|-------|---------|
| `delete_branch_on_merge` | `true` | Clean up merged feature branches |
| `allow_merge_commit` | `false` | Enforce linear history |
| `allow_rebase_merge` | `true` | Allow clean rebasing |
| `allow_squash_merge` | `true` | Allow squashing commits |

### Branch Ruleset

pyrig creates a ruleset named "default" with the following rules:

```python
rules = get_rules_payload(
    deletion={},                          # No branch deletion
    non_fast_forward={},                  # No force pushes
    creation={},                          # Controlled branch creation
    update={},                            # Controlled updates
    pull_request={
        "required_approving_review_count": 1,
        "dismiss_stale_reviews_on_push": True,
        "require_code_owner_review": True,
        "require_last_push_approval": True,
        "required_review_thread_resolution": True,
        "allowed_merge_methods": ["squash", "rebase"],
    },
    required_linear_history={},           # No merge commits
    required_signatures={},               # Signed commits required
    required_status_checks={
        "strict_required_status_checks_policy": True,
        "do_not_enforce_on_create": False,
        "required_status_checks": [
            {"context": "health_check"}
        ],
    },
)
```

### Ruleset Breakdown

| Rule | Effect |
|------|--------|
| `deletion` | Prevents branch deletion (except by admins) |
| `non_fast_forward` | Prevents force pushes |
| `creation` | Controls who can create branches |
| `update` | Controls who can push to branches |
| `pull_request` | Requires PR reviews before merging |
| `required_linear_history` | Prevents merge commits |
| `required_signatures` | Requires signed commits |
| `required_status_checks` | CI must pass before merging |

## Pull Request Requirements

The `pull_request` rule enforces:

| Parameter | Value | Description |
|-----------|-------|-------------|
| `required_approving_review_count` | 1 | At least one approval required |
| `dismiss_stale_reviews_on_push` | true | New commits invalidate old approvals |
| `require_code_owner_review` | true | Code owner must approve |
| `require_last_push_approval` | true | Approver must not be the last pusher |
| `required_review_thread_resolution` | true | All comments must be resolved |
| `allowed_merge_methods` | ["squash", "rebase"] | Only squash or rebase allowed |

## Signed Commits

pyrig requires signed commits via the `required_signatures` rule.

### Setting Up GPG Signing

```bash
# Generate a GPG key
gpg --full-generate-key

# List your keys
gpg --list-secret-keys --keyid-format=long

# Get your key ID (after sec rsa4096/)
gpg --list-secret-keys --keyid-format=long | grep sec

# Configure Git to use your key
git config --global user.signingkey YOUR_KEY_ID
git config --global commit.gpgsign true

# Export public key for GitHub
gpg --armor --export YOUR_KEY_ID
```

### Adding Key to GitHub

1. Go to GitHub → Settings → SSH and GPG keys
2. Click "New GPG key"
3. Paste your exported public key
4. Click "Add GPG key"

### Signing Commits

```bash
# Sign a single commit
git commit -S -m "Your message"

# Enable signing by default
git config --global commit.gpgsign true

# Sign all commits automatically (default after config)
git commit -m "Your message"
```

## Required Status Checks

The `required_status_checks` rule ensures CI passes before merging:

```python
required_status_checks={
    "strict_required_status_checks_policy": True,
    "do_not_enforce_on_create": False,
    "required_status_checks": [
        {"context": "health_check.yaml"}
    ],
}
```

| Parameter | Value | Description |
|-----------|-------|-------------|
| `strict_required_status_checks_policy` | true | Branch must be up-to-date with base |
| `do_not_enforce_on_create` | false | Enforce even on new branches |
| `required_status_checks` | ["health_check.yaml"] | CI workflow must pass |

## Pre-commit Hooks

pyrig generates a `.pre-commit-config.yaml` with security checks:

```yaml
repos:
- repo: local
  hooks:
  - id: lint-code
    name: lint-code
    entry: ruff check --fix
    language: system
    always_run: true
    pass_filenames: false

  - id: format-code
    name: format-code
    entry: ruff format
    language: system
    always_run: true
    pass_filenames: false

  - id: check-types
    name: check-types
    entry: ty check
    language: system
    always_run: true
    pass_filenames: false

  - id: check-static-types
    name: check-static-types
    entry: mypy --exclude-gitignore
    language: system
    always_run: true
    pass_filenames: false

  - id: check-security
    name: check-security
    entry: bandit -c pyproject.toml -r .
    language: system
    always_run: true
    pass_filenames: false
```

### Installing Pre-commit Hooks

```bash
# Install hooks (runs automatically during pyrig init)
uv run pre-commit install

# Run all hooks manually
uv run pre-commit run --all-files

# Run specific hook
uv run pre-commit run check-security --all-files

# Update hooks to latest versions
uv run pre-commit autoupdate
```

## CI Security Integration

The health check workflow runs security checks in CI:

```yaml
# .github/workflows/health_check.yaml
steps:
  - name: Run Pre Commit Hooks
    id: run_pre_commit_hooks
    run: uv run pre-commit run --all-files
```

This ensures:
- All pre-commit hooks pass (including Bandit)
- Consistent checks between local and CI environments
- Security issues are caught even if local hooks are skipped

## Required Secrets

### REPO_TOKEN

A GitHub personal access token with repository permissions:

```yaml
env:
  REPO_TOKEN: ${{ secrets.REPO_TOKEN }}
```

Required scopes:
- `repo` — Full repository access
- `admin:repo_hook` — Repository hooks management
- `workflow` — Workflow management

### Setting Up REPO_TOKEN

1. Go to GitHub → Settings → Developer settings → Personal access tokens
2. Generate new token (classic)
3. Select scopes: `repo`, `admin:repo_hook`, `workflow`
4. Copy the token
5. Go to your repository → Settings → Secrets and variables → Actions
6. Add new secret: Name = `REPO_TOKEN`, Value = your token

## Customizing Security

### Disabling Specific Bandit Checks

```toml
# pyproject.toml
[tool.bandit]
skips = ["B101", "B601"]    # Skip specific checks
```

### Custom Pre-commit Hooks

Override `PreCommitConfigConfigFile` to add custom hooks:

```python
# your_project/dev/configs/git/pre_commit.py
from pyrig.dev.configs.git.pre_commit import PreCommitConfigConfigFile as Base

class PreCommitConfigConfigFile(Base):
    @classmethod
    def get_configs(cls) -> dict[str, Any]:
        config = super().get_configs()
        # Add custom security hook
        config["repos"][0]["hooks"].append({
            "id": "check-secrets",
            "name": "check-secrets",
            "entry": "detect-secrets-hook",
            "language": "system",
            "always_run": True,
            "pass_filenames": False,
        })
        return config
```

### Custom Branch Protection

Override protection in your project:

```python
# your_project/src/git/github/repo/protect.py
from pyrig.src.git.github.repo.protect import get_default_ruleset_params as base_params

def get_default_ruleset_params() -> dict[str, Any]:
    params = base_params()
    # Customize rules
    params["rules"]["pull_request"]["required_approving_review_count"] = 2
    return params
```

## Troubleshooting

### Bandit blocks commit

**Cause**: Security issue detected in code.

**Solution**:
1. Review the flagged code
2. Fix the security issue, OR
3. Add `# nosec` comment with justification

### "Commit signature verification failed"

**Cause**: Commit not signed or key not in GitHub.

**Solution**:
1. Ensure GPG key is configured: `git config --global commit.gpgsign true`
2. Add public key to GitHub
3. Sign the commit: `git commit --amend -S`

### "Required status check hasn't completed"

**Cause**: CI hasn't run or is still running.

**Solution**:
1. Wait for CI to complete
2. Check workflow run in GitHub Actions tab
3. Fix any failing checks

### "Review required" but can't merge

**Cause**: Missing approval or stale review.

**Solution**:
1. Request a new review
2. Ensure reviewer is not the last pusher
3. Resolve all review comments

### "Cannot force push"

**Cause**: `non_fast_forward` rule prevents force pushes.

**Solution**:
1. Create a new commit instead of amending
2. Use `git revert` instead of resetting
3. (Admin only) Temporarily disable the rule

## Summary

| Security Feature | Implementation | Enforcement |
|-----------------|----------------|-------------|
| **Static Analysis** | Bandit in pyproject.toml | Pre-commit + CI |
| **Code Quality** | Ruff linting and formatting | Pre-commit + CI |
| **Type Safety** | Ty and Mypy (strict mode) | Pre-commit + CI |
| **Code Review** | GitHub PR requirements | Branch ruleset |
| **Signed Commits** | GPG signature verification | Branch ruleset |
| **Status Checks** | Health check workflow | Branch ruleset |
| **Linear History** | Squash/rebase only | Repository settings |
| **Branch Protection** | No force push/delete | Branch ruleset |

