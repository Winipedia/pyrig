# ReadmeConfigFile

## Overview

**File Location:** `README.md`
**ConfigFile Class:** `ReadmeConfigFile`
**File Type:** Markdown
**Priority:** Standard

Creates the project's README.md file with a professional header including badges, project name, and description. The README serves as the entry point for anyone discovering your project.

## Purpose

The `README.md` file provides project documentation:

- **Project Introduction** - First impression for users and contributors
- **Status Badges** - Visual indicators of project health and tooling
- **PyPI Description** - Used as the long description on PyPI
- **Documentation Entry Point** - Links to detailed documentation
- **Professional Presentation** - Consistent, polished appearance

### Why pyrig manages this file

pyrig creates `README.md` to:
1. **Immediate professionalism** - Professional README from day one
2. **Automatic badges** - All relevant badges auto-generated
3. **Consistency** - All pyrig projects have similar structure
4. **PyPI integration** - Automatically used as package description
5. **Up-to-date information** - Badges reflect current project state

The file is created during `pyrig init` with a standard header. You can add your own content below the header.

## File Location

The file is placed at the project root:

```
my-awesome-project/
├── README.md  # <-- Here
├── my_awesome_project/
│   └── __init__.py
└── pyproject.toml
```

## File Structure

### Auto-Generated Header

The file contains an auto-generated header with:

1. **Project name** (H1 heading)
2. **Badges** (organized by category)
3. **Description** (from `pyproject.toml`)
4. **Horizontal rules** (visual separation)

### Badge Categories

Badges are organized into four categories:

#### 1. Tooling Badges

Shows the development tools used:

```markdown
<!-- tooling -->
[![pyrig](https://img.shields.io/badge/built%20with-pyrig-3776AB?logo=buildkite&logoColor=black)](https://github.com/Winipedia/pyrig)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Container](https://img.shields.io/badge/Container-Podman-A23CD6?logo=podman&logoColor=grey&colorA=0D1F3F&colorB=A23CD6)](https://podman.io/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://pre-commit.com/)
```

**Badges:**
- **pyrig** - Shows project is built with pyrig
- **uv** - Package manager
- **Container** - Podman for containerization
- **pre-commit** - Pre-commit hooks enabled

#### 2. Code Quality Badges

Shows code quality tools and standards:

```markdown
<!-- code-quality -->
[![ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![ty](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ty/main/assets/badge/v0.json)](https://github.com/astral-sh/ty)[![mypy](https://img.shields.io/badge/type%20checked-mypy-039dfc.svg)](https://mypy-lang.org/)
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![pytest](https://img.shields.io/badge/tested%20with-pytest-46a2f1.svg?logo=pytest)](https://pytest.org/)
[![codecov](https://codecov.io/gh/YourUsername/my-awesome-project/branch/main/graph/badge.svg)](https://codecov.io/gh/YourUsername/my-awesome-project)
```

**Badges:**
- **ruff** - Linter and formatter
- **ty** - Type checker
- **mypy** - Type checker (strict mode)
- **bandit** - Security scanner
- **pytest** - Test framework
- **codecov** - Code coverage tracking

#### 3. Package Info Badges

Shows package metadata:

```markdown
<!-- package-info -->
[![PyPI](https://img.shields.io/pypi/v/my-awesome-project?logo=pypi&logoColor=white)](https://pypi.org/project/my-awesome-project/)
[![Python](https://img.shields.io/badge/python-3.12|3.13|3.14-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/github/license/YourUsername/my-awesome-project)](https://github.com/YourUsername/my-awesome-project/blob/main/LICENSE)
```

**Badges:**
- **PyPI** - Package version on PyPI
- **Python** - Supported Python versions
- **License** - Project license

#### 4. CI/CD Badges

Shows workflow status:

