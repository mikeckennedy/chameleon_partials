## PartialsException


Raised when chameleon_partials is configured or used incorrectly.


Usage

``` python
PartialsException()
```


Examples include registering with a missing template folder, rendering a partial before calling [register_extensions](register_extensions.md#chameleon_partials.register_extensions), or passing a non-dictionary model to [extend_model](extend_model.md#chameleon_partials.extend_model). Errors raised by Chameleon itself, such as the `ValueError` for a missing template file, are propagated unchanged rather than wrapped in this type.
