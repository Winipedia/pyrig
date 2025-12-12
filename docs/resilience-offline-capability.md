# Network Resilience and Offline Capability

This document describes pyrig's network resilience system, which enables project initialization and operation even when external services are unavailable or when working offline.

## Overview

pyrig fetches certain resources from the internet during initialization:
- GitHub's standard Python `.gitignore` template
- MIT license text from GitHub's SPDX API
- Latest stable Python version from endoflife.date API

To ensure reliability, pyrig implements a **resource fallback system** that gracefully handles network failures by falling back to cached local resources.

## Architecture

### Decorator-Based Retry System

The resilience system is built on the `tenacity` library and provides decorators that wrap network-dependent functions:

```python
from pyrig.src.decorators import return_resource_content_on_fetch_error

@return_resource_content_on_fetch_error(resource_name="GITIGNORE")
def get_github_python_gitignore_as_str(cls) -> str:
    """Fetch GitHub's standard Python gitignore patterns.
    
    Falls back to local resource file if fetch fails.
    """
    url = "https://raw.githubusercontent.com/github/gitignore/main/Python.gitignore"
    res = requests.get(url, timeout=10)
    res.raise_for_status()
    return res.text
```

### How It Works

1. **Normal operation**: Function executes and fetches remote resource
2. **Network failure**: Decorator catches `RequestException` (timeout, connection error, HTTP error)
3. **Fallback**: Returns content from local resource file in `pyrig/resources/`
4. **Auto-update**: When running in pyrig itself, successful fetches update the resource files

### Decorator Functions

#### `return_resource_file_content_on_exceptions`

Generic decorator that catches specified exceptions and returns resource file content:

```python
def return_resource_file_content_on_exceptions(
    resource_name: str,
    exceptions: tuple[type[Exception], ...],
    *,
    overwrite_resource: bool = True,
    **tenacity_kwargs: Any,
) -> Callable[[Callable[P, str]], Callable[P, str]]:
    """Return content of a resource file if func raises specific exceptions.
    
    Args:
        resource_name: Name of the resource file (without extension)
        exceptions: Tuple of exception types to catch
        overwrite_resource: If True, update resource file with fresh content
        **tenacity_kwargs: Additional arguments for tenacity retry decorator
    
    Returns:
        Decorated function that falls back to resource file on exception
    """
```

#### `return_resource_content_on_fetch_error`

Specialized decorator for handling network request failures:

```python
def return_resource_content_on_fetch_error(
    resource_name: str,
) -> Callable[[Callable[P, str]], Callable[P, str]]:
    """Return content of a resource file if func raises a requests.HTTPError.
    
    This is a convenience wrapper around return_resource_file_content_on_exceptions
    that specifically handles RequestException (includes HTTPError, ConnectionError,
    Timeout, etc.).
    
    Args:
        resource_name: Name of the resource file (without extension)
    
    Returns:
        Decorated function that falls back to resource file on network error
    """
```

## Resource Files

Pyrig maintains cached versions of external resources in `pyrig/resources/`:

| Resource File | Purpose | Source URL |
|---------------|---------|------------|
| `GITIGNORE` | GitHub's standard Python .gitignore template | `https://raw.githubusercontent.com/github/gitignore/main/Python.gitignore` |
| `MIT_LICENSE_TEMPLATE` | MIT license template with `[year]` and `[fullname]` placeholders | `https://api.github.com/licenses/mit` |
| `LATEST_PYTHON_VERSION` | Latest stable Python version (e.g., "3.14.2") | `https://endoflife.date/api/python.json` |

### Resource File Format

Resource files are plain text files without extensions, stored in `pyrig/resources/`:

```
pyrig/
└── resources/
    ├── __init__.py
    ├── GITIGNORE
    ├── MIT_LICENSE_TEMPLATE
    └── LATEST_PYTHON_VERSION
```

### Auto-Update Mechanism

When running in pyrig's own development environment (detected via `get_pkg_name_from_cwd() == pyrig.__name__`), successful network fetches automatically update the resource files:

```python
@wraps(func)
def wrapper(*args: P.args, **kwargs: P.kwargs) -> str:
    result = decorated_func(*args, **kwargs).strip()
    if (
        get_pkg_name_from_cwd() == pyrig.__name__
        and overwrite_resource
        and result != content
    ):
        resource_path.write_text(result, encoding="utf-8")
        git_add_file(resource_path)  # Stage the updated resource
    return result
```

This ensures:
- Resource files stay up-to-date when pyrig developers run tests
- Changes are automatically staged for commit
- Dependent packages use stable cached versions

## Usage Examples

### GitIgnore Configuration

<augment_code_snippet path="pyrig/dev/configs/git/gitignore.py" mode="EXCERPT">
````python
@classmethod
@return_resource_content_on_fetch_error(resource_name="GITIGNORE")
def get_github_python_gitignore_as_str(cls) -> str:
    """Fetch GitHub's standard Python gitignore patterns."""
    url = "https://raw.githubusercontent.com/github/gitignore/main/Python.gitignore"
    res = requests.get(url, timeout=10)
    res.raise_for_status()
    return res.text
````
</augment_code_snippet>

## Benefits

### 1. Offline Capability

Projects can be initialized and configured without internet access:

```bash
# Works even without internet connection
uv run pyrig init
```

The system falls back to cached resources, ensuring:
- `.gitignore` is created with standard Python patterns
- `LICENSE` is created with MIT license template
- Python version constraints use the last known stable version

### 2. Resilience to Service Outages

