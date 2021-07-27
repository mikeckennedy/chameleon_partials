"""
chameleon_partials - Simple reuse of partial HTML page templates in the
Chameleon template language for Python web frameworks.
"""

__version__ = '0.1.0'
__author__ = 'Michael Kennedy <michael@talkpython.fm>'
__all__ = ['register_extensions', 'render_partial', 'PartialsException', 'extend_model', ]

import os
from typing import Optional, Dict, Any
from chameleon import PageTemplateLoader, PageTemplate

has_registered_extensions = False

__templates: Optional[PageTemplateLoader] = None
template_path: Optional[str] = None


class PartialsException(Exception):
    pass


def register_extensions(template_folder: str, auto_reload=False, cache_init=True):
    global has_registered_extensions
    global __templates, template_path

    if has_registered_extensions and cache_init:
        return

    has_registered_extensions = True

    if not template_folder:
        msg = f'The template_folder must be specified.'
        raise PartialsException(msg)

    if not os.path.isdir(template_folder):
        msg = f"The specified template folder must be a folder, it's not: {template_folder}"
        raise PartialsException(msg)

    template_path = template_folder
    __templates = PageTemplateLoader(template_folder, auto_reload=auto_reload)


class HTML:
    def __init__(self, html_text: str):
        self.html_text: str = html_text

    def __html__(self):
        return self.html_text


def render_partial(template_file: str, **template_data: dict) -> HTML:
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
    if model is None:
        model = {}

    if not isinstance(model, dict):
        raise PartialsException("The model must be a dictionary.")

    model['render_partial'] = render_partial
    return model
