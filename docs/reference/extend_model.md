## extend_model()


Add [render_partial](render_partial.md#chameleon_partials.render_partial) to a view model so templates can call it.


Usage

``` python
extend_model(model)
```


Use this in frameworks where a view returns a model dictionary (for example FastAPI) and you need [render_partial](render_partial.md#chameleon_partials.render_partial) available inside the template. For Pyramid, prefer the `BeforeRender` middleware shown in the README instead. Any existing [render_partial](render_partial.md#chameleon_partials.render_partial) key in the model is replaced.


## Parameters


`model: Optional[Dict[str, Any]]`  
The view model dictionary to extend. `None` is treated as an empty model.


## Returns


`Dict[str, Any]`  
The same dictionary with a [render_partial](render_partial.md#chameleon_partials.render_partial) key added, or a new dictionary when `model` is `None`.


## Raises


`PartialsException`  
If `model` is not a dictionary (and not `None`).


## Examples

``` python
import chameleon_partials

model = {'name': 'Sarah'}
model = chameleon_partials.extend_model(model)
# model['render_partial'] is now callable from the template.
```
