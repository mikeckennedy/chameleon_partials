# Troubleshooting

This is a field guide. Each heading is an error message, or the symptom you see when there is no message, so you can search this page for the exact text in your terminal. Under each one: what happened, why, and what to do about it.

The first five come from chameleon_partials itself and arrive as [PartialsException](../reference/PartialsException.md#chameleon_partials.PartialsException). They all mean the library was set up or called wrongly, and they are all quick to fix. Everything after that comes from Chameleon or Python and passes through unchanged, because the package deliberately never wraps another library's errors.


# PartialsException: You must call register_extensions() before this function can be used

[render_partial](../reference/render_partial.md#chameleon_partials.render_partial) ran before anyone told the library where the templates are. This is the classic first-request-in-a-new-project error. Move [register_extensions](../reference/register_extensions.md#chameleon_partials.register_extensions) to application startup, before the first request is served: in Pyramid, the `main` function that builds the WSGI app. In a test, add a fixture that registers the test template folder, as shown in [Testing](testing.md).


# PartialsException: The template_folder must be specified

[register_extensions](../reference/register_extensions.md#chameleon_partials.register_extensions) was called with an empty string or `None`, usually from a setting that was never filled in. Pass the path to the templates folder, and build it from `__file__` so the working directory cannot change the answer:

``` python
folder = (Path(__file__).parent / 'templates').as_posix()
```


# PartialsException: The specified template folder must be a folder

The path exists in your head but not on disk, or it points at a file. Check the spelling and whether the path is meant to be absolute or relative. The failed call did not mark the library as registered, so once the path is right, a plain retry works. No flag to reset.


# PartialsException: The model must be a dictionary

[extend_model](../reference/extend_model.md#chameleon_partials.extend_model) was handed something other than a `dict` or `None`. A common way to get here is returning a list or a model object from a view and wrapping that. Pass the view-model dictionary, or `None` to get a fresh one back.


# ValueError: Template not found

[render_partial](../reference/render_partial.md#chameleon_partials.render_partial) could not turn the name into a regular file inside the registered folder. This is the most common error on this page, and it has five causes. Work through them in order:

- The path is relative to the registered folder, not to the calling template. From inside `shared/partials/a.pt`, a sibling is `shared/partials/b.pt`, not `b.pt` and not `./b.pt`. This is the cause nine times out of ten.
- The name points at a folder rather than a file, for example `shared/partials` without the file name on the end.
- The name reaches outside the registered folder: an absolute path, a `..` that climbs out, or a `package:path` spec. These are refused on purpose. Move the file under the registered folder, or register a folder higher up.
- The case does not match on Linux. `Video_Square.pt` and `video_square.pt` are different files there, even though macOS and Windows would cheerfully load either. This one tends to appear the first time the app runs in a container.
- The registered folder is not the one you think, usually because an earlier [register_extensions](../reference/register_extensions.md#chameleon_partials.register_extensions) call pointed somewhere else and the second call was a no-op. See the next heading.


# render_partial uses the wrong folder, or a second register_extensions is ignored

With the default `cache_init=True`, [register_extensions](../reference/register_extensions.md#chameleon_partials.register_extensions) does nothing once a previous call has succeeded. In an application that is the behaviour you want. In a test suite, or in a process that must switch folders, pass `cache_init=False` or set `chameleon_partials.has_registered_extensions = False` before registering again.


# NameError: render_partial

Chameleon went looking for [render_partial](../reference/render_partial.md#chameleon_partials.render_partial) in the template's model and found nothing. A partial always receives it, so this only happens in a page template, and it means the wiring step was skipped or did not take. In Pyramid, check that the module holding the `BeforeRender` subscriber sits inside a package that `config.scan()` covers; a subscriber in a file nobody imports is a subscriber that never registers. In other frameworks, make sure the view returns `chameleon_partials.extend_model(model)` and not just `model`.


# NameError: some other name

A partial references a name that the [render_partial](../reference/render_partial.md#chameleon_partials.render_partial) call did not pass. Chameleon's message shows the expression, the file, and the line, so the fix is usually obvious: add the keyword argument to the call, or give the partial a fallback with `tal:define` if the value is genuinely optional.


# TypeError: render() got multiple values for keyword argument 'encoding'

The model included a value called `encoding`. That name is already taken by the package's own call into Chameleon. Rename the variable; `charset` or `text_encoding` both work.


# The fragment shows up as escaped text

The page displays the markup literally, `<div>` and all. The value inserted into the template was a plain string, almost always `html_text`, instead of the `HTML` object that [render_partial](../reference/render_partial.md#chameleon_partials.render_partial) returns. Pass the object through to the template and read `html_text` only at the edge, where you need a real `str`: a response body, an email, a test assertion.


# Edits to a template do not show up

You changed the file, refreshed, and nothing happened. Chameleon compiled the template once and is serving the compiled version. Register with `auto_reload=True` during development so it checks the file's timestamp on each render. In production, leave it `False` and restart after deploying template changes.


# RecursionError

A partial renders itself, directly or through a chain of other partials, with nothing to stop it. Add a `tal:condition` around the nested call that checks a depth counter or an empty children list, and pass that value down on each call.


# IsADirectoryError, or a file outside the templates folder rendered

Both were possible in older releases: the directory error until 0.2.2, the outside file until 0.2.1. Upgrade. Current releases report a folder name or an outside path as `ValueError: Template not found`, and the containment check sees the name exactly as Chameleon's loader does. The check is lexical, so a symlink inside the folder is still followed; keep symlinks out of the templates folder if that matters to you.
