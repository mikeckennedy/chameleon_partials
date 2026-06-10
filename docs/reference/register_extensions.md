## register_extensions()


Register chameleon_partials with Chameleon so partials can be rendered.


Usage

``` python
register_extensions(
    template_folder,
    auto_reload=False,
    cache_init=True,
)
```


Call this once during application startup, before any template is rendered. It builds a Chameleon `PageTemplateLoader` rooted at `template_folder` and stores it in module-level state that [render_partial](render_partial.md#chameleon_partials.render_partial) uses to locate templates. Registration is process-wide and is not guarded by a lock, so call it from normal single-threaded startup code rather than from concurrent request handlers.


## Parameters


`template_folder: str`  
Path to the root folder containing your Chameleon templates (with a `partials` subfolder by convention). Must be an existing directory. Partials are later looked up by path relative to this folder.

`auto_reload: bool = ``False`  
When `True`, Chameleon reloads a template from disk whenever the file changes. Useful during development; leave `False` in production.

`cache_init: bool = ``True`  
When `True` (the default), calling this again after a previous successful registration is a no-op, which makes repeated startup calls safe. Pass `False` to force re-registration, for example to point at a different template folder in tests.


## Raises


`PartialsException`  
If `template_folder` is empty or is not an existing directory.


## Examples

``` python
import chameleon_partials

# At startup; use auto_reload=True while developing.
chameleon_partials.register_extensions('path/to/templates', auto_reload=True)
```
