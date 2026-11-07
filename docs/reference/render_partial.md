## render_partial()


Render a partial template to an HTML fragment.


Usage

``` python
render_partial(
    template_file,
    **template_data,
)
```


Looks up `template_file` in the folder registered with [register_extensions](register_extensions.md#chameleon_partials.register_extensions) and renders it with the supplied keyword arguments as its model. [render_partial](render_partial.md#chameleon_partials.render_partial) is injected into the model automatically, so a partial can render further nested partials. The fragment is rendered as text (`str`); any `bytes` values in the model are decoded as UTF-8.


## Parameters


`template_file: str`  
Path to the partial, relative to the registered templates folder, for example `shared/partials/video_image.pt`.

`**template_data: Any`  
Keyword arguments passed to the template as its model (the variables the template can reference). Values may be any Python objects your template expressions use. The name `encoding` is reserved and cannot be used; `translate`, `target_language`, and `repeat` have special meaning to Chameleon.


## Returns


`HTML`  
An `HTML` wrapper whose `__html__` method yields the rendered markup as safe, pre-escaped HTML.


## Raises


`PartialsException`  
If [register_extensions](register_extensions.md#chameleon_partials.register_extensions) has not been called yet.

`ValueError`  
Raised as Chameleon raises it for a missing file (`Template not found: ...`) when `template_file` does not name a regular file under the registered folder: a missing file, a folder, or a name that would reach outside the folder (an absolute path, a `..` out of the folder, or a `package:path` spec).


## Note

Surrounding whitespace is stripped and `./`, `//`, and a `..` that stays inside the folder are normalized away, so every spelling of a file compiles and caches one template. Distinct case spellings on a case-insensitive filesystem (macOS, Windows) still cache separately. The check that keeps a name inside the folder is lexical, so a symlink inside the folder is still followed.

Choose the partial in your code, never from request data. If a request picks the fragment, map the request value to a name you wrote (`PARTIALS = {'card': 'partials/card.pt'}`) instead of building the path from it, and pass the model as named keyword arguments rather than spreading a request's parameters into it (`render_partial(name, **request.params)` lets a parameter replace a name the template relies on, such as [render_partial](render_partial.md#chameleon_partials.render_partial) itself).


## Examples

``` python
import chameleon_partials

chameleon_partials.register_extensions('path/to/templates')
html = chameleon_partials.render_partial('shared/partials/user_card.pt', name='Sarah', age=32)
print(html.html_text)
```
