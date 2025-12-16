# DotExperimentConfigFile

## Overview

**File Location:** `.experiment.py`
**ConfigFile Class:** `DotExperimentConfigFile`
**File Type:** Python
**Priority:** Standard

Creates a scratch Python file at the project root for local experimentation. This file is automatically gitignored, allowing you to test code without risk of accidentally committing it.

## Purpose

The `.experiment.py` file provides a safe experimentation space:

- **Quick Testing** - Test code snippets without creating temporary files
- **Safe Experimentation** - Automatically gitignored, never committed
- **Convenient Location** - At project root for easy access
- **Import Access** - Can import from your project
- **No Cleanup Needed** - Modify freely without worrying about git

### Why pyrig manages this file

pyrig creates `.experiment.py` to:
1. **Encourage experimentation** - Safe place to try things
2. **Prevent accidents** - Automatically gitignored
3. **Standardize workflow** - All pyrig projects have this file
4. **Reduce clutter** - One designated scratch file instead of many
5. **Quick access** - Always at project root

The file is created during `pyrig init` with a minimal docstring. You can write any code you want in it.

## File Location

The file is placed at the project root:

```
my-awesome-project/
├── .experiment.py  # <-- Here (gitignored)
├── .gitignore
├── my_awesome_project/
│   └── __init__.py
└── pyproject.toml
```

## Default Configuration

**File location:** `.experiment.py`

**File contents:**
```python
"""This file is for experimentation and is ignored by git."""
```

**That's it!** Add your experimental code below this docstring.

## Gitignore Integration

The file is automatically added to `.gitignore`:

```gitignore
# pyrig stuff
.git/
.experiment.py  # <-- Automatically ignored
```

**Benefits:**
- **Never committed** - Your experiments stay local
- **No git noise** - Won't show up in `git status`
- **Safe to modify** - Change freely without affecting git
- **Persistent** - File stays on your machine

## Common Use Cases

### 1. Testing Code Snippets

```python
"""This file is for experimentation and is ignored by git."""
from my_awesome_project import AwesomeClass

# Quick test
awesome = AwesomeClass()
result = awesome.do_something()
print(result)
```

### 2. Debugging

```python
"""This file is for experimentation and is ignored by git."""
from my_awesome_project.core import process_data

# Debug a specific case
data = {"key": "value"}
result = process_data(data)
print(f"Result: {result}")
print(f"Type: {type(result)}")
```

### 3. Exploring APIs

```python
"""This file is for experimentation and is ignored by git."""
import requests

# Test API calls
response = requests.get("https://api.example.com/data")
print(response.json())
```

### 4. Prototyping Features

```python
"""This file is for experimentation and is ignored by git."""
from my_awesome_project import AwesomeClass

# Prototype new feature
class EnhancedAwesome(AwesomeClass):
    def new_feature(self):
        """Try out a new feature."""
        return "New feature!"

# Test it
enhanced = EnhancedAwesome()
print(enhanced.new_feature())
```

### 5. Performance Testing

```python
"""This file is for experimentation and is ignored by git."""
import time
from my_awesome_project import process_large_data

# Benchmark performance
start = time.time()
result = process_large_data()
end = time.time()
print(f"Took {end - start:.2f} seconds")
```

### 6. Exploring ConfigFile System

```python
"""This file is for experimentation and is ignored by git."""
from pyrig.dev.configs.base.base import ConfigFile

# List all ConfigFile subclasses
cs = ConfigFile.get_all_subclasses()
cs = sorted(cs, key=lambda c: c.__name__)
for c in cs:
    print(c.__name__)
```

## Running the Experiment File

### Direct Execution

```bash
# Run with Python
python .experiment.py

# Run with uv
uv run python .experiment.py

# Run with uv (shorter)
uv run .experiment.py
```

### From IDE

Most IDEs recognize `.experiment.py` as a Python file:

- **VS Code** - Right-click → "Run Python File in Terminal"
- **PyCharm** - Right-click → "Run '.experiment'"
- **Vim/Neovim** - `:!python %`

### Interactive Mode

```bash
# Start Python REPL with experiment file
python -i .experiment.py

# Or with uv
uv run python -i .experiment.py
```