```markdown
<!-- ci/cd -->
[![CI](https://img.shields.io/github/actions/workflow/status/YourUsername/my-awesome-project/health_check.yaml?label=CI&logo=github)](https://github.com/YourUsername/my-awesome-project/actions/workflows/health_check.yaml)
[![CD](https://img.shields.io/github/actions/workflow/status/YourUsername/my-awesome-project/release.yaml?label=CD&logo=github)](https://github.com/YourUsername/my-awesome-project/actions/workflows/release.yaml)
```

**Badges:**
- **CI** - Health check workflow status
- **CD** - Release workflow status

### Description Section

The description from `pyproject.toml` is displayed as a blockquote:

```markdown
---

> Your project description from pyproject.toml

---
```

## Default Configuration

For a project named `my-awesome-project` with description "An awesome Python project":

**File location:** `README.md`

**File contents:**
```markdown
# my-awesome-project

<!-- tooling -->
[![pyrig](https://img.shields.io/badge/built%20with-pyrig-3776AB?logo=buildkite&logoColor=black)](https://github.com/Winipedia/pyrig)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Container](https://img.shields.io/badge/Container-Podman-A23CD6?logo=podman&logoColor=grey&colorA=0D1F3F&colorB=A23CD6)](https://podman.io/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://pre-commit.com/)
<!-- code-quality -->
[![ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![ty](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ty/main/assets/badge/v0.json)](https://github.com/astral-sh/ty)[![mypy](https://img.shields.io/badge/type%20checked-mypy-039dfc.svg)](https://mypy-lang.org/)
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![pytest](https://img.shields.io/badge/tested%20with-pytest-46a2f1.svg?logo=pytest)](https://pytest.org/)
[![codecov](https://codecov.io/gh/YourUsername/my-awesome-project/branch/main/graph/badge.svg)](https://codecov.io/gh/YourUsername/my-awesome-project)
<!-- package-info -->
[![PyPI](https://img.shields.io/pypi/v/my-awesome-project?logo=pypi&logoColor=white)](https://pypi.org/project/my-awesome-project/)
[![Python](https://img.shields.io/badge/python-3.12|3.13|3.14-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/github/license/YourUsername/my-awesome-project)](https://github.com/YourUsername/my-awesome-project/blob/main/LICENSE)
<!-- ci/cd -->
[![CI](https://img.shields.io/github/actions/workflow/status/YourUsername/my-awesome-project/health_check.yaml?label=CI&logo=github)](https://github.com/YourUsername/my-awesome-project/actions/workflows/health_check.yaml)
[![CD](https://img.shields.io/github/actions/workflow/status/YourUsername/my-awesome-project/release.yaml?label=CD&logo=github)](https://github.com/YourUsername/my-awesome-project/actions/workflows/release.yaml)

---

> An awesome Python project

---
```

**You can add your own content below this header.**

## Validation

pyrig validates that `README.md` has the required structure:

### Required Elements

1. **All badges** - All badges must be present
2. **Project description** - Description from `pyproject.toml` must be present
3. **Project name** - Project name must be in the file

### Flexible Validation

pyrig allows you to add content as long as the required elements exist:

```markdown
# my-awesome-project

<!-- badges here -->

---

> An awesome Python project

---

## Installation

```bash
pip install my-awesome-project
```

## Usage

```python
from my_awesome_project import main
main()
```

## Features

- Feature 1
- Feature 2
- Feature 3

## Documentation

See [docs/index.md](docs/index.md) for full documentation.

## Contributing

Contributions welcome! Please read CONTRIBUTING.md first.

## License

MIT License - see LICENSE file for details.
```

## PyPI Integration

The README.md is automatically used as the long description on PyPI:

```toml
# pyproject.toml
[project]
readme = "README.md"
```

When you publish to PyPI, the README content appears on your package page.

**Benefits:**
- **Single source of truth** - One README for GitHub and PyPI
- **Automatic sync** - Changes automatically reflected on PyPI
- **Professional appearance** - Badges and formatting work on PyPI
- **Markdown support** - PyPI renders Markdown correctly

