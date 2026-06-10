## render_partial()


Render a partial template to an HTML fragment.


Usage

``` python
render_partial(
    template_file,
    **template_data,
)
```


Looks up `template_file` in the folder registered with [register_extensions](register_extensions.md#chameleon_partials.register_extensions) and renders it with the supplied keyword arguments as its model. [render_partial](render_partial.md#chameleon_partials.render_partial) is injected into the model automatically, so a partial can render further nested partials.


## Parameters


`template_file: str`  
Path to the partial, relative to the registered templates folder, for example `shared/partials/video_image.pt`.

`**template_data: Any`  
Keyword arguments passed to the template as its model (the variables the template can reference).


## Returns


`HTML`  
An `HTML` wrapper whose `__html__` method yields the rendered markup, so the result is

treated as safe, pre-escaped HTML when embedded in another template.


## Raises


`PartialsException`  
If [register_extensions](register_extensions.md#chameleon_partials.register_extensions) has not been called yet.
