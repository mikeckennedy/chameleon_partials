# Troubleshooting

Each heading below is an error you can hit in normal use, with the cause and the fix. The first group comes from chameleon_partials and is raised as [PartialsException](../reference/PartialsException.md#chameleon_partials.PartialsException). The rest come from Chameleon or Python and pass through unchanged, because the package never wraps them.


# PartialsException: You must call register_extensions() before this function can be used

[render_partial](../reference/render_partial.md#chameleon_partials.render_partial) ran before [register_extensions](../reference/register_extensions.md#chameleon_partials.register_extensions). Move the registration to application startup, before the first request. In Pyramid that is the `main` function that builds the WSGI app. In a test, add a fixture that registers the test template folder, as shown in [Testing](testing.md).


# PartialsException: The template_folder must be specified

[register_extensions](../reference/register_extensions.md#chameleon_partials.register_extensions) was called with an empty string or `None`. Pass the path to your templates folder. Build it from `__file__` so it does not depend on the working directory:

``` python
folder = (Path(__file__).parent / 'templates').as_posix()
```


# PartialsException: The specified template folder must be a folder

The path passed to [register_extensions](../reference/register_extensions.md#chameleon_partials.register_extensions) does not exist or is a file. Check the spelling and that the path is absolute or relative to the right place. The failed call does not mark the package as registered, so after fixing the path a plain retry works.


# PartialsException: The model must be a dictionary

[extend_model](../reference/extend_model.md#chameleon_partials.extend_model) was given something other than a `dict` or `None`. Pass the view-model dictionary, or `None` to get a new one back.


# ValueError: Template not found

[render_partial](../reference/render_partial.md#chameleon_partials.render_partial) could not resolve the name to a regular file inside the registered folder. Check these causes in order:

- The path is relative to the registered folder, not to the calling template. From inside `shared/partials/a.pt`, a sibling is `shared/partials/b.pt`, not `b.pt` and not `./b.pt`.
- The name points at a folder rather than a file, for example `shared/partials` without the file name.
- The name reaches outside the registered folder: an absolute path, a `..` that leaves the folder, or a `package:path` spec. These are refused on purpose. Move the file under the registered folder or register a higher folder.
- The case does not match on Linux. `Video_Square.pt` and `video_square.pt` are different files there, even though macOS and Windows would load either.
- The registered folder is not the one you think, usually because [register_extensions](../reference/register_extensions.md#chameleon_partials.register_extensions) was called earlier with a different folder and the second call was a no-op. See the next heading.


# render_partial uses the wrong folder, or a second register_extensions is ignored

With the default `cache_init=True`, [register_extensions](../reference/register_extensions.md#chameleon_partials.register_extensions) does nothing once a previous call succeeded. In an application that is the behaviour you want. In tests, or in a process that must switch folders, pass `cache_init=False` or set `chameleon_partials.has_registered_extensions = False` before registering again.


# NameError: render_partial

Chameleon could not find [render_partial](../reference/render_partial.md#chameleon_partials.render_partial) in the template's model. The partial itself always gets it, so this happens in a page template. In Pyramid, make sure the `BeforeRender` subscriber module is inside a package that `config.scan()` covers and that it is imported. In other frameworks, return `chameleon_partials.extend_model(model)` from the view instead of `model`.


# NameError: some other name

A partial references a name that the [render_partial](../reference/render_partial.md#chameleon_partials.render_partial) call did not pass. Add the keyword argument to the call, or give the partial a fallback with `tal:define`. Chameleon's error message shows the expression, the file, and the line.


# TypeError: render() got multiple values for keyword argument 'encoding'

The model passed a value named `encoding`. That name is taken by the package's own call into Chameleon. Rename the variable.


# The fragment shows up as escaped text

The markup appears literally, with `<div>` where tags should be. The value inserted into the template was a plain string, usually `html_text`, rather than the `HTML` object that [render_partial](../reference/render_partial.md#chameleon_partials.render_partial) returns. Pass the object through, and only read `html_text` where you need a `str`, such as a response body or a test assertion.


# Edits to a template do not show up

Chameleon compiled the template once and is serving the compiled version. Register with `auto_reload=True` during development, and restart the process after template changes in production, where the default `False` is the right setting.


# RecursionError

A partial renders itself, directly or through another partial, without a condition that stops. Add a `tal:condition` around the nested call, or pass a depth that the partial checks.


# IsADirectoryError, or a file outside the templates folder rendered

Both were possible before 0.2.2 and 0.2.1 respectively. Upgrade. Current releases report a folder name or an outside path as `ValueError: Template not found`. The check is lexical, so a symlink inside the folder is still followed; keep symlinks out of the templates folder if that matters to you.
