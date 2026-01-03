# VersionController (git)

Type-safe wrapper for [Git](https://git-scm.com/), the version control system.

## Overview

`VersionController` wraps git commands for:

- Repository initialization (`git init`)
- Staging changes (`git add`)
- Committing (`git commit`)
- Remote operations (`git push`)
- Tagging (`git tag`)
- Configuration (`git config`)

## Methods

| Method | Command | Description |
|--------|---------|-------------|
| `get_init_args()` | `git init` | Initialize repository |
| `get_add_args(*files)` | `git add` | Stage files |
| `get_add_all_args()` | `git add .` | Stage all changes |
| `get_add_pyproject_toml_args()` | `git add pyproject.toml` | Stage pyproject.toml |
| `get_add_pyproject_toml_and_uv_lock_args()` | `git add pyproject.toml uv.lock` | Stage both files |
| `get_commit_args(*args)` | `git commit` | Commit changes |
| `get_commit_no_verify_args(msg=...)` | `git commit --no-verify -m` | Commit without hooks |
| `get_push_args()` | `git push` | Push to remote |
| `get_push_origin_args()` | `git push origin` | Push to origin |
| `get_push_origin_tag_args(tag=...)` | `git push origin <tag>` | Push specific tag |
| `get_config_args(*args)` | `git config` | Configure git |
| `get_config_global_args(*args)` | `git config --global` | Global config |
| `get_config_local_args(*args)` | `git config --local` | Local config |
| `get_config_local_user_email_args(email)` | `git config --local user.email` | Set local email |
| `get_config_local_user_name_args(name)` | `git config --local user.name` | Set local name |
| `get_config_global_user_email_args(email)` | `git config --global user.email` | Set global email |
| `get_config_global_user_name_args(name)` | `git config --global user.name` | Set global name |
| `get_tag_args(tag=...)` | `git tag` | Create tag |

## Usage

```python
from pyrig.dev.management.version_controller import VersionController

# Stage and commit
VersionController.L.get_add_all_args().run()
VersionController.L.get_commit_no_verify_args(msg="Update docs").run()

# Push changes
VersionController.L.get_push_args().run()

# Create and push a tag
VersionController.L.get_tag_args(tag="v1.0.0").run()
VersionController.L.get_push_origin_tag_args(tag="v1.0.0").run()

# Configure user
VersionController.L.get_config_local_user_name_args("Bot").run()
VersionController.L.get_config_local_user_email_args("bot@example.com").run()
```

## Subclassing Example

To add GPG signing to commits by default:

```python
# myapp/dev/management/version_controller.py
from pyrig.dev.management.version_controller import VersionController as BaseVC
from pyrig.src.processes import Args

class VersionController(BaseVC):
    @classmethod
    def get_commit_args(cls, *args: str) -> Args:
        # Always sign commits
        return super().get_commit_args("-S", *args)
```

## Related

- [Architecture](architecture.md) - How the Tool system works