External services being unavailable won't break pyrig:

- GitHub API rate limits → Uses cached license template
- GitHub raw content unavailable → Uses cached .gitignore
- endoflife.date API down → Uses cached Python version

### 3. Consistent Behavior

Resource files provide predictable fallback behavior:

- Same .gitignore patterns across all environments
- Same license template regardless of API availability
- Deterministic Python version when API is unreachable

### 4. Always Up-to-Date

When online, pyrig automatically updates its resource files:

- Developers running tests fetch latest versions
- Updated resources are staged for commit
- Next release includes refreshed fallback data

## Testing

The resilience system is tested to ensure proper fallback behavior:

<augment_code_snippet path="tests/test_pyrig/test_src/test_decorators.py" mode="EXCERPT">
````python
def test_return_resource_content_on_fetch_error(
    tmp_path: Path, mocker: MockFixture
) -> None:
    """Test function."""
    resource_path = tmp_path / "test_resource.txt"
    mocker.patch(
        decorators.__name__ + "." + get_resource_path.__name__,
        return_value=resource_path,
    )
    resource_path.write_text("Hello World!")

    @return_resource_content_on_fetch_error("test_resource.txt")
    def test_func() -> str:
        raise RequestException("Test exception")

    # Function should return resource content instead of raising
    assert test_func() == "Hello World!"
````
</augment_code_snippet>

## Implementation Details

### Tenacity Integration

The decorator system uses `tenacity` for retry logic:

```python
from tenacity import retry, retry_if_exception_type, stop_after_attempt

tenacity_decorator = retry(
    retry=retry_if_exception_type(exception_types=exceptions),
    stop=stop_after_attempt(max_attempt_number=1),  # No retries, just catch once
    retry_error_callback=lambda _state: content,     # Return resource content
    reraise=False,                                   # Don't re-raise exception
    **tenacity_kwargs,
)
```

Key configuration:
- **No retries**: `stop_after_attempt(1)` means catch exception once, don't retry
- **Fallback callback**: `retry_error_callback` returns resource file content
- **No re-raise**: `reraise=False` prevents exception from propagating

### Resource Path Resolution

Resources are located using the `get_resource_path` utility:

```python
from pyrig.src.resource import get_resource_path
from pyrig import resources

resource_path = get_resource_path(resource_name, resources)
content = resource_path.read_text(encoding="utf-8").strip()
```

This ensures resources are found regardless of how pyrig is installed (editable, wheel, etc.).

## Creating Custom Resilient Functions

You can use the decorator system for your own network-dependent functions:

### Step 1: Create a Resource File

```bash
# Create resource file in your package
echo "Default content" > your_project/resources/MY_RESOURCE
```

### Step 2: Decorate Your Function

```python
from pyrig.src.decorators import return_resource_content_on_fetch_error

@return_resource_content_on_fetch_error(resource_name="MY_RESOURCE")
def fetch_my_data() -> str:
    """Fetch data from external API with fallback."""
    response = requests.get("https://api.example.com/data", timeout=10)
    response.raise_for_status()
    return response.text
```

### Step 3: Use the Function

```python
# Works online (fetches from API)
data = fetch_my_data()

# Works offline (uses resource file)
data = fetch_my_data()  # Returns content from MY_RESOURCE
```

## Troubleshooting

### Resource File Not Found

**Error:**
```
FileNotFoundError: Resource 'GITIGNORE' not found
```

**Cause:** Resource file is missing from `pyrig/resources/`

**Solution:**
1. Ensure pyrig is properly installed: `uv sync`
2. Check that resource files exist in the installation
3. Reinstall pyrig if necessary: `uv sync --reinstall`

### Stale Resource Content

**Symptom:** Resource file contains outdated content

**Solution:**
1. Run tests in pyrig's development environment to trigger auto-update
2. Or manually update the resource file with fresh content
3. Commit the updated resource file

### Network Timeout

**Symptom:** Function takes long time before falling back

**Solution:**
Adjust timeout in the fetch function:

```python
# Reduce timeout for faster fallback
res = requests.get(url, timeout=5)  # 5 seconds instead of 10
```

## Summary

| Feature | Benefit |
|---------|---------|
| **Decorator-based** | Clean, reusable pattern for network resilience |
| **Automatic fallback** | No manual error handling needed |
| **Resource caching** | Offline capability out of the box |
| **Auto-update** | Resources stay current when online |
| **Tenacity integration** | Robust retry and error handling |
| **Git integration** | Updated resources automatically staged |

The resilience system ensures pyrig works reliably in all network conditions, from offline development to CI/CD environments with rate limits or service outages.

### License Configuration

<augment_code_snippet path="pyrig/dev/configs/licence.py" mode="EXCERPT">
````python
@classmethod
@return_resource_content_on_fetch_error(resource_name="MIT_LICENSE_TEMPLATE")
def get_mit_license(cls) -> str:
    """Get the MIT license text."""
    url = "https://api.github.com/licenses/mit"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    return data["body"]
````
</augment_code_snippet>

### Python Version Fetching

<augment_code_snippet path="pyrig/dev/configs/pyproject.py" mode="EXCERPT">
````python
@classmethod
@return_resource_content_on_fetch_error(resource_name="LATEST_PYTHON_VERSION")
@cache
def fetch_latest_python_version(cls) -> str:
    """Fetch the latest stable Python version from endoflife.date."""
    url = "https://endoflife.date/api/python.json"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    return data[0]["latest"]
````
</augment_code_snippet>

