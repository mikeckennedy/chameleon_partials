# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Google-style docstrings, complete type annotations, and runnable usage examples for
  the public API (`register_extensions`, `render_partial`, `extend_model`,
  `PartialsException`) and the internal `HTML` wrapper.
- PEP 561 `py.typed` marker, so type checkers consume the package's inline type
  annotations; the package checks clean under `ty` and `pyrefly`, which join the dev
  requirements.
- Documentation site rendered from those docstrings with Great Docs, published at
  https://mkennedy.codes/docs/chameleon-partials/. Includes `scripts/build_docs.py`
  and `scripts/serve_docs.py`; the built site is committed in `docs/`, and
  `great-docs` joins the `dev` extra (skipped automatically on Python < 3.11).
- Pyramid `BeforeRender` middleware pattern, documented in the README and wired into
  the example app, so views do not have to add `render_partial` to every model by
  hand.
- Test suite (`tests/test_rendering.py`) covering bare renders, partials with data,
  layouts, nested (recursive) partials, and error conditions.
- This changelog.

### Changed

- Packaging migrated from `setup.py` to a PEP 621 `pyproject.toml`. The version stays
  single-sourced in `chameleon_partials/__init__.py` and dependencies in
  `requirements*.txt` (read dynamically), so the built wheel is unchanged aside from
  added project URLs.
- Raised the minimum supported Python from 3.6 to 3.9 (3.6-3.8 are end-of-life and
  match no supported Chameleon release). Trove classifiers now cover Python 3.9-3.14,
  and the development status is Production/Stable.

### Fixed

- `register_extensions` no longer marks the extension as registered when registration
  fails. The flag used to be set before the template folder was validated, so a
  failed call left the library flagged as registered and a later retry with the
  default `cache_init=True` silently did nothing. Failed registrations can now simply
  be retried. (Behavior change.)
- `extend_model`'s type annotation now accepts `None` (`Optional[Dict[str, Any]]`),
  matching its documented and actual behavior.
- README accuracy: the Pyramid startup snippet now imports `Configurator`, the
  listing snippet matches the example app's template (`span`, not `div`), and several
  typos were corrected: "incredible easy", "subtitle of author", "them middleware",
  and "veiws" ([#2](https://github.com/mikeckennedy/chameleon_partials/pull/2),
  thanks @hodgesd).

## [0.1.0] - 2021-07-27

Initial release.

### Added

- `register_extensions(template_folder, auto_reload=False, cache_init=True)`:
  one-time startup registration that points the library at your Chameleon templates
  folder.
- `render_partial(template_file, **template_data)`: renders a partial template to an
  `HTML` fragment; partials can nest by calling `render_partial` themselves.
- `extend_model(model)`: adds `render_partial` to a view-model dictionary for
  frameworks without a middleware hook.
- `HTML` wrapper implementing `__html__`, so rendered fragments are embedded verbatim
  instead of being escaped.
- `PartialsException`: raised for misconfiguration and misuse.
- Example Pyramid application (`example/`) showing video-card partials reused across
  pages, plus a README walkthrough.

[Unreleased]: https://github.com/mikeckennedy/chameleon_partials/commits/main
[0.1.0]: https://pypi.org/project/chameleon-partials/0.1.0/
