# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

`AGENTS.md` and `GEMINI.md` are symlinks to this file — always edit `CLAUDE.md`, and never
replace the symlinks with regular files. `WARP.md` is a separate, older guidance file (not
a symlink); this file supersedes it where they disagree.

## What this is

chameleon_partials is a small, single-module library: the entire implementation is
`chameleon_partials/__init__.py` (~200 lines). It lets Chameleon templates render reusable
partial HTML fragments via a `render_partial()` function, for any Python web framework that
renders Chameleon templates (Pyramid, FastAPI, ...). It is the Chameleon sibling of
[jinja_partials](https://github.com/mikeckennedy/jinja_partials).

The PyPI name is `chameleon-partials` (hyphen); the import is `chameleon_partials` (underscore).

## Environment and commands

The project venv lives at `venv/` (not `.venv`) and is uv-managed. `uv run` resolves to
`venv/` because `UV_PROJECT_ENVIRONMENT=venv` is set in this environment; `venv/bin/<tool>`
works equivalently everywhere `uv run <tool>` is shown. `uv.lock` is deliberately
git-ignored (machine-local; uv regenerates it) — never force-add it.

```bash
uv run pytest                                                  # full test suite (tests/ only)
uv run pytest tests/test_rendering.py::test_render_with_data   # single test by node id
uv run ruff check                                              # lint (--fix to auto-fix)
uv run ruff format                                             # format (--check to verify only)
uv run ty check chameleon_partials                             # type check (must pass clean)
uv run pyrefly check chameleon_partials/__init__.py            # second type checker (must pass clean)
venv/bin/python scripts/build_docs.py                          # rebuild docs site into docs/
venv/bin/python scripts/serve_docs.py                          # preview at 127.0.0.1:8099/docs/chameleon-partials/
```

- Run pytest from the repo root: `[tool.pytest.ini_options] testpaths = ["tests"]`
  deliberately excludes `example/`, whose tests need Pyramid/WebTest (not installed in the
  root venv).
- A repo-wide `ty check` (no path argument) fails on `example/`: unresolved-import errors
  for Pyramid/pydantic/WebTest (not installed in the root venv), plus one for the
  known-stale `my_view` import in `example/tests/test_views.py` — scope it to the package
  as shown above.
- ruff is not declared in requirements-dev.txt; it is present only as a transitive
  dependency of great-docs (Python >= 3.11). Config is in `ruff.toml`: 120-char lines,
  single quotes, E/F/I rules, and `target-version = "py39"` — pinned to match
  `requires-python >= 3.9` so Ruff never rewrites `Optional[Dict]`-style typing into
  3.10+-only syntax. Do not bump it.
- There is no CI (`.github/` holds only FUNDING.yml); tests, lint, and type checks run
  locally only.

## Architecture

Everything hangs off module-level global state in `chameleon_partials/__init__.py`:

- `register_extensions(template_folder, auto_reload=False, cache_init=True)` builds a
  Chameleon `PageTemplateLoader` rooted at the folder and stores it in module globals.
  With the default `cache_init=True`, calling it again after one success is a silent
  no-op — tests pointing at a different folder must pass `cache_init=False` or reset
  `chameleon_partials.has_registered_extensions` (the `registered_extension` fixture in
  `tests/test_rendering.py` does this in teardown). The registered flag is set only after
  the loader builds successfully, so a failed registration can be retried — a 0.2.0
  bugfix; keep that ordering.
- `render_partial(template_file, **template_data)` looks templates up by path relative to
  the registered folder — always, even when called from inside another partial. It injects
  itself into the model (when not already present), which is what lets partials nest. It
  returns an `HTML` wrapper whose `__html__()` makes template engines insert the markup
  unescaped. `HTML` is deliberately excluded from `__all__`; tests read its `.html_text`.
- Error contract (promised in the docstrings — preserve it): `PartialsException` covers
  misuse/misconfiguration only; Chameleon's own errors propagate unwrapped (a missing
  template raises Chameleon's `ValueError`, not `PartialsException`).
- Integration patterns: Pyramid apps use a `BeforeRender` subscriber that sets
  `event['render_partial']` (see `example/demo_chameleon_partials/views/partials_middleware.py`);
  other frameworks call `extend_model(model)` on the view-model dict.

## Packaging

`pyproject.toml` keeps version and dependencies dynamic — edit the sources, not pyproject:

- The version is single-sourced from `__version__` in `chameleon_partials/__init__.py`;
  bump it there only.
- Runtime deps come from `requirements.txt` (just `chameleon`); the `dev` extra comes from
  `requirements-dev.txt`.
- `py.typed` must stay explicitly listed in `[tool.setuptools.package-data]`: the
  setuptools>=64 build floor predates automatic py.typed inclusion.

`CHANGELOG.md` follows Keep a Changelog + SemVer, with repo-specific conventions: there is
no `[Unreleased]` section — add entries under a dated `## [X.Y.Z] - YYYY-MM-DD` heading
with a matching bottom reference link to the PyPI release page
(`https://pypi.org/project/chameleon-partials/X.Y.Z/`). Releases are commits titled
`release: X.Y.Z`; the repo uses no git tags.

## Docs pipeline (inverted from the usual convention)

The site at https://mkennedy.codes/docs/chameleon-partials/ is generated by Great Docs
(Quarto-based; config in `great-docs.yml`) from the package's Google-style docstrings.
The build scratch dir `great-docs/` is git-ignored, while the generated site in `docs/`
IS committed (git-push static hosting, served by nginx at a subpath).

- **Never hand-edit `docs/`** — `scripts/build_docs.py` deletes and fully replaces it on
  every build. To change docs content, edit the docstrings or `great-docs.yml`, then
  rebuild (also available as the default VS Code build task, "Build Docs"). After a
  rebuild, commit the whole `docs/` diff; the only generated file excluded is
  `docs/build-timings.json`, which is git-ignored on purpose.
- Docs builds require the Quarto CLI on PATH (installed system-wide at
  `/usr/local/bin/quarto`, not via the venv) — great-docs shells out to it.
- `build_docs.py` applies two idempotent post-processing workarounds for great-docs 0.13.0
  bugs (pruning dead `search.json` entries; injecting canonical links from sitemap.xml).
  They must run on every build.
- `scripts/serve_docs.py` previews the committed site under the exact production subpath,
  so subpath-only asset/link breakage shows up locally. The VS Code launch configs offer
  two previews: "Preview Docs" (`great-docs preview`, live but served at the root path, so
  it does not exercise the production subpath) and "Preview Docs (subpath)"
  (`serve_docs.py`) — use the subpath one to validate links and assets.
- great-docs requires Python >= 3.11 (environment marker in requirements-dev.txt) even
  though the library itself supports 3.9+.
- The site ships agent-facing artifacts (`docs/llms.txt`, `docs/llms-full.txt`,
  `docs/skill.md`, and `.well-known/` skill files) — all generated; the same no-hand-edit
  rule applies.

## Example app (`example/`)

A standalone Pyramid demo (`demo_chameleon_partials`) with its own setup.py, ini files,
and test suite — set it up per `example/README.md`. Note that `chameleon_partials` itself
is not in the example's `requires`, so it must be installed into the example's env
separately (e.g. `pip install -e ..` from `example/`). Run it with
`env/bin/pserve development.ini` (http://localhost:6543).

It is the reference for real-world usage: the BeforeRender middleware, nested partials
inside `tal:repeat` loops, and METAL layout inheritance. Known-stale bit: its
`tests/test_views.py` imports a `my_view` that no longer exists (cookiecutter leftover),
so the example's own test suite does not pass as-is.
