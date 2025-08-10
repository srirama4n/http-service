# Documentation Generation Guide

This guide explains how to generate, build, and maintain documentation for the HTTP Service project.

## 📋 Prerequisites

### Required Dependencies

Install the documentation dependencies:

```bash
# Install documentation dependencies
pip install -r requirements-docs.txt

# Or install individually
pip install sphinx sphinx-rtd-theme myst-parser sphinx-autodoc-typehints
```

### Optional Dependencies

For enhanced documentation features:

```bash
# Install all development dependencies (includes docs)
pip install -e .[dev]

# Or install all dependencies
pip install -e .[all]
```

## 🏗️ Documentation Structure

```
docs/
├── conf.py              # Sphinx configuration
├── index.md             # Main documentation page
├── installation.md      # Installation guide
├── quickstart.md        # Quick start guide
├── api_reference.md     # API documentation
├── examples.md          # Usage examples
├── _build/              # Generated documentation (auto-created)
│   └── html/           # HTML output
├── _static/            # Static assets (CSS, JS, images)
└── _templates/         # Custom templates
```

## 🔧 Building Documentation

### Quick Build

```bash
# Navigate to docs directory
cd docs

# Build HTML documentation
sphinx-build -b html . _build/html
```

### Using Makefile

```bash
# From project root
make docs

# Or with specific options
make docs-clean  # Clean build artifacts
make docs-serve  # Build and serve locally
```

### Using Build Script

```bash
# From project root
python build_script.py docs

# Or with specific options
python build_script.py build-docs
```

## 📖 Documentation Formats

### HTML (Default)

```bash
# Build HTML documentation
sphinx-build -b html . _build/html

# View locally
open _build/html/index.html
# or
python -m http.server -d _build/html
```

### PDF

```bash
# Install LaTeX dependencies first
# On macOS: brew install --cask mactex
# On Ubuntu: sudo apt-get install texlive-full

# Build PDF documentation
sphinx-build -b latex . _build/latex
cd _build/latex && make
```

### EPUB

```bash
# Build EPUB documentation
sphinx-build -b epub . _build/epub
```

### Single HTML

```bash
# Build single HTML file
sphinx-build -b singlehtml . _build/singlehtml
```

## 🎨 Customization

### Theme Configuration

Edit `docs/conf.py` to customize the theme:

```python
# Theme options
html_theme_options = {
    'navigation_depth': 4,
    'collapse_navigation': False,
    'sticky_navigation': True,
    'includehidden': True,
    'titles_only': False,
    'github_url': 'https://github.com/srirama4n/http-service',
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': True,
    'style_nav_header_background': '#2980B9',
}
```

### Adding New Pages

1. **Create a new Markdown file**:
   ```bash
   touch docs/new_page.md
   ```

2. **Add content** using Markdown syntax:
   ```markdown
   # New Page Title

   Content goes here...

   ## Section

   More content...
   ```

3. **Add to toctree** in `docs/index.md`:
   ```markdown
   ```{toctree}
   :maxdepth: 2
   :caption: Contents:

   installation
   quickstart
   api_reference
   examples
   new_page
   ```
   ```

### Custom CSS

1. **Create CSS file**:
   ```bash
   mkdir -p docs/_static
   touch docs/_static/custom.css
   ```

2. **Add custom styles**:
   ```css
   /* Custom styles */
   .custom-class {
       color: #2980B9;
   }
   ```

3. **Include in conf.py**:
   ```python
   html_css_files = [
       'custom.css',
   ]
   ```

## 🔍 AutoDoc Configuration

### API Documentation

The documentation automatically generates API docs from docstrings:

```python
# In your Python files, use Google or NumPy style docstrings
def my_function(param1: str, param2: int = 10) -> bool:
    """Short description of function.
    
    Longer description if needed.
    
    Args:
        param1: Description of param1
        param2: Description of param2, defaults to 10
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When param1 is empty
    """
    pass
```

### Type Hints

Type hints are automatically included in documentation:

```python
from typing import Optional, List, Dict, Any

def process_data(data: List[Dict[str, Any]]) -> Optional[str]:
    """Process data with type hints."""
    pass
```

## 🚀 Deployment

### Local Development

```bash
# Build and serve locally
cd docs
sphinx-build -b html . _build/html
python -m http.server -d _build/html 8000

# Open in browser
open http://localhost:8000
```

### GitHub Pages

1. **Enable GitHub Pages** in repository settings
2. **Set source** to `/docs` branch or `/docs` folder
3. **Build and commit** documentation:
   ```bash
   cd docs
   sphinx-build -b html . _build/html
   git add _build/html
   git commit -m "Update documentation"
   git push
   ```

### Read the Docs

1. **Connect repository** to Read the Docs
2. **Configure build settings**:
   - Python version: 3.8+
   - Install method: pip
   - Requirements file: `requirements-docs.txt`
3. **Build automatically** on each commit

### Netlify/Vercel

1. **Deploy from Git** repository
2. **Set build command**:
   ```bash
   cd docs && sphinx-build -b html . _build/html
   ```
3. **Set publish directory**: `docs/_build/html`

## 🧪 Testing Documentation

### Link Checking

```bash
# Check for broken links
sphinx-build -b linkcheck . _build/linkcheck
```

### Spelling Check

```bash
# Install sphinxcontrib-spelling
pip install sphinxcontrib-spelling

# Add to conf.py extensions
extensions = [
    # ... other extensions
    'sphinxcontrib.spelling',
]

# Build with spelling check
sphinx-build -b spelling . _build/spelling
```

