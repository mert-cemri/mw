# AgentDash Library Publishing Instructions

This document provides step-by-step instructions for publishing the AgentDash library to PyPI so users can install it with `pip install agentdash`.

## 📦 Package Structure

The AgentDash library has been created with the following structure:

```
mw/
├── agentdash/                     # Main library package
│   ├── __init__.py               # Package initialization & exports  
│   ├── annotator.py              # Main annotator class
│   └── taxonomy.py               # MAST taxonomy definitions
├── setup.py                      # Legacy setup configuration
├── pyproject.toml                # Modern Python packaging config
├── MANIFEST.in                   # File inclusion rules
├── agentdash-requirements.txt    # Library dependencies
├── README-agentdash.md           # Library documentation
└── PUBLISH_INSTRUCTIONS.md       # This file
```

## 🎯 API Design

The library provides the exact API you requested:

```python
from agentdash import annotator

openai_api_key = "your-openai-api-key"
Annotator = annotator(openai_api_key)

trace = "Agent1: Hello... Agent2: Hi..."
annotation = Annotator.produce_taxonomy(trace)

print(annotation['failure_modes'])  # {'1.1': 0, '1.2': 1, ...}
print(annotation['summary'])        # "Brief description of issues"
print(annotation['task_completion']) # True/False
```

## 🚀 Publishing Steps

### 1. Prerequisites

Install required tools:
```bash
pip install build twine
```

### 2. Prepare for Publishing

1. **Create PyPI Account**: 
   - Go to https://pypi.org and create an account
   - Verify your email address
   - (Optional) Set up 2FA for security

2. **Check Package Name**:
   - Search PyPI to ensure "agentdash" is available
   - If taken, consider alternatives like "agentdash-mast", "agentdash-taxonomy", etc.
   - Update package name in `pyproject.toml` and `setup.py` if needed

3. **Update Package Info**:
   - Replace placeholder URLs in `pyproject.toml` with actual repository URLs
   - Update author email and contact information
   - Ensure all dependencies are correct

### 3. Build the Package

From the `mw/` directory:

```bash
# Clean any previous builds
rm -rf build/ dist/ *.egg-info/

# Build the package
python -m build
```

This creates:
- `dist/agentdash-0.1.0.tar.gz` (source distribution)
- `dist/agentdash-0.1.0-py3-none-any.whl` (wheel distribution)

### 4. Test the Package Locally

Install and test locally before publishing:

```bash
# Install from local build
pip install dist/agentdash-0.1.0-py3-none-any.whl

# Test the installation
python -c "from agentdash import annotator; print('✅ AgentDash imported successfully')"

# Uninstall after testing
pip uninstall agentdash
```

### 5. Upload to Test PyPI (Recommended)

Test on PyPI's test server first:

```bash
# Upload to test PyPI
twine upload --repository testpypi dist/*

# Install from test PyPI to verify
pip install --index-url https://test.pypi.org/simple/ agentdash

# Test and then uninstall
pip uninstall agentdash
```

### 6. Upload to Production PyPI

Once everything works on test PyPI:

```bash
# Upload to production PyPI
twine upload dist/*
```

You'll be prompted for your PyPI username and password.

### 7. Verify Installation

After publishing, test the installation:

```bash
# Install from PyPI
pip install agentdash

# Test basic functionality
python -c "
from agentdash import annotator
print('✅ AgentDash library installed successfully')
print('📊 Taxonomy has', len(annotator('test').list_failure_modes()), 'failure modes')
"
```

## 🔧 Alternative Publishing Methods

### Using API Tokens (Recommended)

1. Generate API token on PyPI (Account Settings → API tokens)
2. Create `~/.pypirc`:

```ini
[pypi]
username = __token__
password = pypi-your-api-token-here
```

3. Upload with: `twine upload dist/*`

### Using GitHub Actions (Advanced)

Set up automated publishing on GitHub releases:

```yaml
# .github/workflows/publish.yml
name: Publish to PyPI
on:
  release:
    types: [published]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: '3.x'
    - run: pip install build twine
    - run: python -m build
    - run: twine upload dist/*
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
```

## 📝 Post-Publishing Tasks

After successful publishing:

1. **Update Documentation**:
   - Add installation instructions to project README
   - Create usage examples and tutorials
   - Set up documentation website (optional)

2. **Version Management**:
   - Tag the release in Git: `git tag v0.1.0`
   - Plan versioning strategy for future releases
   - Consider semantic versioning (major.minor.patch)

3. **Community**:
   - Announce on relevant forums/social media
   - Create GitHub repository with source code
   - Set up issue tracking for bug reports

## 🐛 Troubleshooting

### Common Issues:

1. **Package name already exists**:
   - Choose alternative name: `agentdash-mast`, `agentdash-taxonomy`, etc.
   - Update `pyproject.toml` and `setup.py`

2. **Import errors after installation**:
   - Check `__init__.py` exports
   - Verify package structure with `python -c "import agentdash; print(agentdash.__file__)"`

3. **Missing dependencies**:
   - Ensure `openai>=1.0.0` is listed in requirements
   - Test with fresh virtual environment

4. **Authentication errors**:
   - Verify PyPI credentials
   - Use API tokens instead of username/password
   - Check network/firewall restrictions

## 🎉 Success!

Once published, users can install and use your library:

```bash
pip install agentdash
```

```python
from agentdash import annotator

openai_api_key = "sk-your-key"
Annotator = annotator(openai_api_key)

trace = "Agent1: Let's solve this problem..."
annotation = Annotator.produce_taxonomy(trace)

print(f"Detected {annotation['total_failures']} failure modes")
for mode, detected in annotation['failure_modes'].items():
    if detected:
        info = Annotator.get_failure_mode_info(mode)
        print(f"- {mode}: {info['name']}")
```

## 📞 Support

For publishing help:
- PyPI Help: https://pypi.org/help/
- Packaging Guide: https://packaging.python.org/
- Twine Docs: https://twine.readthedocs.io/

The AgentDash library is ready for the world! 🌟