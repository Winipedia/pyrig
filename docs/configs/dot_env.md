# .env Configuration

The `DotEnvConfigFile` manages the `.env` file for local environment variables.

## Overview

Creates a .env file that:
- Stores local environment variables
- Automatically excluded from version control (in `.gitignore`)
- Located at the project root
- User-managed content (pyrig doesn't write to it)
- Loaded using python-dotenv library

## Inheritance

```mermaid
graph TD
    A[ConfigFile] --> B[DotEnvConfigFile]
    
    style A fill:#a8dadc,stroke:#333,stroke-width:2px,color:#000
    style B fill:#f4a261,stroke:#333,stroke-width:2px,color:#000
```

**Inherits from**: `ConfigFile`

**What this means**:
- Direct inheritance from ConfigFile
- Custom `load()` and `dump()` implementations
- Read-only from pyrig's perspective
- Users manage content manually

## File Location

**Path**: `.env` (project root)

**Extension**: `.env` - Environment file.

**Filename**: Empty string to produce `.env` (not `env.env`).

**Special filename handling**: `get_filename()` returns `""` to create a dotfile.

## How It Works

### Automatic Generation

When initialized via `uv run myapp mkroot`, the file is created:

1. **Empty file**: Created if it doesn't exist
2. **Git exclusion**: Automatically added to `.gitignore`
3. **User-managed**: Pyrig doesn't write to this file

### Loading Environment Variables

```python
@classmethod
def load(cls) -> dict[str, str | None]:
    """Load environment variables from the .env file."""
    return dotenv_values(cls.get_path())
```

Uses the `python-dotenv` library to parse the file.

### Dump Protection

```python
@classmethod
def dump(cls, config: dict[str, Any] | list[Any]) -> None:
    """Prevent writing to .env files."""
    if config:
        raise ValueError(f"Cannot dump {config} to .env file.")
```

Pyrig prevents accidental writes to `.env` files.

## Usage

### Automatic Creation

```bash
uv run myapp mkroot
```

### Adding Environment Variables

Manually edit the `.env` file:

```bash
# .env
DATABASE_URL=postgresql://localhost/mydb
API_KEY=your-secret-key
DEBUG=true
```

### Loading in Python

```python
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

# Access variables
database_url = os.getenv("DATABASE_URL")
api_key = os.getenv("API_KEY")
debug = os.getenv("DEBUG", "false").lower() == "true"
```

### Using with pyrig

```python
from pyrig.dev.configs.dot_env import DotEnvConfigFile

# Load all variables
env_vars = DotEnvConfigFile.load()
print(env_vars["DATABASE_URL"])
```

## Validation Logic

The `is_correct()` method checks if the file exists:

```python
@classmethod
def is_correct(cls) -> bool:
    """Check if the .env file exists."""
    return super().is_correct() or cls.get_path().exists()
```

**Required element**: File must exist (can be empty).

## Best Practices

1. **Never commit**: Keep `.env` out of version control
2. **Use .env.example**: Create a template with dummy values
3. **Document variables**: Add comments explaining each variable
4. **Keep secrets safe**: Don't share `.env` files
5. **Use different files**: `.env.local`, `.env.test` for different environments

