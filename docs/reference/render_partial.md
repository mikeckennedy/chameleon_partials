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
Propagated from Chameleon if `template_file` does not exist under the registered folder.


## Examples

``` python
import chameleon_partials

chameleon_partials.register_extensions('path/to/templates')
html = chameleon_partials.render_partial('shared/partials/user_card.pt', name='Sarah', age=32)
print(html.html_text)
```
