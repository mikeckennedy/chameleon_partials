# Getting started

This page takes you from an empty project to a rendered fragment. It assumes a web framework that already renders Chameleon templates, such as Pyramid with `pyramid_chameleon`, or FastAPI with Chameleon called directly.


# Install

``` bash
uv add chameleon-partials
# or
pip install chameleon-partials
```

The distribution name on PyPI is `chameleon-partials` with a hyphen. The import name is `chameleon_partials` with an underscore. The only runtime dependency is Chameleon.


# Register the template folder once

Call [register_extensions](../reference/register_extensions.md#chameleon_partials.register_extensions) once at application startup, before any template renders. It takes the root folder of your Chameleon templates. Every partial is later named by its path relative to this folder.

``` python
from pathlib import Path

import chameleon_partials

folder = (Path(__file__).parent / 'templates').as_posix()
chameleon_partials.register_extensions(folder, auto_reload=True)
```

Build the folder path from `__file__` so it does not depend on the working directory. Set `auto_reload=True` while developing so edits to a template show up without a restart, and leave it at the default `False` in production.

In a Pyramid app this call goes in the `main` function that builds the WSGI app. In a FastAPI app it goes at module level next to the app object or in the lifespan startup. Registration is process-wide module state, so call it from single-threaded startup code, not from a request handler.

Calling it a second time after a successful registration does nothing. That is intended, so repeated startup calls are safe. See [Testing](testing.md) for how to point at a different folder.


# Make render_partial available to templates

A template can only call [render_partial](../reference/render_partial.md#chameleon_partials.render_partial) if the name is in its model. Wire that once, in whichever way your framework supports.

In Pyramid, add a `BeforeRender` subscriber. Drop this file into your `views` package so `config.scan()` picks it up, and every template gets [render_partial](../reference/render_partial.md#chameleon_partials.render_partial) with no change to the views:

``` python
# views/partials_middleware.py
from pyramid.events import BeforeRender, subscriber

import chameleon_partials


@subscriber(BeforeRender)
def add_global(event):
    event['render_partial'] = chameleon_partials.render_partial
```

In any other framework, extend the model dictionary before you hand it to the template:

``` python
model = {'videos': videos}
return chameleon_partials.extend_model(model)
```

[extend_model](../reference/extend_model.md#chameleon_partials.extend_model) adds the [render_partial](../reference/render_partial.md#chameleon_partials.render_partial) key to the dictionary you pass and returns the same dictionary. It accepts `None` and returns a new dictionary in that case.


# Write a partial

A partial is a plain Chameleon template holding a fragment of HTML. It does not need a layout, a `<html>` element, or a `metal:define-macro`. Keep partials together under a folder such as `shared/partials/` so they are easy to find:

``` html
<!-- templates/shared/partials/video_image.pt -->
<img src="https://img.youtube.com/vi/${ video.id }/maxresdefault.jpg"
     class="img img-responsive ${ ' '.join(classes or []) }"
     alt="${ video.title }"
     title="${ video.title }">
```

The template references `video` and `classes`. Those names come from the keyword arguments of the [render_partial](../reference/render_partial.md#chameleon_partials.render_partial) call that renders it.


# Render it

From any page template, or from another partial, call [render_partial](../reference/render_partial.md#chameleon_partials.render_partial) inside a `${ }` expression. The first argument is the path relative to the registered folder. The keyword arguments become the fragment's model:

``` html
[${ render_partial('shared/partials/video_image.pt', video=video, classes=[]) }](https://www.youtube.com/watch?v=${ video.id })
```

[render_partial](../reference/render_partial.md#chameleon_partials.render_partial) returns an `HTML` object rather than a string. Chameleon sees its `__html__` method and inserts the markup as is, without escaping it. A plain string in the same position would be escaped.

That is the whole mechanism. [Writing partials](writing-partials.md) covers nesting, loops, layouts, and the rules a partial name has to follow.
