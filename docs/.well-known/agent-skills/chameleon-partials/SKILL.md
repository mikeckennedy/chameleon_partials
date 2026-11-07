---
name: chameleon-partials
description: >-
  Renders reusable HTML fragments (partials) inside Chameleon templates for any Python web framework that renders Chameleon, such as Pyramid or FastAPI. Use when adding chameleon_partials to an app, calling render_partial from a .pt template or from Python, wiring render_partial into Pyramid (BeforeRender) or another framework (extend_model), testing partials with pytest, or fixing PartialsException, ValueError "Template not found", NameError: render_partial, escaped markup, or template edits that do not show up.
license: MIT
compatibility: Requires Python >=3.10 and Chameleon. Framework-agnostic; the example app uses Pyramid.
---

# chameleon-partials

Chameleon has no built-in way to reuse a fragment of HTML across pages. chameleon_partials adds `render_partial(path, **model)`: a template calls it inside `${ }` to insert a fragment template from a folder registered once at startup, passing keyword arguments as the fragment's model. It returns an `HTML` object, not a `str`, which Chameleon inserts unescaped through `__html__`. Misuse raises `PartialsException`; a missing or refused template raises Chameleon's own `ValueError` (`Template not found: ...`).

## Install

`uv add chameleon-partials` or `pip install chameleon-partials`. The import name is `chameleon_partials`.

## Use

```python
# Application startup, once, before any template renders.
from pathlib import Path
import chameleon_partials

folder = (Path(__file__).parent / 'templates').as_posix()
chameleon_partials.register_extensions(folder, auto_reload=dev_mode)  # auto_reload=False in production
```

```html
<!-- Any page template or partial. The path is relative to the registered folder. -->
<span tal:repeat="v videos">${ render_partial('shared/partials/video_square.pt', video=v) }</span>
```

Pyramid: add a `BeforeRender` subscriber in a package that `config.scan()` covers, and every template gets `render_partial`:

```python
from pyramid.events import BeforeRender, subscriber
import chameleon_partials


@subscriber(BeforeRender)
def add_global(event):
    event['render_partial'] = chameleon_partials.render_partial
```

Other frameworks: `return chameleon_partials.extend_model(model)` from the view. Tests: register the test template folder in a fixture, set `chameleon_partials.has_registered_extensions = False` in its teardown, and assert on `render_partial(...).html_text`.

## Rules

- Partial paths are always relative to the registered folder, never to the calling template, even inside a nested partial. Chameleon's `metal:use-macro="load: ../shared/_layout.pt"` is relative to the current file. Do not mix the two rules.
- `register_extensions` does nothing after one successful call (default `cache_init=True`). To re-point it, pass `cache_init=False` or reset `has_registered_extensions`. A call that raised did not register, so fix the folder and call again.
- Registration is module-global and not lock-guarded: call it from startup code, not from request handlers. Rendering after registration is safe from several threads.
- `PartialsException` means misuse only: rendering before registration, an empty or missing folder, or a non-dict model. Chameleon's errors pass through unwrapped: a missing template is `ValueError`, a missing model variable is `NameError`.
- A name that leaves the folder (an absolute path, a `..` out of it, a `package:path` spec) or names a folder is refused as `ValueError: Template not found`. The check is lexical, so a symlink inside the folder is followed. Never build the path from request data; map request values to names you wrote.
- `render_partial` is injected into the model only when the key is absent, so `render_partial(name, **request.params)` lets a request replace it. Pass named keyword arguments.
- Do not name a model value `encoding` (the package passes it to Chameleon; yours raises `TypeError`). `translate`, `target_language`, and `repeat` belong to Chameleon.
- Pass the returned `HTML` object into templates. Read `.html_text` only for a response body or an assertion; a plain `str` is escaped on insertion.
- Names are normalized (`./`, `//`, a `..` that stays inside, surrounding whitespace), so each file compiles once. A different case spelling on macOS or Windows still loads but is a separate cached template.
- With `auto_reload=True` a changed file recompiles on the next render; with the default `False`, template edits need a process restart.
- A partial that renders itself without a stopping condition raises `RecursionError`.
- Templates are TAL and METAL, not Jinja: `${ expr }`, `tal:repeat`, `tal:condition`, `tal:define`. There is no `{% %}` or `{{ }}`.

## Decision table

| Need | Use |
|------|-----|
| Insert a fragment in a template | `${ render_partial('shared/partials/x.pt', key=value) }` |
| Give every Pyramid template `render_partial` | `BeforeRender` subscriber setting `event['render_partial']` |
| Give a template `render_partial` in another framework | `return chameleon_partials.extend_model(model)` |
| Fragment as a string (HTMX response, email, test) | `render_partial(path, **model).html_text` |
| See template edits without a restart | `register_extensions(folder, auto_reload=True)` |
| Register a different folder in the same process | `register_extensions(folder, cache_init=False)` or reset `has_registered_extensions` |
| Let a request choose the fragment | `PARTIALS = {'card': 'shared/partials/card.pt'}` then `render_partial(PARTIALS[key], ...)` |

## API

- `register_extensions(template_folder: str, auto_reload: bool = False, cache_init: bool = True) -> None`: raises `PartialsException` for an empty or non-directory folder. Call once at startup.
- `render_partial(template_file: str, **template_data) -> HTML`: raises `PartialsException` before registration and `ValueError` for a missing, folder, or refused name; Chameleon's render errors propagate. Injects itself into the model when absent.
- `extend_model(model: dict | None) -> dict`: sets `model['render_partial']` (replacing any existing key) and returns the same dict; `None` gives a new dict; a non-dict raises `PartialsException`.
- `PartialsException(Exception)`: misconfiguration or misuse only.
- `HTML` (not in `__all__`): `html_text` holds the markup and `__html__()` returns it.

## Example output

```text
>>> render_partial('shared/partials/video_square.pt', video=v).html_text
'<div>\n    <a href="https://www.youtube.com/watch?v=abc123" target="_blank">\n        <img src="https://img.youtube.com/vi/abc123/maxresdefault.jpg"\n     class="img img-responsive "\n     alt="Talk Python"\n     title="Talk Python">\n    </a>\n    ...\n    <div class="views">12,345 views</div>\n</div>'
# The <img> came from the nested video_image.pt partial, inserted unescaped by video_square.pt.
>>> render_partial('shared/partials/missing.pt')
ValueError: Template not found: shared/partials/missing.pt.
>>> render_partial('x.pt')  # before register_extensions
PartialsException: You must call register_extensions() before this function can be used.
```

When a render fails, fix in this order: register the folder, get `render_partial` into the model, make the path relative to the registered folder, then supply every name the partial uses.

## Resources

- [Documentation](https://mkennedy.codes/docs/chameleon-partials/) (every page has a Markdown twin: swap `.html` for `.md`)
- [Getting started](https://mkennedy.codes/docs/chameleon-partials/user-guide/getting-started.html), [Writing partials](https://mkennedy.codes/docs/chameleon-partials/user-guide/writing-partials.html), [Testing](https://mkennedy.codes/docs/chameleon-partials/user-guide/testing.html), [Troubleshooting](https://mkennedy.codes/docs/chameleon-partials/user-guide/troubleshooting.html)
- [API reference](https://mkennedy.codes/docs/chameleon-partials/reference/), [llms.txt](https://mkennedy.codes/docs/chameleon-partials/llms.txt), [llms-full.txt](https://mkennedy.codes/docs/chameleon-partials/llms-full.txt)
- [Source](https://github.com/mikeckennedy/chameleon_partials) and the [example Pyramid app](https://github.com/mikeckennedy/chameleon_partials/tree/main/example)