## Badge Information

### Dynamic Badges

Some badges update automatically:

- **PyPI version** - Updates when you publish new versions
- **CI/CD status** - Updates with workflow runs
- **Codecov** - Updates with coverage reports
- **Python versions** - Updates when you change `requires-python`

### Static Badges

Some badges are static indicators:

- **pyrig** - Shows project uses pyrig
- **uv** - Shows project uses uv
- **Container** - Shows project uses Podman
- **pre-commit** - Shows pre-commit is enabled
- **ruff/mypy/bandit/pytest** - Shows tools used

## Customization

You can add content below the auto-generated header:

### Example: Full README

```markdown
# my-awesome-project

<!-- auto-generated badges -->

---

> An awesome Python project

---

## What is my-awesome-project?

my-awesome-project is a Python library that does amazing things.

## Features

- **Fast** - Optimized for performance
- **Simple** - Easy to use API
- **Reliable** - Comprehensive test coverage
- **Well-documented** - Extensive documentation

## Installation

```bash
pip install my-awesome-project
```

## Quick Start

```python
from my_awesome_project import AwesomeClass

# Create an instance
awesome = AwesomeClass()

# Do something awesome
result = awesome.do_something()
print(result)
```

## Documentation

- [Getting Started](docs/getting-started.md)
- [API Reference](docs/api-reference.md)
- [Examples](docs/examples.md)
- [Contributing](CONTRIBUTING.md)

## Requirements

- Python 3.12+
- uv package manager

## Development

```bash
# Clone the repository
git clone https://github.com/YourUsername/my-awesome-project.git
cd my-awesome-project

# Install dependencies
uv sync

# Run tests
uv run pytest

