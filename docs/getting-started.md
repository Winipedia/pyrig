# Getting Started

This is a complete guide to setting up a new python project from scratch with pyrig.

pyrig provides **minimal best practices fully working defaults for everything a
project needs**. This guide will walk you through setting up a complete,
production-ready Python project in a few minutes.

## Quick Start

To get started immediately with only the essentials simply create
a new project directory, navigate into it, and run:

```bash
uv init my-project --python 3.12
cd my-project
uv add pyrig
uv run pyrig init
```

This will set up a complete python project with all of pyrig's best practices
fully working from the start. The only thing the full setup guide will add to this
is setting up your repository with GitHub and the CI/CD pipeline properly.
We recommend following the full setup guide, especially if you want anything
that needs a remote repository and/or CI/CD to work,
but if you just want to get going with a local project and add the repository
and CI/CD setup later, this is the fastest way to get started.

## Full Setup Guide

### Required Software

**Python 3.12+**:
pyrig requires Python 3.12 or higher to run. You can seamlessly manage
multiple Python versions with uv's built-in python version management.

**Git**:
Pyrig requires you to have git installed for version control.
One of pyrig's standards is that your git username should match your GitHub username
because pyrig uses the values set in your git's username and email to insert them
into files, like your username as an author in pyproject.toml and your email in
the CODE_OF_CONDUCT.md. The git username is only a fallback in case the repository's
remote URL is not set, so if you have already cloned your repository before
running `pyrig init`, pyrig will use the GitHub username parsed from the
remote URL instead of the git username.

```bash
# Verify installation
git --version

# Configure user (should match GitHub username)
git config --global user.name "YourGitHubUsername"
git config --global user.email "your.email@example.com"
```

**Signed Commits** (recommended):

Setting up signed commits is highly recommended for verifying commit
authenticity. However, since the repository owner has overwrite rights, it's
not strictly required when you initialize the project yourself.
We highly recommend setting this up if not done so already as it just good
practice and adds a layer of security to your repository.

See [GitHub's guide on signing commits](https://docs.github.com/en/authentication/managing-commit-signature-verification) for detailed setup instructions.

**uv** (Python package manager):

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify installation
uv --version
```

### Accounts & Tokens

**GitHub Account**:

You will need an account for [github.com](https://github.com)

**GitHub Personal Access Token (REPO_TOKEN)** - **Required**:

1. Go to GitHub Settings → Developer settings → Personal access tokens →
Fine-grained tokens
2. Under Repository permissions, set:
   - Administration: Read and write (for `pyrig protect-repo`)
   - Pages: Read and write (for enabling GitHub Pages)
3. Generate token
4. **Copy token immediately** (you won't see it again)
5. Add token to your repository secrets as `REPO_TOKEN`

## Setup Steps

### 1. Create GitHub Repository

On github.com, create a new repository for your project.
It must have the same name that you want your project to have.
This is one of pyrig's standards.
You can but do not have to initialize the repository with a
README, .gitignore, or license - pyrig will add all of those.
But if you do not want a standard MIT license you can add a custom one
when creating the repo and pyrig will not overwrite it.

### 2. Clone Repository

We highly recommend using ssh to clone your repository as it is more secure
but pyrig will work with https as well.

```bash
git clone git@github.com:YourUsername/my-project.git
# navigate into project directory
cd my-project

# Verify remote is set
git remote -v
# Should show: origin  git@github.com:YourUsername/my-project.git
```

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

### 5. Add Any Plugins You Want (optional)

pyrig is extensible through plugins. A plugin is just a package that pyrig
discovers automatically — adding it as a dependency is all it takes for its
tools, config files, and workflow steps to be picked up by `pyrig init`.
Add any of the plugins you want before running `pyrig init` so they are
included in the initial scaffold:

```bash
# Publish your package to PyPI from CI/CD
uv add pyrig-pypi

# Upload test coverage reports to Codecov
uv add pyrig-codecov

# Build standalone executables of your project
uv add pyrig-executables
```

### 6. Run pyrig init

This will create an initial commit of the scaffolded and initialized project.

```bash
# Initialize pyrig project
uv run pyrig init
```

### 7. Push to GitHub

Make sure you have the necessary tokens and secrets set up before
pushing so that the CI/CD pipeline can run successfully on push.

```bash
# Push initial commit
git push -u origin main
```

### 8. Verify Workflows

On GitHub.com:

1. Go to Actions tab
2. Health Check workflow should run automatically,
followed by Release workflow and Deploy workflow
3. Verify all jobs run successfully
(should just take a 2-3 minutes on an empty project)

### 9. Start coding

Start coding under the `src/my_project/` directory.

Add commands to your CLI with `pyrig mk cmd` and start building your project!
Generate test skeletons with `pyrig sync` and watch your CI/CD pipeline
run on every push.
