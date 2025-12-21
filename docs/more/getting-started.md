# Getting Started

Complete guide to setting up a new pyrig project from scratch.

## Prerequisites

### Required Software

**Git**:
```bash
# Verify installation
git --version

# Configure user (should match GitHub username)
git config --global user.name "YourGitHubUsername"
git config --global user.email "your.email@example.com"
```

**uv** (Python package manager):
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify installation
uv --version
```

**Podman** (for containerization):
```bash
# Linux
sudo apt install podman  # Debian/Ubuntu
sudo dnf install podman  # Fedora

# macOS
brew install podman

# Verify installation
podman --version
```

### Required Accounts & Tokens

**GitHub Account**:
- Create account at [github.com](https://github.com)
- Verify email address

**GitHub Personal Access Token (REPO_TOKEN)**:
1. Go to GitHub Settings → Developer settings → Personal access tokens → Fine-grained tokens
2. Select scopes:
   - `administration: read, write` (for `pyrig protect-repo`)
   - `contents: read, write` (for CI/CD)
   - `pages: read, write` (for GitHub Pages)
3. Click "Generate token"
4. **Copy token immediately** (you won't see it again)
5. Add token to your repository secrets

**PyPI Token (PYPI_TOKEN)** (optional, for publishing):
1. Create account at [pypi.org](https://pypi.org)
2. Create an API token
3. Scope: "Entire account" (recommended change to specific project after first publish)
4. Click "Add token"
5. **Copy token immediately** (you won't see it again)
6. Add token to your repository secrets

**Codecov Token (CODECOV_TOKEN)** (optional, for coverage reporting):
1. Create account at [codecov.io](https://codecov.io)
2. Link your GitHub account
3. Add your repository
4. Copy the repository upload token from Settings
5. Add token to your repository secrets

## Setup Steps

### 1. Create GitHub Repository

```bash
# On GitHub.com:
# 1. Click "New repository"
# 2. Name: my-project
# 3. Description: Your project description
# 4. Public or Private
# 5. You do not need to initialize with README, .gitignore bc pyrig will create it for you. (create a licence if you do not want the MIT license)
# 6. Click "Create repository"
```

### 2. Clone Repository

```bash
# Clone the empty repository
git clone https://github.com/YourUsername/my-project.git
cd my-project

