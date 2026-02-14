# ProjectCoverageTester (pytest-cov)

Constructs [Codecov](https://codecov.io/) dashboard URLs and coverage badge
Markdown for your project.

Unlike other Tool wrappers that wrap external CLI tools, ProjectCoverageTester
generates Codecov URLs dynamically from your git remote configuration. It's used
internally by pyrig to populate coverage badge links in README files.

## Subclassing Example

```python
# myapp/rig/tools/project_coverage_tester.py
from pyrig.rig.tools.project_coverage_tester import (
    ProjectCoverageTester as BasePCT,
)

class ProjectCoverageTester(BasePCT):
    @classmethod
    def remote_coverage_url(cls) -> str:
        # Use Coveralls instead of Codecov
        owner, repo = VersionController.I.repo_owner_and_name(
            check_repo_url=False, url_encode=True
        )
        return f"https://coveralls.io/github/{owner}/{repo}"
```

## Related

- [Architecture](architecture.md) - Design philosophy and extension mechanisms
- [Tooling - pytest-cov](../more/tooling.md#pytest-cov) - Why pyrig uses
  pytest-cov
- [Tooling - Codecov](../more/tooling.md#codecov) - Coverage tracking service
- [ProjectTester](project_tester.md) - Test execution wrapper
