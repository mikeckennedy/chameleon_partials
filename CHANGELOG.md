# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.2] - 2026-11-06

### Security

- `render_partial` strips surrounding whitespace from a name before checking it, as Chameleon's loader does before loading it. The 0.2.1 check saw the unstripped name, so a leading space, tab, or newline (`' ../secret.pt'`) passed the check as the folder `' ..'` and then loaded the file outside the template folder. Stripping first makes the check and the loader see one string; a harmless name with surrounding whitespace still renders, as before.

### Fixed

- Every spelling of a partial now compiles and caches one template. Chameleon's loader caches by the exact name it is given, so `./shared/card.pt`, `shared//card.pt`, `shared/../shared/card.pt`, and whitespace variants each kept their own compiled copy for the life of the process, which a request-chosen name could grow without bound. Names are normalized first; distinct case spellings on a case-insensitive filesystem still cache separately.
- A name that is a folder (`partials`, `partials/`, `.`) raises `ValueError` (`Template not found: ...`) instead of leaking an `IsADirectoryError` from inside Chameleon.

### Added

- `_template_name(template_file, folder)`, the single function `render_partial` now resolves names through. It returns the normalized name to load or `None` for a refused or missing one. chameleon-rs calls it when it renders a partial on behalf of this package, so both engines share one check.
- Guidance in the `render_partial` docs and README: choose the partial in code and map any request value to a name you wrote, and pass the model as named keyword arguments rather than spreading request parameters into it.

### Changed

- The minimum supported Python is now 3.10 (`requires-python >= 3.10`), and the 3.9 trove classifier is gone. Chameleon itself still supports 3.9; stay on 0.2.1 if you need it.

### Documentation

- A user guide on the docs site, also included in `llms-full.txt`: getting started, writing partials (path resolution, the model, nesting, loops, METAL layouts, rendering from Python, choosing partials safely), testing, and a troubleshooting page that lists every error the package or Chameleon raises in normal use with its cause and fix. The README links each page and gained Testing and Troubleshooting sections.
- The agent skill (`skill.md` and the `.well-known` copies) is now hand-written in `skills/chameleon-partials/SKILL.md` and copied verbatim by Great Docs, replacing the generated one. It states the rules an agent would otherwise get wrong (path resolution, the one-shot registration, the error contract, reserved model names, the `HTML` wrapper), a decision table, the API with what each name raises, and real output.
- The module docstring names the four public entry points, the `HTML` wrapper, and the error contract, since it is the first thing an agent sees on import.
- `scripts/build_docs.py` now fails when `llms.txt`, `llms-full.txt`, `skill.md`, or a `.well-known` skill file is missing from the built site. Great Docs reports success even when it could not import the package to write `llms-full.txt`.
- The example app's own test suite passes again: `tests/test_views.py` imported a `my_view` that no longer existed and now tests the `index` view, `test_functional.py` asserts on the rendered partials rather than on text the home page never had, and the `Video` model's optional `category` field has a default so the app loads under pydantic 2.

## [0.2.1] - 2026-10-28

### Security

- `render_partial` refuses names that would load a file outside the registered template folder: an absolute path, a `..` out of the folder, or a `package:path` spec. These used to reach Chameleon's loader as is, which loaded the file and ran it as a template; they now raise Chameleon's own `ValueError` (`Template not found: ...`), as a missing file does. A `..` that stays inside the folder still works, and the check is lexical, so a symlink inside the folder is still followed.

## [0.2.0] - 2026-06-10

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
- Project URLs in the package metadata for the PyPI sidebar — Issues, Changelog, and
  Funding (GitHub Sponsors) — alongside the existing Homepage, Repository, and
  Documentation links.
- Pyramid `BeforeRender` middleware pattern, documented in the README and wired into
  the example app, so views do not have to add `render_partial` to every model by
  hand.
- Test suite (`tests/test_rendering.py`) covering bare renders, partials with data,
  layouts, nested (recursive) partials, and error conditions.
- Pytest configuration (`[tool.pytest.ini_options]`, `testpaths = ["tests"]`) so a bare
  `pytest` from the repo root runs only the package's tests instead of erroring while
  collecting the standalone `example/` app's suite (which needs Pyramid and WebTest).
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
- Ruff's `target-version` is now `py39` to match `requires-python` (was `py313`), so
  Ruff won't rewrite code into newer-only idioms that would break on Python 3.9.
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

[0.2.2]: https://pypi.org/project/chameleon-partials/0.2.2/
[0.2.1]: https://pypi.org/project/chameleon-partials/0.2.1/
[0.2.0]: https://pypi.org/project/chameleon-partials/0.2.0/
[0.1.0]: https://pypi.org/project/chameleon-partials/0.1.0/
