# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Development Commands

### Environment Setup
```bash
# Install dependencies for development
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install package in development mode
pip install -e .
```

### Testing
```bash
# Run all tests
python3 -m pytest tests/

# Run specific test
python3 -m pytest tests/test_rendering.py::test_render_empty

# Run tests with verbose output
python3 -m pytest tests/ -v
```

### Code Quality
```bash
# Check code style and issues
ruff check .

# Auto-fix code style issues
ruff check . --fix

# Format code
ruff format .
```

### Example Application
```bash
# Navigate to example directory
cd example/

# Install example dependencies
pip install -e .

# Run example application (requires additional setup)
# See example/README for full setup instructions
```

## Architecture Overview

### Core Library Structure
- **`chameleon_partials/__init__.py`**: Single-module library containing all functionality
- **Main Components**:
  - `register_extensions()`: Initializes template loader with folder path
  - `render_partial()`: Core function to render partial templates with data
  - `extend_model()`: Helper to inject `render_partial` into view model dictionaries
  - `HTML` class: Wrapper for rendered HTML with `__html__()` method
  - `PartialsException`: Custom exception for library errors

### Integration Patterns
The library supports two primary integration approaches:

1. **Pyramid Framework**: Uses middleware pattern via `BeforeRender` event subscriber
2. **Other Frameworks**: Manual model extension using `extend_model()`

### Template Resolution
- Templates are loaded via Chameleon's `PageTemplateLoader`
- Template paths are relative to registered folder
- Supports nested partials (partials can call other partials)
- Auto-reload capability for development

## Usage Patterns

### Basic Registration and Usage
```python
import chameleon_partials
from pathlib import Path

# One-time registration (typically in app startup)
folder = (Path(__file__).parent / "templates").as_posix()
chameleon_partials.register_extensions(folder, auto_reload=True, cache_init=True)

# In templates, use render_partial function
# ${render_partial('shared/partials/video_image.pt', video=video, classes=[])}
```

### Pyramid Integration (Recommended)
```python
# views/partials_middleware.py
from pyramid.events import subscriber, BeforeRender
import chameleon_partials

@subscriber(BeforeRender)
def add_global(event):
    event['render_partial'] = chameleon_partials.render_partial
```

### Manual Model Extension
```python
# For non-Pyramid frameworks
@view_config(route_name='listing')
def listing(request):
    videos = video_service.all_videos()
    model = dict(videos=videos)
    return chameleon_partials.extend_model(model)  # Injects render_partial
```

### Nested Partials Example
Partials can render other partials recursively:
```html
<!-- video_square.pt -->
<div>
    <a href="https://www.youtube.com/watch?v=${video.id}">
        ${render_partial('shared/partials/video_image.pt', video=video, classes=[])}
    </a>
    <div class="views">${"{:,}".format(video.views)} views</div>
</div>
```

## Development Workflow

### Code Style
- Uses Ruff for linting and formatting with configuration in `ruff.toml`
- Line length: 120 characters
- Single quotes preferred
- Python 3.13 target version

### Testing Strategy
- Tests located in `tests/` directory
- Uses pytest with pytest-clarity for enhanced output
- Test fixtures handle template registration/cleanup
- Tests cover rendering with data, layouts, recursion, and error cases

### Repository Structure
- `/chameleon_partials/`: Core library code (single module)
- `/tests/`: Unit tests with test templates
- `/example/`: Complete Pyramid demo application
- `/readme_resources/`: Documentation assets

### Key Development Notes
- Template registration is global state - tests must clean up properly
- The library requires Chameleon templates (`.pt` files)  
- Example application demonstrates real-world usage patterns
- Auto-reload should be enabled during development for template changes