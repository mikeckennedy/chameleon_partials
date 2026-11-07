#!/usr/bin/env python3
"""Build the docs and mirror the static site into the committed repo-root docs/ folder.

Great Docs renders the site to ``great-docs/_site/``, an ephemeral, git-ignored build
directory that is regenerated on every build. For git-push static hosting we keep a
committed copy of the site at the repo root in ``docs/`` (which nginx serves at the
subpath). This script runs the build, mirrors ``_site/`` into ``docs/`` (full replace),
applies two small post-processing fixes (see ``_postprocess`` below), and then fails if any
agent-facing file is missing from the output (see ``_check_required``): great-docs reports a
successful build even when it could not import the package to write ``llms-full.txt``.

Run it with the project's virtualenv interpreter, e.g.::

    venv/bin/python scripts/build_docs.py
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
PKG_DIR = _SCRIPTS.parent  # dir holding pyproject.toml + great-docs.yml
REPO_ROOT = PKG_DIR  # the package lives at the git root (single-tier)
SITE = PKG_DIR / 'great-docs' / '_site'
DEST = REPO_ROOT / 'docs'


def _site_url() -> str:
    """Read ``site_url`` from great-docs.yml so the canonical base never drifts from config."""
    cfg = PKG_DIR / 'great-docs.yml'
    if not cfg.is_file():
        return ''
    m = re.search(r'(?m)^\s*site_url:\s*["\']?([^"\'\n]+)', cfg.read_text(encoding='utf-8'))
    return m.group(1).strip() if m else ''


def _postprocess(dest: Path) -> None:
    """Work around two great-docs 0.13.0 bugs in the mirrored site.

    Both fix generated files, so they must run on every build (a hand-edit to docs/ would be
    overwritten). Each step is guarded and idempotent. great-docs 0.17.0 no longer trips either
    bug (no dead search entries, canonical links emitted), so both steps are quiet no-ops on a
    current build and stay here as guards.

    1. Prune dead entries from search.json. great-docs indexes a "skill" page as
       ``skill.html`` but only emits ``skill.md`` / ``skills.html``, so those search results
       404. We drop any entry whose target file does not exist under docs/.
    2. Inject ``<link rel="canonical">``. great-docs' canonical-injection guard
       false-positives on a JS string containing ``rel="canonical"`` and so emits no real
       canonical element. We add one per page, taking the exact URL from sitemap.xml so it
       matches the sitemap (and skipping any page that already has a canonical link, which
       keeps this forward-compatible once great-docs fixes the bug).
    """
    # 1) Prune search.json entries that point at missing files.
    search = dest / 'search.json'
    if search.is_file():
        try:
            entries = json.loads(search.read_text(encoding='utf-8'))
            kept = [
                e for e in entries if not (href := str(e.get('href', '')).split('#', 1)[0]) or (dest / href).exists()
            ]
            dropped = len(entries) - len(kept)
            if dropped:
                search.write_text(json.dumps(kept), encoding='utf-8')
                print(f'  search.json: pruned {dropped} dead entr{"y" if dropped == 1 else "ies"}')
        except (ValueError, OSError) as exc:  # pragma: no cover - defensive
            print(f'  search.json prune skipped: {exc}', file=sys.stderr)

    # 2) Inject canonical links derived from sitemap.xml.
    base = _site_url()
    sitemap = dest / 'sitemap.xml'
    if base and sitemap.is_file():
        injected = 0
        for loc in re.findall(r'<loc>([^<]+)</loc>', sitemap.read_text(encoding='utf-8')):
            if not loc.startswith(base):
                continue
            rel = loc[len(base) :]
            if rel == '' or rel.endswith('/'):
                rel += 'index.html'
            page = dest / rel
            if not page.is_file():
                continue
            html = page.read_text(encoding='utf-8')
            if re.search(r'<link[^>]*\brel="canonical"', html):
                continue
            new = html.replace('<head>', f'<head>\n<link rel="canonical" href="{loc}">', 1)
            if new != html:
                page.write_text(new, encoding='utf-8')
                injected += 1
        if injected:
            print(f'  canonical: injected <link rel=canonical> into {injected} page(s)')


# Files that must exist in every build. great-docs only writes llms-full.txt (and the
# one-line summaries in llms.txt) when it can import the package; if the import fails it
# prints "Could not import ..." and still reports success, so check the output directly.
REQUIRED = (
    'llms.txt',
    'llms-full.txt',
    'skill.md',
    '.well-known/skills/default/SKILL.md',
    '.well-known/agent-skills/index.json',
)


def _check_required(dest: Path) -> bool:
    """Return False (after printing what is missing) when an agent-facing file was not built."""
    missing = [rel for rel in REQUIRED if not (dest / rel).is_file()]
    index = dest / '.well-known/agent-skills/index.json'
    if index.is_file():
        try:
            for skill in json.loads(index.read_text(encoding='utf-8')).get('skills', []):
                for rel in skill.get('files', []):
                    path = f'.well-known/agent-skills/{skill.get("name", "")}/{rel}'
                    if not (dest / path).is_file():
                        missing.append(path)
        except ValueError as exc:
            missing.append(f'.well-known/agent-skills/index.json (unreadable: {exc})')
    for rel in missing:
        print(f'missing from the built site: {rel}', file=sys.stderr)
    return not missing


def main() -> int:
    # Prefer the great-docs installed alongside the running interpreter (the project venv),
    # falling back to whatever is on PATH.
    great_docs = Path(sys.executable).with_name('great-docs')
    cmd = [str(great_docs) if great_docs.exists() else 'great-docs', 'build']
    if subprocess.run(cmd, cwd=PKG_DIR).returncode != 0:
        return 1

    if not SITE.is_dir():
        print(f'build output missing: {SITE}', file=sys.stderr)
        return 1

    if DEST.exists():
        shutil.rmtree(DEST)
    shutil.copytree(SITE, DEST)
    _postprocess(DEST)
    if not _check_required(DEST):
        return 1
    print(f'Mirrored -> {DEST} ({sum(1 for p in DEST.rglob("*") if p.is_file())} files)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