## Best Practices

### ✅ DO

- **Use for quick tests** - Perfect for one-off experiments
- **Import your project** - Test your code directly
- **Leave it messy** - It's a scratch file
- **Modify freely** - It's gitignored
- **Use for debugging** - Add print statements, breakpoints

### ❌ DON'T

- **Don't commit it** - It's automatically gitignored (good!)
- **Don't put production code here** - Use proper modules
- **Don't rely on it** - It's temporary by nature
- **Don't share it** - Each developer has their own
- **Don't remove from gitignore** - Keep it ignored

## Customization

You can customize the initial content:

```python
# my_awesome_project/dev/configs/python/dot_experiment.py
from pyrig.dev.configs.python.dot_experiment import DotExperimentConfigFile


class CustomDotExperimentConfigFile(DotExperimentConfigFile):
    """Custom experiment file with helpful imports."""

    @classmethod
    def get_content_str(cls) -> str:
        """Get custom experiment file content."""
        return '''"""This file is for experimentation and is ignored by git."""
# Common imports
from my_awesome_project import AwesomeClass
from my_awesome_project.core import process_data
from my_awesome_project.utils import helper_function

# Your experiments here
'''
```

## Related Files

- **`.gitignore`** - Ignores this file ([gitignore.md](gitignore.md))
- **`.env`** - Another gitignored file for secrets ([dotenv.md](dotenv.md))

## Common Issues

### Issue: File shows up in git status

**Symptom:** `.experiment.py` appears in `git status`

**Cause:** File was tracked before being added to `.gitignore`

**Solution:**

```bash
# Remove from git tracking (keeps local file)
git rm --cached .experiment.py

# Commit the removal
git commit -m "Stop tracking .experiment.py"

# Verify it's ignored
git status  # Should not show .experiment.py
```

### Issue: Want to share experiment code

**Symptom:** Need to share code from `.experiment.py`

**Cause:** File is gitignored

**Solution:**

Don't commit `.experiment.py`. Instead:

```bash
# Copy code to a proper module
cp .experiment.py my_awesome_project/new_feature.py

# Or create a new test
cp .experiment.py tests/test_new_feature.py

# Then commit the new file
git add my_awesome_project/new_feature.py
git commit -m "Add new feature"
```

### Issue: Accidentally deleted .experiment.py

**Symptom:** File is missing

**Cause:** Deleted the file

**Solution:**

```bash
# Recreate it
pyrig mkroot

# Or create manually
echo '"""This file is for experimentation and is ignored by git."""' > .experiment.py
```

### Issue: Want multiple experiment files

**Symptom:** One experiment file isn't enough

**Cause:** Working on multiple experiments

**Solution:**

Create additional experiment files:

```bash
# Create more experiment files
touch .experiment2.py
touch .experiment_feature_x.py

# Add to .gitignore
echo ".experiment*.py" >> .gitignore

# Now you have multiple scratch files
```

## Advanced Usage

### Experiment File with Logging

```python
"""This file is for experimentation and is ignored by git."""
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

from my_awesome_project import AwesomeClass

# Experiment with logging
logger.debug("Starting experiment")
awesome = AwesomeClass()
result = awesome.do_something()
logger.info(f"Result: {result}")
```

### Experiment File with Profiling

```python
"""This file is for experimentation and is ignored by git."""
import cProfile
import pstats
from my_awesome_project import expensive_function

# Profile performance
profiler = cProfile.Profile()
profiler.enable()

result = expensive_function()

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)
```

### Experiment File with Type Checking

```python
"""This file is for experimentation and is ignored by git."""
from typing import reveal_type
from my_awesome_project import AwesomeClass

# Check types
awesome = AwesomeClass()
reveal_type(awesome)  # mypy will show the type
result = awesome.do_something()
reveal_type(result)  # mypy will show the type
```

Run with mypy:
```bash
uv run mypy .experiment.py
```

## See Also

- [.gitignore](gitignore.md) - Git ignore patterns
- [.env](dotenv.md) - Environment variables file
- [Python REPL](https://docs.python.org/3/tutorial/interpreter.html) - Interactive Python
- [Getting Started Guide](../getting-started.md) - Initial project setup

