---
name: chameleon-partials
description: >
  Simple reuse of partial HTML page templates in the Chameleon template language for Python web frameworks. Use when writing Python code that uses the chameleon_partials package.
license: MIT
compatibility: Requires Python >=3.9.
---

# Chameleon Partials

Simple reuse of partial HTML page templates in the Chameleon template language for Python web frameworks.

## Installation

```bash
pip install chameleon-partials
```

## API overview

### Setup

Register chameleon_partials with Chameleon. Call this once at application startup.

- `register_extensions`: Register chameleon_partials with Chameleon so partials can be rendered

### Rendering partials

Render partial templates and expose render_partial to your view models.

- `render_partial`: Render a partial template to an HTML fragment
- `extend_model`: Add `render_partial` to a view model so templates can call it

### Exceptions

Errors raised by the library.

- `PartialsException`: Raised when chameleon_partials is configured or used incorrectly

## Resources

- [Full documentation](https://mkennedy.codes/docs/chameleon-partials/)
- [llms.txt](llms.txt) — Indexed API reference for LLMs
- [llms-full.txt](llms-full.txt) — Comprehensive documentation for LLMs
- [Source code](https://github.com/mikeckennedy/chameleon_partials)