# Verify remote is set
git remote -v
# Should show: origin  https://github.com/YourUsername/my-project.git
```

**Note**: Git user.name doesn't have to match GitHub username exactly, as long as `git remote -v` shows the correct GitHub URL after cloning. But if you use pyrig init before having cloned the repo and therefore not having a remote set, pyrig will default to your user name under `git config user.name`.
pyrig's init command will also work without a cloned repo, but it is recommended to clone it first and then run `uv run pyrig init` to avoid any potential issues.

### 3. Initialize Project with uv

```bash
# Initialize Python project
uv init
```

### 4. Add pyrig Dependency

```bash
# Add pyrig to project
uv add pyrig
```

### 5. Run pyrig init

```bash
# Initialize pyrig project
uv run pyrig init
```

This runs 9 steps:
1. **Adding dev dependencies** - Installs pyrig-dev
2. **Syncing venv** - Installs all dependencies
3. **Creating priority config files** - pyproject.toml, .gitignore, LICENSE, ...
4. **Syncing venv** - Installs project itself, activates CLI
5. **Creating project root** - All config files and directory structure
6. **Creating test files** - Test skeletons for all code
7. **Running pre-commit hooks** - Formats and lints code
8. **Running tests** - Validates everything works
9. **Committing initial changes** - Creates initial commit

### 7. Add Repository Secrets (for CI/CD)

On GitHub.com, go to your repository:

1. Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add each secret:

**REPO_TOKEN**:
- Name: `REPO_TOKEN`
- Secret: Your GitHub fine-grained personal access token with permissions:
  - `administration: read, write`
  - `contents: read, write`
  - `pages: read, write`
- Click "Add secret"

**PYPI_TOKEN** (optional):
- Name: `PYPI_TOKEN`
- Secret: Your PyPI token
- Click "Add secret"

**CODECOV_TOKEN** (optional, but recommended):
- Name: `CODECOV_TOKEN`
- Secret: Your Codecov token
- Click "Add secret"

### 8. Push to GitHub

```bash
# Push initial commit
git push -u origin main
```

### 9. Verify Workflows

On GitHub.com:
1. Go to Actions tab
2. Health Check workflow should run automatically
3. Verify all jobs pass (should just take a 2-3 minutes on an empty project)

## What You Get

After completing setup, your project has:

**Complete Project Structure**:
```
my-project/
├── my_project/                      # Source code package
│   ├── __init__.py
│   ├── main.py                      # CLI entry point
│   ├── py.typed                     # PEP 561 type marker
│   ├── dev/                         # Development infrastructure
│   │   ├── __init__.py
│   │   ├── builders/                # Build artifact definitions
│   │   │   └── __init__.py
│   │   ├── cli/                     # CLI command system
│   │   │   ├── __init__.py
│   │   │   ├── subcommands.py       # Project commands
│   │   │   └── shared_subcommands.py # Shared commands
│   │   ├── configs/                 # Config file managers
│   │   │   └── __init__.py
│   │   └── tests/                   # Test infrastructure
│   │       ├── __init__.py
│   │       └── fixtures/
│   │           └── __init__.py
│   ├── resources/                   # Static resources
│   │   └── __init__.py
│   └── src/                         # Application logic
│       └── __init__.py
│
├── tests/                           # Test files (mirrors source)
│   ├── __init__.py
│   ├── conftest.py                  # Pytest configuration
│   ├── test_zero.py                 # Initial test
│   └── test_my_project/             # Mirrors my_project/ structure
│       ├── __init__.py
│       ├── test_main.py
│       ├── test_dev/                # Mirrors my_project/dev/
│       │   ├── __init__.py
│       │   ├── test_builders/
│       │   │   └── __init__.py
│       │   ├── test_cli/
│       │   │   ├── __init__.py
│       │   │   ├── test_subcommands.py
│       │   │   └── test_shared_subcommands.py
│       │   ├── test_configs/
│       │   │   └── __init__.py
│       │   └── test_tests/
│       │       └── __init__.py
│       ├── test_resources/          # Mirrors my_project/resources/
│       │   └── __init__.py
│       └── test_src/                # Mirrors my_project/src/
│           └── __init__.py
│
├── docs/                            # MkDocs documentation
│   └── index.md                     # Documentation homepage
│
├── .github/                         # GitHub configuration
│   └── workflows/                   # CI/CD workflows
│       ├── health_check.yaml        # Tests, linting, type checking
│       ├── build.yaml               # Build artifacts
│       ├── release.yaml             # Version and release
│       └── publish.yaml             # PyPI and docs publishing
│
├── .env                             # Environment variables (not committed)
├── .experiment.py                   # Scratch file for local experiments (not committed)
├── .gitignore                       # Git ignore patterns
├── .pre-commit-config.yaml          # Pre-commit hooks
├── .python-version                  # Python version (3.12+)
├── Containerfile                    # Podman/Docker image definition
├── LICENSE                          # MIT license
├── README.md                        # Project readme
├── mkdocs.yml                       # MkDocs configuration
├── pyproject.toml                   # Project metadata and tool configs
└── uv.lock                          # Dependency lock file
```
- `docs/` - MkDocs documentation
- `.github/workflows/` - CI/CD workflows

**Configuration Files**:
- `pyproject.toml` - Project metadata, dependencies, tool configs
- `.gitignore` - Git ignore patterns
- `.pre-commit-config.yaml` - Pre-commit hooks
- `mkdocs.yml` - Documentation configuration
- `Containerfile` - Container image definition
- `LICENSE` - MIT license
- `.env` - Environment variables (not committed)

... and more config files detailed in [Configs Documentation](../configs/index.md)

**CI/CD Workflows**:
- **Health Check** - Runs on every PR (tests, linting, type checking)
- **Build** - Creates executables and container images
- **Release** - Version bumping and GitHub releases
- **Publish** - PyPI and documentation publishing

**Development Tools**:
- **uv** - Package management
- **ruff** - Linting and formatting
- **mypy** - Type checking
- **pytest** - Testing with 90% coverage
- **pre-commit** - Git hooks
- **MkDocs** - Documentation

**CLI Commands**:
```bash
uv run my-project --help     # Your CLI
uv run my-projectversion     # Display version
```

## Additional Resources

- [CLI Documentation](../cli/index.md) - Command reference
- [Configuration Files](../configs/index.md) - Config file details
- [Workflows](../configs/workflows/index.md) - CI/CD workflow documentation
- [Tooling](tooling.md) - Tool choices and rationale
- [Trade-offs](drawbacks.md) - What you sacrifice and gain

