## PartialsException


Raised when chameleon_partials is configured or used incorrectly.


Usage

``` python
PartialsException()
```


Examples include registering with a missing template folder, rendering a partial before calling [register_extensions](register_extensions.md#chameleon_partials.register_extensions), or passing a non-dictionary model to [extend_model](extend_model.md#chameleon_partials.extend_model). Errors raised by Chameleon itself, such as the `ValueError` for a missing template file, are propagated unchanged rather than wrapped in this type.


## Examples

``` python
import chameleon_partials

try:
    chameleon_partials.render_partial('shared/partials/user_card.pt', name='Sarah')
except chameleon_partials.PartialsException:
    # register_extensions() has not been called yet; do that at startup.
    raise
except ValueError:
    # Chameleon's own error: the template file is missing or outside the folder.
    raise
```