# Run linting
uv run pre-commit run --all-files
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- Built with [pyrig](https://github.com/Winipedia/pyrig)
- Powered by [uv](https://github.com/astral-sh/uv)
```

### Example: Minimal README

```markdown
# my-awesome-project

<!-- auto-generated badges -->

---

> An awesome Python project

---

## Installation

```bash
pip install my-awesome-project
```

## Usage

```python
from my_awesome_project import main
main()
```

See [docs/index.md](docs/index.md) for full documentation.
```

## Related Files

- **`pyproject.toml`** - Contains project description and metadata ([pyproject.md](pyproject.md))
- **`docs/index.md`** - Documentation index ([docs-index.md](docs-index.md))
- **`LICENSE`** - License file ([license-file.md](license-file.md))
- **`.github/workflows/health_check.yaml`** - CI workflow ([health-check-workflow.md](health-check-workflow.md))
- **`.github/workflows/release.yaml`** - CD workflow ([release-workflow.md](release-workflow.md))

## Common Issues

### Issue: Badges not updating

**Symptom:** Badges show old information or errors

**Cause:** Badge URLs may be cached or incorrect

**Solution:**

Badges update automatically, but may be cached:
- **PyPI badge** - Updates within minutes of publishing
- **CI/CD badges** - Update after workflow runs
- **Codecov badge** - Updates after coverage upload

If badges are broken, check:
1. Repository is public (or badges configured for private repos)
2. Workflows have run at least once
3. Package is published to PyPI

### Issue: Want to remove pyrig badge

**Symptom:** Don't want to show "built with pyrig" badge

**Cause:** Badge is auto-generated

**Solution:**

You can remove it manually (pyrig won't re-add it):

```markdown
# my-awesome-project

<!-- tooling -->
<!-- Remove the pyrig badge line -->
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
...
```

Or customize the badge generation:

```python
# my_awesome_project/dev/configs/markdown/readme.py
from pyrig.dev.configs.markdown.readme import ReadmeConfigFile


class CustomReadmeConfigFile(ReadmeConfigFile):
    """Custom README without pyrig badge."""

    @classmethod
    def get_badges(cls) -> dict[str, list[str]]:
        """Get badges without pyrig."""
        badges = super().get_badges()
        # Remove pyrig badge
        badges["tooling"] = [
            b for b in badges["tooling"] if "pyrig" not in b
        ]
        return badges
```

### Issue: Want custom badge categories

**Symptom:** Want different badge organization

**Cause:** Default categories may not fit your needs

**Solution:**

```python
# my_awesome_project/dev/configs/markdown/readme.py
from pyrig.dev.configs.markdown.readme import ReadmeConfigFile


class CustomReadmeConfigFile(ReadmeConfigFile):
    """Custom README with custom badges."""

    @classmethod
    def get_badges(cls) -> dict[str, list[str]]:
        """Get custom badge categories."""
        badges = super().get_badges()

        # Add custom category
        badges["deployment"] = [
            "[![Docker](https://img.shields.io/badge/docker-enabled-blue?logo=docker)](https://docker.com)",
            "[![AWS](https://img.shields.io/badge/AWS-deployed-orange?logo=amazon-aws)](https://aws.amazon.com)",
        ]

        return badges
```

### Issue: Description not updating

**Symptom:** README shows old description

**Cause:** Description is cached from `pyproject.toml`

**Solution:**

```bash
# Update description in pyproject.toml
# Then regenerate README
uv run pyrig mkroot
```

Or update manually in README.md (pyrig won't overwrite if badges are present).

## Best Practices

### ✅ DO

- **Add content below header** - Explain what your project does
- **Include installation instructions** - Make it easy to get started
- **Add usage examples** - Show how to use your project
- **Link to documentation** - Point to detailed docs
- **Keep it concise** - README should be scannable

### ❌ DON'T

- **Don't remove required badges** - They provide valuable information
- **Don't duplicate pyproject.toml** - Use it as single source of truth
- **Don't write a novel** - Keep README focused
- **Don't forget to update** - Keep README current with project
- **Don't hardcode versions** - Let badges show current version

## Advanced Usage

### Custom Badge Styling

```python
# my_awesome_project/dev/configs/markdown/readme.py
from pyrig.dev.configs.markdown.readme import ReadmeConfigFile


class CustomReadmeConfigFile(ReadmeConfigFile):
    """Custom README with styled badges."""

    @classmethod
    def get_badges(cls) -> dict[str, list[str]]:
        """Get badges with custom styling."""
        badges = super().get_badges()

        # Add custom styled badge
        badges["custom"] = [
            "[![Custom](https://img.shields.io/badge/custom-badge-success?style=for-the-badge&logo=github)](https://example.com)",
        ]

        return badges
```

### Conditional Badges

```python
# my_awesome_project/dev/configs/markdown/readme.py
from pyrig.dev.configs.markdown.readme import ReadmeConfigFile
from pyrig.dev.configs.pyproject import PyprojectConfigFile


class CustomReadmeConfigFile(ReadmeConfigFile):
    """Custom README with conditional badges."""

    @classmethod
    def get_badges(cls) -> dict[str, list[str]]:
        """Get badges conditionally."""
        badges = super().get_badges()

        # Only show codecov badge if coverage is configured
        if "codecov" in PyprojectConfigFile.get_dev_dependencies():
            # Badge already included
            pass
        else:
            # Remove codecov badge
            badges["code-quality"] = [
                b for b in badges["code-quality"] if "codecov" not in b
            ]

        return badges
```

## See Also

- [Shields.io](https://shields.io/) - Badge generation service
- [PyPI Documentation](https://packaging.python.org/en/latest/guides/making-a-pypi-friendly-readme/) - PyPI README guide
- [Markdown Guide](https://www.markdownguide.org/) - Markdown syntax
- [pyproject.toml](pyproject.md) - Project configuration
- [docs/index.md](docs-index.md) - Documentation index
- [Getting Started Guide](../getting-started.md) - Initial project setup


