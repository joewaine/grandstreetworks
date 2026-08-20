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
import json
import html
import importlib
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hero_backdrops import wants_backdrop

REPO = Path(__file__).resolve().parent.parent
WORK = REPO / "work"
SOURCE = Path.home() / "fractal" / "cash_rich" / "demos"
NOINDEX = '<meta name="robots" content="noindex">\n'
CHARSET = '<meta charset="utf-8">\n'



def slugify(name):
    """A business name as a URL segment: 'Fair Oaks Roofing' -> fair-oaks-roofing."""
    s = name.lower().replace("&", "and")
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def trade_dir(source_slug):
    """Published directory for a trade: '06-roofing' -> 'roofing'."""
    return re.sub(r"^\d+-", "", source_slug)

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



HERO_DIR = REPO / "work" / "_assets" / "hero"


def first_section_end(page):
    """Index just past the first top-level <section>'s closing tag.

    Every design opens with its hero as the first section in the body — most
    call it .hero, a few call it .band — so this is the one structural hook
    that holds across all 114 pages. Depth-counted, because a couple of heroes
    nest a section inside themselves.
    """
    start = page.find("<section")
    if start == -1:
        return -1
    depth, i = 0, start
    for m in re.finditer(r"<section\b|</section>", page[start:]):
        i = start + m.end()
        depth += 1 if m.group(0).startswith("<section") else -1
        if depth == 0:
            return i
    return -1


def plate_alt(filename, trade):
    """Alt text from the plate's own name: 'a-storm-clearing' -> the phrase."""
    stem = Path(filename).stem
    words = stem.split("-", 1)[1].replace("-", " ") if "-" in stem else stem
    return f"{words[0].upper()}{words[1:]} — {trade.replace('-', ' ')}"


PLATE_CSS = """
<style>
  /* Hero plate, added with the photography pass. Full-bleed between the hero
     and the first content section, with no border of its own: every one of
     these designs owns a different rule weight and ink colour, and a borrowed
     hairline reads as a mistake in about half of them. */
  .gsw-plate { margin: 0; display: block; width: 100%; overflow: hidden; }
  .gsw-plate img {
    display: block;
    width: 100%;
    height: clamp(220px, 40vw, 520px);
    object-fit: cover;
    object-position: center;
  }
  @media (max-width: 640px) { .gsw-plate img { height: clamp(180px, 52vw, 300px); } }
</style>
"""


def add_hero_plate(page, trade, index):
    """Drop one photographic plate in under the hero."""
    plates = sorted(q.name for q in (HERO_DIR / trade).glob("*.jpg"))
    if not plates:
        return page, "no plates for this trade"
    name = plates[index % len(plates)]
    cut = first_section_end(page)
    if cut == -1:
        return page, "no <section> to place the plate after"
    fig = (f'\n<figure class="gsw-plate">'
           f'<img src="../_assets/hero/{trade}/{name}" '
           f'alt="{html.escape(plate_alt(name, trade), quote=True)}" loading="lazy">'
           f'</figure>\n')
    page = page[:cut] + fig + page[cut:]
    if "gsw-plate" not in page.split("</head>")[0]:
        page = page.replace("</head>", PLATE_CSS + "</head>", 1)
    return page, None



HERO_COLORS = json.loads((REPO / "tools" / "hero_colors.json").read_text()) \
    if (REPO / "tools" / "hero_colors.json").exists() else {}


