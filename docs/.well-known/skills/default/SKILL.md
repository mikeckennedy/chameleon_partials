---
name: chameleon-partials
description: >
  Simple reuse of partial HTML page templates in the Chameleon template language for Python web frameworks. Use when writing Python code that uses the chameleon_partials package.
license: MIT
compatibility: Requires Python >=3.9.
---

# Chameleon Partials

Simple reuse of partial HTML page templates in the Chameleon template language for Python web frameworks.

## Installation

```bash
pip install chameleon-partials
```

## API overview

### Setup

Register chameleon_partials with Chameleon. Call this once at application startup.

- `register_extensions`: Register chameleon_partials with Chameleon so partials can be rendered

### Rendering partials

Render partial templates and expose render_partial to your view models.

- `render_partial`: Render a partial template to an HTML fragment
- `extend_model`: Add `render_partial` to a view model so templates can call it

### Exceptions

Errors raised by the library.

- `PartialsException`: Raised when chameleon_partials is configured or used incorrectly

## End-to-end wiring

Register the template folder once at startup, then call `render_partial(...)` from inside any Chameleon template. Template paths are always relative to the registered folder — even when called from inside another partial.

```python
# At application startup, before any template renders
from pathlib import Path
import chameleon_partials

folder = (Path(__file__).parent / 'templates').as_posix()
chameleon_partials.register_extensions(folder, auto_reload=True)  # auto_reload for dev only
```

```html
<!-- templates/shared/partials/greeting.pt (a partial is a bare HTML fragment) -->
<div class="greeting">
    <h2>Hello, ${ name }!</h2>
</div>
```

```html
<!-- Any page template: inline the fragment, passing its model as keyword arguments -->
${ render_partial('shared/partials/greeting.pt', name='Michael') }
```

The template needs `render_partial` in its model. Pyramid apps wire it globally with a `BeforeRender` subscriber; other frameworks (FastAPI, plain WSGI, ...) call `extend_model(model)` on the view-model dict before rendering:

```python
# Pyramid: discovered by config.scan(); every template gets render_partial automatically
from pyramid.events import subscriber, BeforeRender
import chameleon_partials

@subscriber(BeforeRender)
def add_global(event):
    event['render_partial'] = chameleon_partials.render_partial
```

```python
# Any other framework: extend the view model per view
model = dict(name='Michael')
return chameleon_partials.extend_model(model)
```

Inside a partial, `render_partial` is injected into the model automatically, so partials can nest further partials with no extra wiring — nesting depth is unlimited.

## Chameleon template syntax (this is TAL, not Jinja)

Chameleon templates are valid HTML/XML where directives live in `tal:` and `metal:` attributes. There is no `{% ... %}` or `{{ ... }}` — do not use Jinja/Django syntax. Interpolation uses `${ ... }` and may contain arbitrary Python expressions.

```html
<h1>${ video.title }</h1>
<div class="views">${ "{:,}".format(video.views) } views</div>

<!-- Loop: render a partial per item -->
<div class="video" tal:repeat="v videos">
    ${ render_partial('shared/partials/video_square.pt', video=v) }
</div>

<!-- Condition (element omitted entirely when falsy) -->
<img tal:condition="show_avatar" src="${ user.avatar_url }" />
```

## Shared layouts with METAL macros

Partials compose with Chameleon's METAL layout inheritance — pages fill a layout's slot and call partials inside it:

```html
<!-- templates/shared/_layout.pt -->
<!DOCTYPE html metal:define-macro="layout">
<html lang="en">
<body>
    <div metal:define-slot="content">No content</div>
</body>
</html>
```

```html
<!-- templates/home/index.pt -->
<div metal:use-macro="load: ../shared/_layout.pt">
    <div metal:fill-slot="content">
        <div tal:repeat="v videos">
            ${ render_partial('shared/partials/video_square.pt', video=v) }
        </div>
    </div>
</div>
```

Note the asymmetry: `metal:use-macro="load: ..."` paths are relative to the *current template file*, while `render_partial(...)` paths are always relative to the *registered template folder*.

## Project layout conventions

```
your_app/
├── __init__.py                    # register_extensions() here, at startup
├── views/
│   └── partials_middleware.py     # BeforeRender subscriber (Pyramid)
└── templates/                     # the registered folder
    ├── home/index.pt              # page templates
    └── shared/
        ├── _layout.pt             # METAL layout (underscore prefix by convention)
        └── partials/              # reusable fragments live here
            └── video_square.pt
```

## Registration semantics & testing

Registration is process-wide module state. With the default `cache_init=True`, calling `register_extensions()` again after a previous successful registration is a silent no-op — safe for repeated startup calls, but a test pointing at a different folder must pass `cache_init=False` or reset the flag. A registration that *raised* does not mark the module as registered (since 0.2.0), so it can simply be retried.

```python
@pytest.fixture
def registered_extension():
    folder = (Path(__file__).parent / 'test_templates').as_posix()
    chameleon_partials.register_extensions(folder, auto_reload=True)
    yield
    chameleon_partials.has_registered_extensions = False  # reset for the next test
```

`render_partial` returns an `HTML` wrapper (its `__html__()` makes engines insert the markup unescaped); in tests or HTMX/email code, read the raw string from `.html_text`.

## Error contract

`PartialsException` covers misuse and misconfiguration only: rendering before `register_extensions()`, an empty or non-directory template folder, or a non-dict model to `extend_model()`. Chameleon's own errors propagate unwrapped — a missing template file raises Chameleon's `ValueError`, not `PartialsException`.

## Fetching these docs as Markdown

Every page on the documentation site has a plain-Markdown twin: swap the `.html` extension for `.md` to get token-efficient source without the site chrome. For example https://mkennedy.codes/docs/chameleon-partials/reference/render_partial.html is also available at https://mkennedy.codes/docs/chameleon-partials/reference/render_partial.md. Prefer the `.md` form when reading these docs programmatically.


## Resources

- [Full documentation](https://mkennedy.codes/docs/chameleon-partials/)
- [llms.txt](llms.txt) — Indexed API reference for LLMs
- [llms-full.txt](llms-full.txt) — Comprehensive documentation for LLMs
- [Source code](https://github.com/mikeckennedy/chameleon_partials)
