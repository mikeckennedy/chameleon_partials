# API Reference


The complete public API of chameleon_partials: register the extension, render partial templates, share render_partial with your view models, and handle errors.


## Setup


Register chameleon_partials with Chameleon. Call this once at application startup.


[register_extensions()](register_extensions.md#chameleon_partials.register_extensions)  
Register chameleon_partials with Chameleon so partials can be rendered.


## Rendering partials


Render partial templates and expose render_partial to your view models.


[render_partial()](render_partial.md#chameleon_partials.render_partial)  
Render a partial template to an HTML fragment.

[extend_model()](extend_model.md#chameleon_partials.extend_model)  
Add `render_partial` to a view model so templates can call it.


## Exceptions


Errors raised by the library.


[PartialsException](PartialsException.md#chameleon_partials.PartialsException)  
Raised when chameleon_partials is configured or used incorrectly.
