"""
chameleon_partials - Simple reuse of partial HTML page templates in the
Chameleon template language for Python web frameworks.
"""

__version__ = '0.1.0'
__author__ = 'Michael Kennedy <michael@talkpython.fm>'
__all__ = ['register_extensions', 'render_partial', 'PartialsException', 'extend_model', ]

import os
from typing import Any, Dict, Optional

from chameleon import PageTemplate, PageTemplateLoader

has_registered_extensions = False

__templates: Optional[PageTemplateLoader] = None
template_path: Optional[str] = None


class PartialsException(Exception):
    """Raised when chameleon_partials is configured or used incorrectly.

    Examples include registering with a missing template folder, rendering a partial
    before calling `register_extensions`, or passing a non-dictionary model to
    `extend_model`.
    """


def register_extensions(template_folder: str, auto_reload: bool = False, cache_init: bool = True):
    """Register chameleon_partials with Chameleon so partials can be rendered.

    Call this once during application startup, before any template is rendered. It builds a
    Chameleon `PageTemplateLoader` rooted at `template_folder` and stores it in module-level
    state that `render_partial` uses to locate templates.

    Args:
        template_folder: Path to the root folder containing your Chameleon templates (with a
            `partials` subfolder by convention). Must be an existing directory.
        auto_reload: When `True`, Chameleon reloads a template from disk whenever the file
            changes. Useful during development; leave `False` in production.
        cache_init: When `True` (the default), calling this again after a previous
            successful registration is a no-op, which makes repeated startup calls safe.
            Pass `False` to force re-registration, for example to point at a different
            template folder in tests.

    Raises:
        PartialsException: If `template_folder` is empty or is not an existing directory.
    """
    global has_registered_extensions
    global __templates, template_path

    if has_registered_extensions and cache_init:
        return

    if not template_folder:
        msg = 'The template_folder must be specified.'
        raise PartialsException(msg)

    if not os.path.isdir(template_folder):
        msg = f"The specified template folder must be a folder, it's not: {template_folder}"
        raise PartialsException(msg)

    template_path = template_folder
    __templates = PageTemplateLoader(template_folder, auto_reload=auto_reload)

    # Mark as registered only after the loader was built successfully, so a call that
    # raised above does not leave the extension flagged as registered (which would turn a
    # later default cache_init=True retry into a silent no-op).
    has_registered_extensions = True


class HTML:
    """A thin wrapper that marks a string as already-rendered, safe HTML.

    `render_partial` returns one of these. Chameleon (and other template engines) call an
    object's `__html__` method when present, so the wrapped markup is inserted verbatim
    instead of being escaped. This type is internal and is not part of the public `__all__`
    API.
    """

    def __init__(self, html_text: str):
        self.html_text: str = html_text

    def __html__(self):
        return self.html_text


def render_partial(template_file: str, **template_data: Any) -> HTML:
    """Render a partial template to an HTML fragment.

    Looks up `template_file` in the folder registered with `register_extensions` and renders
    it with the supplied keyword arguments as its model. `render_partial` is injected into the
    model automatically, so a partial can render further nested partials.

    Args:
        template_file: Path to the partial, relative to the registered templates folder, for
            example `shared/partials/video_image.pt`.
        **template_data: Keyword arguments passed to the template as its model (the variables
            the template can reference).

    Returns:
        An `HTML` wrapper whose `__html__` method yields the rendered markup, so the result is
        treated as safe, pre-escaped HTML when embedded in another template.

    Raises:
        PartialsException: If `register_extensions` has not been called yet.
    """
    if not has_registered_extensions:
        raise PartialsException("You must call register_extensions() before this function can be used.")

    if template_data is None:
        template_data = {}

    if 'render_partial' not in template_data:
        template_data['render_partial'] = render_partial

    page: PageTemplate = __templates[template_file]
    html_source = page.render(encoding='utf-8', **template_data)
    return HTML(html_source)


def extend_model(model: Dict[str, Any]) -> Dict[str, Any]:
    """Add `render_partial` to a view model so templates can call it.

    Use this in frameworks where a view returns a model dictionary (for example FastAPI) and
    you need `render_partial` available inside the template. For Pyramid, prefer the
    `BeforeRender` middleware shown in the README instead.

    Args:
        model: The view model dictionary to extend. `None` is treated as an empty model.

    Returns:
        The same dictionary with a `render_partial` key added (a new dictionary is returned
        when `model` is `None`).

    Raises:
        PartialsException: If `model` is not a dictionary (and not `None`).
    """
    if model is None:
        model = {}

    if not isinstance(model, dict):
        raise PartialsException("The model must be a dictionary.")

    model['render_partial'] = render_partial
    return model
