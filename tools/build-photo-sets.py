#!/usr/bin/env python3
"""Build the photographic reference sets in work/ from cash_rich/static2.

The static2 pages are 36 design experiments run against one prospect, so all
36 carry the same fictional firm and the same words. This script picks the
chosen few, repoints them at the shared assets in work/_assets, and swaps in a
distinct firm, phone number and copy deck for each — see tools/photo_copy_*.py.

    python3 tools/build-photo-sets.py                 # build every set
    python3 tools/build-photo-sets.py --set pi        # just one
    python3 tools/build-photo-sets.py --check         # report, write nothing

A maintenance tool, not a build step: Render publishes the repo as committed.
"""

import argparse
import html
import importlib
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
WORK = REPO / "work"
SOURCE = Path.home() / "fractal" / "cash_rich" / "static2"

# set key -> (copy module, destination directory)
SETS = {
    "pi": ("photo_copy_pi", "01-personal-injury"),
    "estate": ("photo_copy_estate", "21-estate-law"),
}

# Everything the source pages say about the one firm they were built for.
SOURCE_FIRM = "Vance &amp; Cole"
SOURCE_INITIALS = "V&amp;C"
SOURCE_PHONE = "(555) 019-2200"
SOURCE_TEL = "+15550192200"
# Nothing may survive from the source prospect's branding.
FORBIDDEN = ["Vance", "Cole", "019-2200", "0192200"]

NOINDEX = '<meta name="robots" content="noindex"/>\n'


def build_page(key, spec, dest_dir, check=False):
    src = SOURCE / f"hero-{key}.html"
    if not src.exists():
        return f"missing source {src}", None
    s = src.read_text()
    notes = []

    # --- assets: one shared copy for the whole work/ tree -------------------
    s = s.replace('href="fonts/', 'href="../_assets/fonts/')
    s = s.replace('src="hero/', 'src="../_assets/hero/')
    s = s.replace("url('hero/", "url('../_assets/hero/").replace('url("hero/', 'url("../_assets/hero/')
    s = s.replace("url(hero/", "url(../_assets/hero/")

    # --- the copy deck -----------------------------------------------------
    missed = []
    # longest first: a short key like "Free consultation" otherwise fires inside
    # a longer sentence and stops that sentence's own key from ever matching
    for old, new in sorted(spec["copy"].items(), key=lambda kv: -len(kv[0])):
        if old not in s:
            missed.append(old[:48])
            continue
        s = s.replace(old, new)
    applied = len(spec["copy"]) - len(missed)
    if missed:
        # Expected: the six decks carry different subsets of the source copy —
        # some have no figures block, some no review wall — so a key that is
        # absent here is usually absent from that design, not a typo.
        notes.append(f"{applied}/{len(spec['copy'])} applied, {len(missed)} n/a")

    # --- identity ----------------------------------------------------------
    firm_esc = html.escape(spec["firm"], quote=False).replace("&amp;amp;", "&amp;")
    s = s.replace(SOURCE_FIRM, firm_esc)
    s = s.replace(SOURCE_INITIALS, html.escape(spec["initials"], quote=False))
    s = s.replace(SOURCE_PHONE, spec["phone"])
    s = s.replace(SOURCE_TEL, spec["tel"])

    # --- title and headline ------------------------------------------------
    s = re.sub(r"<title>.*?</title>", "<title>" + html.escape(spec["title"], quote=False) + "</title>",
               s, count=1, flags=re.S)
    def swap_h1(m):
        sep = "<br/>" if "<br" in m.group(2) else " "
        return m.group(1) + sep.join(html.escape(l, quote=False) for l in spec["h1"]) + m.group(3)
    s, n = re.subn(r"(<h1[^>]*>)(.*?)(</h1>)", swap_h1, s, count=1, flags=re.S)
    if not n:
        notes.append("no <h1> found")

    # --- noindex, same as every other page under work/ ---------------------
    if 'name="robots"' not in s:
        s = s.replace('<meta charset="utf-8"/>\n', '<meta charset="utf-8"/>\n' + NOINDEX, 1)

    leftovers = [w for w in FORBIDDEN if w in s]
    if leftovers:
        notes.append(f"SOURCE BRANDING LEFT: {leftovers}")

    if not check:
        out = WORK / dest_dir / f"{spec['slug']}.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(s)
    return ("; ".join(notes) if notes else "ok"), spec["slug"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", dest="only", choices=sorted(SETS))
    ap.add_argument("--check", action="store_true", help="report without writing")
    args = ap.parse_args()

    sys.path.insert(0, str(REPO / "tools"))
    problems = 0
    for name, (module, dest) in SETS.items():
        if args.only and name != args.only:
            continue
        try:
            deck = importlib.import_module(module)
        except ModuleNotFoundError:
            print(f"[{name}] no copy deck yet ({module}.py) — skipped")
            continue
        print(f"[{name}] -> work/{dest}")
        for key, spec in deck.PAGES.items():
            status, slug = build_page(key, spec, dest, args.check)
            flag = "!" if ("SOURCE BRANDING" in status or "no <h1>" in status) else " "
            print(f"  {flag} {key:<14} {str(slug):<18} {status}")
            if "SOURCE BRANDING LEFT" in status or "no <h1>" in status:
                problems += 1
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
