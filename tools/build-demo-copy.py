#!/usr/bin/env python3
"""Give every CSS-only reference build its own business and its own words.

The demo harness in cash_rich built six *designs* for one fictional company per
trade, so all six of Ridgeline Roofing's pages carry the same name, the same
headline and the same forty-two shared strings. Six of those published side by
side reads as one site recoloured, which is the failure the whole set exists to
argue against.

This rebuilds each page from the harness source with a per-page deck applied:
a distinct firm, a distinct phone number, and its own headline, subhead, proof
and closing copy. Trade-generic material — a roofer's four services, the order
of a job — is deliberately left alone. Six roofers really do tear off and
re-deck; what differs is who they are and what they lead with.

    python3 tools/build-demo-copy.py                # every trade with a deck
    python3 tools/build-demo-copy.py --trade 06-roofing
    python3 tools/build-demo-copy.py --check        # report, write nothing

Decks live in tools/demo_copy/<trade>.py. A maintenance tool, not a build step.
"""

import argparse
import html
import importlib
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
WORK = REPO / "work"
SOURCE = Path.home() / "fractal" / "cash_rich" / "demos"
NOINDEX = '<meta name="robots" content="noindex">\n'
CHARSET = '<meta charset="utf-8">\n'


BRAND_RE = re.compile(r'(<(?:a|div|span)[^>]*class="[^"]*\bbrand\b[^"]*"[^>]*>)(.*?)(</(?:a|div|span)>)', re.S)


def rebrand_split(page, source_firm, new_firm):
    """Rewrite nav wordmarks that split the firm name across markup.

    Several designs set the brand as `Ardent<span>.</span>Smile Studio` or
    `Ardent <span>Smile Studio</span>`, so a plain string replacement never
    matches. Rebuild the element's contents in whichever shape it already uses,
    so the design's own treatment of the wordmark survives the rename.
    """
    head = source_firm.split()[0]
    first, _, rest = new_firm.partition(" ")

    def swap(m):
        inner = m.group(2)
        if head not in re.sub(r"<[^>]+>", "", inner):
            return m.group(0)
        sep = re.search(r"<span[^>]*>([^<]{1,3})</span>", inner)
        e = lambda t: html.escape(t, quote=False)
        if sep and not sep.group(1).strip().isalnum():
            built = f"{e(first)}<span>{sep.group(1)}</span>{e(rest)}"
        elif "<span" in inner:
            built = f"{e(first)} <span>{e(rest)}</span>"
        else:
            built = e(new_firm)
        return m.group(1) + built + m.group(3)

    return BRAND_RE.sub(swap, page)


def build_page(deck, filename, spec, trade, check=False):
    src = SOURCE / trade / filename
    if not src.exists():
        return f"missing source {src}", 0
    s = src.read_text()
    notes = []

    # Page copy first: some keys quote the source firm, and replacing the firm
    # before them would stop those keys ever matching.
    missed = []
    for old, new in sorted(spec.get("copy", {}).items(), key=lambda kv: -len(kv[0])):
        if old not in s:
            missed.append(old[:46])
            continue
        s = s.replace(old, new)

    # The headline is shared across a trade's six designs and its markup varies,
    # so swap the element's contents rather than matching a literal string.
    if spec.get("h1"):
        lines = spec["h1"] if isinstance(spec["h1"], list) else [spec["h1"]]
        def swap(m):
            sep = "<br>" if "<br" in m.group(2) else " "
            return m.group(1) + sep.join(html.escape(l, quote=False) for l in lines) + m.group(3)
        s2, n = re.subn(r"(<h1[^>]*>)(.*?)(</h1>)", swap, s, count=1, flags=re.S)
        if n:
            s = s2
        else:
            notes.append("no <h1> found")

    firm = html.escape(spec["firm"], quote=False)
    s = s.replace(html.escape(deck.SOURCE_FIRM, quote=False), firm)
    s = s.replace(deck.SOURCE_FIRM, spec["firm"])
    s = s.replace(deck.SOURCE_PHONE, spec["phone"])
    s = s.replace(deck.SOURCE_TEL, spec["tel"])
    for short, repl in spec.get("short", {}).items():
        s = s.replace(short, repl)
    s = rebrand_split(s, deck.SOURCE_FIRM, spec["firm"])

    if 'name="robots"' not in s and CHARSET in s:
        s = s.replace(CHARSET, CHARSET + NOINDEX, 1)

    stale = [w for w in deck.FORBIDDEN if w in s]
    if stale:
        notes.append(f"SOURCE BRANDING LEFT: {stale}")
    if missed:
        notes.append(f"{len(missed)} keys n/a: {missed[:2]}")

    if not check:
        (WORK / trade / filename).write_text(s)
    return ("; ".join(notes) if notes else "ok"), len(spec.get("copy", {})) - len(missed)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trade")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    sys.path.insert(0, str(REPO / "tools"))
    decks = sorted(p.stem for p in (REPO / "tools" / "demo_copy").glob("[0-9]*.py"))
    if args.trade:
        decks = [d for d in decks if d == args.trade]
        if not decks:
            print(f"no deck at tools/demo_copy/{args.trade}.py", file=sys.stderr)
            sys.exit(1)

    problems = 0
    for trade in decks:
        deck = importlib.import_module(f"demo_copy.{trade}")
        print(f"[{trade}]")
        names = set()
        for filename, spec in deck.PAGES.items():
            status, applied = build_page(deck, filename, spec, trade, args.check)
            bad = "SOURCE BRANDING" in status
            print(f"  {'!' if bad else ' '} {filename:<24} {spec['firm']:<30} {applied:>3} applied  {status}")
            names.add(spec["firm"])
            problems += bad
        if len(names) != len(deck.PAGES):
            print(f"  ! only {len(names)} distinct firms across {len(deck.PAGES)} pages")
            problems += 1
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
