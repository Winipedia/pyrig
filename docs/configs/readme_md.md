# README.md Configuration

The `ReadmeConfigFile` manages the `README.md` file, which serves as the
homepage for your GitHub repository.

## Overview

Creates a README file that:

- Uses the project name as the header
- Includes all standard badges (tooling, code quality, package info, CI/CD,
  documentation)
- Displays the project description from `pyproject.toml`
- Provides a professional first impression for repository visitors
- Allows users to add custom content below the header
- Is always required (never marked as unwanted)

## Inheritance

```mermaid
graph TD
    A[ConfigFile] --> B[ListConfigFile]
    B --> C[StringConfigFile]
    C --> D[MarkdownConfigFile]
    D --> E[BadgesMarkdownConfigFile]
    E --> F[ReadmeConfigFile]

    style A fill:#a8dadc,stroke:#333,stroke-width:2px,color:#000
    style B fill:#457b9d,stroke:#333,stroke-width:2px,color:#fff
    style C fill:#f4a261,stroke:#333,stroke-width:2px,color:#000
    style D fill:#e76f51,stroke:#333,stroke-width:2px,color:#000
    style E fill:#9d84b7,stroke:#333,stroke-width:2px,color:#000
    style F fill:#90be6d,stroke:#333,stroke-width:2px,color:#000
```

**Inherits from**: `BadgesMarkdownConfigFile`

**What this means**:

- Markdown file format (`.md` extension)
- Automatically generates badges from project metadata
- Includes project name and description
- Validation checks for required elements (badges, description, project name)
- Users can add content after the generated header
- File is considered correct if it contains all required elements

## File Location

**Path**: `README.md` (project root)

**Extension**: `.md` - Standard Markdown extension.

**Filename**: `README` - The standard repository documentation file recognized
by GitHub, GitLab, and other platforms.

**Special filename handling**: `get_filename()` returns `"README"` (uppercase)
to follow convention.

## How It Works

### Automatic Generation

When initialized via `uv run pyrig mkroot`, the `README.md` file is created
with:

1. **Project name header**: Uses project name from `pyproject.toml`
2. **Badge sections**: Five categories of badges (tooling, code quality, package
   info, CI/CD, documentation)
3. **Project description**: Quoted description from `pyproject.toml`
4. **Horizontal rules**: Visual separators for clean layout

### Generated Content

For a project named "myapp" with description "A sample application":

```markdown
# myapp

<!-- tooling -->

[![pyrig](https://img.shields.io/badge/built%20with-pyrig-3776AB?logo=buildkite&logoColor=black)](https://github.com/Winipedia/pyrig)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Container](https://img.shields.io/badge/Container-Podman-A23CD6?logo=podman&logoColor=grey&colorA=0D1F3F&colorB=A23CD6)](https://podman.io/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://pre-commit.com/)
[![MkDocs](https://img.shields.io/badge/MkDocs-Documentation-326CE5?logo=mkdocs&logoColor=white)](https://www.mkdocs.org/)

<!-- code-quality -->

[![ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![ty](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ty/main/assets/badge/v0.json)](https://github.com/astral-sh/ty)
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![pytest](https://img.shields.io/badge/tested%20with-pytest-46a2f1.svg?logo=pytest)](https://pytest.org/)
[![codecov](https://codecov.io/gh/owner/myapp/branch/main/graph/badge.svg)](https://codecov.io/gh/owner/myapp)
[![rumdl](https://img.shields.io/badge/markdown-rumdl-darkgreen)](https://github.com/rvben/rumdl)

<!-- package-info -->

[![PyPI](https://img.shields.io/pypi/v/myapp?logo=pypi&logoColor=white)](https://pypi.org/project/myapp/)
[![Python](https://img.shields.io/badge/python-3.10|3.11|3.12-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/github/license/owner/myapp)](https://github.com/owner/myapp/blob/main/LICENSE)

<!-- ci/cd -->

[![CI](https://img.shields.io/github/actions/workflow/status/owner/myapp/health_check.yaml?label=CI&logo=github)](https://github.com/owner/myapp/actions/workflows/health_check.yaml)
[![CD](https://img.shields.io/github/actions/workflow/status/owner/myapp/release.yaml?label=CD&logo=github)](https://github.com/owner/myapp/actions/workflows/release.yaml)

<!-- documentation -->

[![Documentation](https://img.shields.io/badge/Docs-GitHub%20Pages-black?style=for-the-badge&logo=github&logoColor=white)](https://owner.github.io/myapp)

---

> A sample application

---
```

### Content Generation Logic

The `ReadmeConfigFile` inherits content generation from
`BadgesMarkdownConfigFile` without modification.

**Key behavior**:

- Uses project name as-is (unlike `IndexConfigFile` which adds " Documentation")
- Organizes badges by category with HTML comments
- Wraps description in blockquote
- Adds horizontal rules for visual separation

## Dynamic Configuration

The README adapts to your project automatically:

### Project Name

Automatically uses your project name from `pyproject.toml` `[project]` `name`
field.

### Project Description

Displays the project description from `pyproject.toml` `[project]` `description`
field as a blockquote below the badges.

### Repository Information

Extracts repository owner and name from Git remote URL for badge links.

### Python Versions

Shows supported Python versions from `pyproject.toml` `requires-python` field in
the Python badge (e.g., `3.10|3.11|3.12`).

## Badge Categories

Badges are organized into five categories: tooling, code quality, package info,
CI/CD, and documentation. See [Index.md](index_md.md) for the complete badge
list.

## Usage

### Automatic Creation

The file is automatically created when you run:

```bash
uv run pyrig mkroot
```

### Adding Custom Content

Simply add your content after the generated header.

The validation only checks that required elements exist, so you can add as much
content as you want.

### Validation Logic

The validation checks that the README file contains all required elements:

**Required elements**:

1. All badges from all categories
2. Project description
3. Project name

**Flexible structure**: As long as these elements exist somewhere in the file,
it's considered valid. You can add custom content anywhere.

### Always Required

The `README.md` file is always required and never marked as unwanted. This
ensures it's never removed or skipped during project initialization.

**Note**: We can't think of a reason why you would not want a README.md file,
but if you need to override this behavior, you can subclass `ReadmeConfigFile`
and override `is_unwanted()` to return `True`.

## Best Practices

1. **Keep the header**: Don't remove the generated badges and description
2. **Add content below**: Append your README content after the horizontal rules
3. **Be concise**: README should be a quick overview, not full documentation
4. **Include essentials**: Installation, quick start, features, links to docs
5. **Update description**: Keep `pyproject.toml` description current
6. **Link to documentation**: Point readers to full docs for details
