# Getting started

This page takes an app from nothing to a rendered fragment in four moves. It assumes a framework that already renders Chameleon templates, such as Pyramid with `pyramid_chameleon`, or FastAPI calling Chameleon directly. The snippets come from the demo video site, so the fragment we build is the YouTube thumbnail that every video card shares.


# Move one: install

``` bash
uv add chameleon-partials
# or
pip install chameleon-partials
```

Two spellings, and both matter. The distribution on PyPI is `chameleon-partials` with a hyphen. The module you import is `chameleon_partials` with an underscore. The package is pure Python and its only runtime dependency is Chameleon itself.


# Move two: tell the library where the templates live

The library needs to know one thing before it can do anything: the root folder of your Chameleon templates. Tell it once, at startup, before any template renders:

``` python
from pathlib import Path

import chameleon_partials

folder = (Path(__file__).parent / 'templates').as_posix()
chameleon_partials.register_extensions(folder, auto_reload=True)
```

Build the path from `__file__` rather than a relative string, so it works no matter which directory the process was launched from. Every partial you render later is named by its path relative to this folder, which is why this is the only place the folder ever appears.

`auto_reload=True` makes Chameleon check a template's modification time on each render and recompile when it changed, so you can edit a fragment and refresh the browser. It costs a stat call per render, so leave it at the default `False` in production and restart on deploy.

In a Pyramid app this call belongs in the `main` function that builds the WSGI app. In FastAPI it goes at module level beside the app object, or in the lifespan startup. The registration is process-wide module state, so it wants single-threaded startup code, not a request handler.

One more thing worth knowing now rather than later: once a call to [register_extensions](../reference/register_extensions.md#chameleon_partials.register_extensions) has succeeded, calling it again does nothing. That is on purpose, so an app that initialises twice does not rebuild its loader, and it is exactly the behaviour a test suite needs to know about. [Testing](testing.md) covers how to point tests at their own folder.


# Move three: open the door for your templates

A template can only call [render_partial](../reference/render_partial.md#chameleon_partials.render_partial) if that name is in its model. Chameleon has no global namespace to drop it into, so you wire it once in whatever way your framework offers.

Pyramid has the nicest answer. A `BeforeRender` subscriber runs before every template render and can add names to the model. Put this file inside the package that `config.scan()` covers and forget about it:

``` python
# views/partials_middleware.py
from pyramid.events import BeforeRender, subscriber

import chameleon_partials


@subscriber(BeforeRender)
def add_global(event):
    event['render_partial'] = chameleon_partials.render_partial
```

Every view in the app now returns its model exactly as before, and every template can call [render_partial](../reference/render_partial.md#chameleon_partials.render_partial).

Elsewhere, extend the model dictionary on its way out of the view:

``` python
model = {'videos': videos}
return chameleon_partials.extend_model(model)
```

[extend_model](../reference/extend_model.md#chameleon_partials.extend_model) adds the [render_partial](../reference/render_partial.md#chameleon_partials.render_partial) key to the dictionary you give it and returns that same dictionary. Hand it `None` and you get a fresh dictionary back.


# Move four: write a fragment and render it

A partial is a plain Chameleon template holding a piece of HTML. No layout, no `<html>` element, no `metal:define-macro`. Here is the thumbnail, as it lives in the demo app:

``` html
<!-- templates/shared/partials/video_image.pt -->
<img src="https://img.youtube.com/vi/${ video.id }/maxresdefault.jpg"
     class="img img-responsive ${ ' '.join(classes or []) }"
     alt="${ video.title }"
     title="${ video.title }">
```

It uses two names, `video` and `classes`. Nothing in the file says where those come from, and that is the point: they come from whoever renders it. A folder named `shared/partials/` is only a convention, but it is a good one, because six months from now you will want to know which `.pt` files are pages and which are pieces.

Now render it. From a page template, or from inside another partial, call [render_partial](../reference/render_partial.md#chameleon_partials.render_partial) in a `${ }` expression. The first argument is the path relative to the registered folder, and the keyword arguments are the fragment's model:

``` html
[${ render_partial('shared/partials/video_image.pt', video=video, classes=[]) }](https://www.youtube.com/watch?v=${ video.id })
```

Reload the page and the thumbnail is there. Behind the scenes [render_partial](../reference/render_partial.md#chameleon_partials.render_partial) looked the file up in the registered folder, rendered it with `video` and `classes` in scope, and returned an `HTML` object rather than a string. Chameleon notices the object's `__html__` method and inserts the markup as is. Had the function returned a plain string, Chameleon would have escaped it and you would be looking at a literal `<img` on the page. That small wrapper is what makes the whole thing feel native.

Those four moves are the entire library. Everything else is the rulebook, and [Writing partials](writing-partials.md) is where it lives.