def _luminance(rgb):
    vals = [int(v) / 255 for v in re.findall(r"\d+", rgb)[:3]]
    lin = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in vals]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def scrim_css(rgb):
    """A scrim in the design's own hero colour, following the Green Circle rule.

    Legibility must not depend on the photograph: the copy side is opaque enough
    to hold on its own, thinning toward the side the text does not reach, and
    flat below the breakpoint where the copy spans the full width.

    Dark heroes get a lighter ramp. A near-black scrim at .97 erases the
    photograph completely — the pool build was a black rectangle — and light
    type over a dark image needs far less help than dark type over a bright one.
    """
    c = " ".join(re.findall(r"\d+", rgb)[:3])
    dark = _luminance(rgb) < 0.18
    a = (0.90, 0.84, 0.56, 0.36) if dark else (0.97, 0.95, 0.70, 0.52)
    flat = 0.86 if dark else 0.93
    return f"""  .gsw-backdrop::after {{
    content: ""; position: absolute; inset: 0;
    background: linear-gradient(100deg,
      rgb({c} / {a[0]}) 0%, rgb({c} / {a[1]}) 38%, rgb({c} / {a[2]}) 68%, rgb({c} / {a[3]}) 100%);
  }}
  @media (max-width: 60rem) {{ .gsw-backdrop::after {{ background: rgb({c} / {flat}); }} }}"""


BACKDROP_CSS = """
<style>
  /* Hero backdrop. The photograph sits behind the hero's own composition; the
     scrim below is the design's own background colour, so nothing about the
     contrast the layout was built with changes. */
  .gsw-imaged {{ position: relative; isolation: isolate; overflow: hidden; }}
  .gsw-imaged > *:not(.gsw-backdrop) {{ position: relative; z-index: 1; }}
  .gsw-backdrop {{ position: absolute; inset: 0; z-index: 0; }}
  .gsw-backdrop img {{ width: 100%; height: 100%; object-fit: cover; object-position: center; }}
{scrim}
  @media (forced-colors: active) {{ .gsw-backdrop {{ display: none; }} }}
  @media print {{ .gsw-backdrop {{ display: none; }} }}
</style>
"""


def add_hero_backdrop(page, trade, index, filename):
    """Put the plate behind the hero instead of under it."""
    reading = HERO_COLORS.get(f"{trade}/{filename}")
    if not reading:
        return page, f"no measured hero colour for {filename}"
    plates = sorted(q.name for q in (HERO_DIR / trade).glob("*.jpg"))
    if not plates:
        return page, "no plates for this trade"
    name = plates[index % len(plates)]

    m = re.search(r"<section\b[^>]*>", page)
    if not m:
        return page, "no <section> to make the backdrop hero"
    tag = m.group(0)
    if 'class="' in tag:
        new_tag = tag.replace('class="', 'class="gsw-imaged ', 1)
    else:
        new_tag = tag[:-1] + ' class="gsw-imaged">'
    backdrop = (f'<div class="gsw-backdrop" aria-hidden="true">'
                f'<img src="../_assets/hero/{trade}/{name}" alt="" loading="eager"></div>')
    page = page[:m.start()] + new_tag + backdrop + page[m.end():]
    page = page.replace("</head>",
                        BACKDROP_CSS.format(scrim=scrim_css(reading["bg"])) + "</head>", 1)
    return page, None


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

    # Testimonials tend to drop the suffix and say just "Halcyon" or
    # "Ridgeline". Sweep the bare head word last, after every deliberate
    # replacement has had its chance, so a deck can still rewrite the quote
    # properly when it wants to.
    head = deck.SOURCE_FIRM.split()[0]
    if head in s:
        s = s.replace(head, spec["firm"].split()[0])

    td = trade_dir(trade)
    out_name = f"{slugify(spec['firm'])}.html"
    if wants_backdrop(td, spec["_index"]):
        s, note = add_hero_backdrop(s, td, spec["_index"], out_name)
    else:
        s, note = add_hero_plate(s, td, spec["_index"])
    if note:
        notes.append(note)

    if 'name="robots"' not in s and CHARSET in s:
        s = s.replace(CHARSET, CHARSET + NOINDEX, 1)

    stale = [w for w in deck.FORBIDDEN if w in s]
    if stale:
        notes.append(f"SOURCE BRANDING LEFT: {stale}")
    if missed:
        notes.append(f"{len(missed)} keys n/a: {missed[:2]}")

    if not check:
        out = WORK / trade_dir(trade) / f"{slugify(spec['firm'])}.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(s)
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
        for i, (filename, spec) in enumerate(deck.PAGES.items()):
            spec["_index"] = i
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