### Coverage Report

```bash
# Check documentation coverage
sphinx-build -b coverage . _build/coverage
```

## 🔧 Advanced Configuration

### Intersphinx Mapping

Configure external documentation links in `conf.py`:

```python
intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'httpx': ('https://www.python-httpx.org/', None),
    'pytest': ('https://docs.pytest.org/', None),
}
```

### Custom Extensions

Add custom Sphinx extensions:

```python
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.mathjax',
    'sphinx_rtd_theme',
    'myst_parser',
    'sphinx_autodoc_typehints',
    # Add custom extensions here
]
```

### Build Profiles

Create different build configurations:

```bash
# Development build (faster)
sphinx-build -b html -D html_theme_options.development=true . _build/html

# Production build (optimized)
sphinx-build -b html -D html_theme_options.production=true . _build/html
```

## 📊 Documentation Metrics

### Build Statistics

```bash
# Show build statistics
sphinx-build -b html . _build/html 2>&1 | grep -E "(warning|error|built)"
```

### Coverage Report

```bash
# Generate coverage report
sphinx-build -b coverage . _build/coverage
cat _build/coverage/python.txt
```

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**:
   ```bash
   # Add project root to Python path
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   ```

2. **Missing Dependencies**:
   ```bash
   # Install all documentation dependencies
   pip install -r requirements-docs.txt
   ```

3. **Theme Issues**:
   ```bash
   # Reinstall theme
   pip uninstall sphinx-rtd-theme
   pip install sphinx-rtd-theme
   ```

4. **Build Warnings**:
   ```bash
   # Show all warnings
   sphinx-build -b html -W . _build/html
   ```

### Debug Mode

```bash
# Verbose build output
sphinx-build -b html -v . _build/html

# Debug mode
sphinx-build -b html -vvv . _build/html
```

## 📝 Documentation Standards

### Writing Guidelines

1. **Use Markdown** for all documentation files
2. **Follow Google Style** for docstrings
3. **Include type hints** in all function signatures
4. **Add examples** for all major features
5. **Use consistent formatting** and structure

### File Naming

- Use lowercase with underscores: `api_reference.md`
- Use descriptive names: `installation.md`, `quickstart.md`
- Keep names short but clear

### Content Structure

```markdown
# Page Title

Brief description of the page content.

## Section 1

Content for section 1.

### Subsection 1.1

More detailed content.

## Section 2

Content for section 2.

## Examples

```python
# Code examples
def example_function():
    pass
```

## See Also

- [Related Page](related_page.md)
- [External Link](https://example.com)
```

## 🔄 Continuous Integration

### GitHub Actions

Create `.github/workflows/docs.yml`:

```yaml
name: Build Documentation

on:
  push:
    branches: [ main ]
    paths: [ 'docs/**', 'http_service/**' ]
  pull_request:
    branches: [ main ]

jobs:
  build-docs:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        pip install -r requirements-docs.txt
    - name: Build documentation
      run: |
        cd docs
        sphinx-build -b html . _build/html
    - name: Deploy to GitHub Pages
      if: github.ref == 'refs/heads/main'
      uses: peaceiris/actions-gh-pages@v3
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./docs/_build/html
```

### Pre-commit Hooks

Add to `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
  - repo: local
    hooks:
      - id: docs-build
        name: Build Documentation
        entry: bash -c 'cd docs && sphinx-build -b html . _build/html'
        language: system
        pass_filenames: false
```

## 📚 Additional Resources

### Sphinx Documentation

- [Sphinx User Guide](https://www.sphinx-doc.org/en/master/usage/index.html)
- [Sphinx Configuration](https://www.sphinx-doc.org/en/master/usage/configuration.html)
- [Sphinx Extensions](https://www.sphinx-doc.org/en/master/usage/extensions/index.html)

### MyST Parser

- [MyST Documentation](https://myst-parser.readthedocs.io/)
- [Markdown Syntax](https://myst-parser.readthedocs.io/en/latest/syntax/syntax.html)

### Read the Docs Theme

- [Theme Documentation](https://sphinx-rtd-theme.readthedocs.io/)
- [Theme Configuration](https://sphinx-rtd-theme.readthedocs.io/en/latest/configuring.html)

### Best Practices

- [Documentation Best Practices](https://www.writethedocs.org/guide/)
- [Technical Writing](https://developers.google.com/tech-writing)
- [API Documentation](https://swagger.io/resources/articles/documenting-your-api/)

## 🎯 Quick Reference

### Common Commands

```bash
# Build documentation
cd docs && sphinx-build -b html . _build/html

# Clean build artifacts
rm -rf docs/_build

# Serve locally
python -m http.server -d docs/_build/html 8000

# Check links
sphinx-build -b linkcheck . _build/linkcheck

# Build with warnings
sphinx-build -b html -W . _build/html
```

### File Locations

- **Configuration**: `docs/conf.py`
- **Main Page**: `docs/index.md`
- **Build Output**: `docs/_build/html/`
- **Static Assets**: `docs/_static/`
- **Templates**: `docs/_templates/`

### Environment Variables

```bash
# Set Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Set Sphinx options
export SPHINXOPTS="-W --keep-going"

# Set theme options
export SPHINX_THEME_OPTIONS="development=true"
```

This guide provides everything you need to generate, build, and maintain comprehensive documentation for the HTTP Service project! 🚀
