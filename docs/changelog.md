# Changelog

This changelog is generated automatically from [GitHub Releases](https://github.com/mikeckennedy/chameleon_partials/releases).


# v0.2.0

*2026-06-11* · [GitHub](https://github.com/mikeckennedy/chameleon_partials/releases/tag/v0.2.0)


## \[0.2.0\] - 2026-06-10


### Added

- Google-style docstrings, complete type annotations, and runnable usage examples for the public API ([register_extensions](reference/register_extensions.html#chameleon_partials.register_extensions), [render_partial](reference/render_partial.html#chameleon_partials.render_partial), [extend_model](reference/extend_model.html#chameleon_partials.extend_model), [PartialsException](reference/PartialsException.html#chameleon_partials.PartialsException)) and the internal `HTML` wrapper.
- PEP 561 `py.typed` marker, so type checkers consume the package's inline type annotations; the package checks clean under `ty` and `pyrefly`, which join the dev requirements.
- Documentation site rendered from those docstrings with Great Docs, published at https://mkennedy.codes/docs/chameleon-partials/. Includes `scripts/build_docs.py` and `scripts/serve_docs.py`; the built site is committed in `docs/`, and `great-docs` joins the `dev` extra (skipped automatically on Python \< 3.11).
- Project URLs in the package metadata for the PyPI sidebar -- Issues, Changelog, and Funding (GitHub Sponsors) -- alongside the existing Homepage, Repository, and Documentation links.
- Pyramid `BeforeRender` middleware pattern, documented in the README and wired into the example app, so views do not have to add [render_partial](reference/render_partial.html#chameleon_partials.render_partial) to every model by hand.
- Test suite (`tests/test_rendering.py`) covering bare renders, partials with data, layouts, nested (recursive) partials, and error conditions.
- Pytest configuration (`[tool.pytest.ini_options]`, `testpaths = ["tests"]`) so a bare `pytest` from the repo root runs only the package's tests instead of erroring while collecting the standalone `example/` app's suite (which needs Pyramid and WebTest).
- This changelog.


### Changed

- Packaging migrated from `setup.py` to a PEP 621 `pyproject.toml`. The version stays single-sourced in `chameleon_partials/__init__.py` and dependencies in `requirements*.txt` (read dynamically), so the built wheel is unchanged aside from added project URLs.
- Raised the minimum supported Python from 3.6 to 3.9 (3.6-3.8 are end-of-life and match no supported Chameleon release). Trove classifiers now cover Python 3.9-3.14, and the development status is Production/Stable.


### Fixed

- [register_extensions](reference/register_extensions.html#chameleon_partials.register_extensions) no longer marks the extension as registered when registration fails. The flag used to be set before the template folder was validated, so a failed call left the library flagged as registered and a later retry with the default `cache_init=True` silently did nothing. Failed registrations can now simply be retried. (Behavior change.)
- [extend_model](reference/extend_model.html#chameleon_partials.extend_model)'s type annotation now accepts `None` (`Optional[Dict[str, Any]]`), matching its documented and actual behavior.
- Ruff's `target-version` is now `py39` to match `requires-python` (was `py313`), so Ruff won't rewrite code into newer-only idioms that would break on Python 3.9.
- README accuracy: the Pyramid startup snippet now imports `Configurator`, the listing snippet matches the example app's template (`span`, not `div`), and several typos were corrected: "incredible easy", "subtitle of author", "them middleware", and "veiws" ([\#2](https://github.com/mikeckennedy/chameleon_partials/pull/2), thanks [<span class="citation" cites="hodgesd">@hodgesd</span>](https://github.com/hodgesd)).
