#!/usr/bin/env python3
"""Add a recent-work gallery — before/after plus process detail — to each build.

Sixteen of the 120 builds talk about before-and-after in copy while showing
nothing, and every build ships exactly one photograph. This injects the band the
copy already promises, immediately above each build's closing CTA.

The band has to sit inside six unrelated designs without looking bolted on, so
it borrows rather than declares:

  * colour comes from the custom properties every build defines anyway
    (--ink, --surface, --accent, --muted, --rule, --wrap), which means the dark
    build gets a dark band with no special case;
  * type comes from using a real <h2> and <p>, so each build's own display face
    and heading ramp apply with nothing hardcoded;
  * the image set differs per build, so six galleries in one trade index do not
    read as the same six photographs six times.

    python3 tools/build-gallery.py roofing
    python3 tools/build-gallery.py roofing --replace

Run build-responsive-images.py --kind library first; this points at that ladder.
"""

import argparse
import html
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
WORK = REPO / "work"
MARKER = "<!-- gsw:gallery -->"
END_MARKER = "<!-- /gsw:gallery -->"

AVIF_WIDTHS = (640, 1280)
JPEG_WIDTH = 720

# name -> (caption, aspect)
CAPTIONS = {
    "roofing": {
        "tear-off": ("Tear-off, down to the deck", "4:3"),
        "underlayment": ("Synthetic underlayment", "4:3"),
        "courses": ("New courses going on", "4:3"),
        "ridge-vent": ("Ridge vent and cap", "4:3"),
        "flashing": ("Step flashing at the chimney", "4:3"),
        "drip-edge": ("Drip edge and gutter", "4:3"),
        "jobsite": ("Site protected, drive clear", "4:3"),
        "finished-home": ("Finished, from the kerb", "16:9"),
        "damage-before": ("Before", "4:3"),
        "damage-after": ("After", "4:3"),
    },
}

# Each build shows a different three, so a trade index scrolling six builds does
# not show the same gallery six times.
SETS = {
    "roofing": {
        "halloran-roofing": {
            "label": "Recent work", "heading": "The storm week, start to finish.",
            "note": "One street, one week: the call that came in at nine, and the roof that "
                    "was finished before the next front arrived.",
            "tiles": ["tear-off", "jobsite", "finished-home"]},
        "fair-oaks-roofing": {
            "label": "On your street", "heading": "Four houses, same postcode.",
            "note": "Every one of these is a house someone can drive past. Ask them what "
                    "the week was like — that is the only reference that counts.",
            "tiles": ["finished-home", "drip-edge", "courses"]},
        "meridian-roof-co": {
            "label": "Recent work", "heading": "What 2,400 roofs looks like up close.",
            "note": "The same sequence on every job, whether it is a repair or a full "
                    "replacement. Six crews, one standard.",
            "tiles": ["courses", "ridge-vent", "jobsite"]},
        "anchor-peak-roofing": {
            "label": "On the job", "heading": "Tarped, stripped, replaced.",
            "note": "Emergency work does not mean rough work. The same details get done "
                    "at two in the morning as at two in the afternoon.",
            "tiles": ["tear-off", "underlayment", "flashing"]},
        "sentry-roofing-and-restoration": {
            "label": "Documented", "heading": "Photographed for the adjuster.",
            "note": "Every job is documented the way a claim needs it — before, during "
                    "and after, with the detail shots the adjuster will ask for.",
            "tiles": ["flashing", "drip-edge", "ridge-vent"]},
        "northgate-roofing": {
            "label": "Dispatched", "heading": "From the call to the clear-up.",
            "note": "What happens after someone answers: a crew, a protected site, and "
                    "a driveway you can park on the same evening.",
            "tiles": ["jobsite", "underlayment", "tear-off"]},
    },
}

CSS = """
<style>
  /* Recent-work gallery. Everything here is drawn from the properties the build
     already declares, so the band inherits each design's palette and heading
     face rather than importing a seventh look. */
  .gsw-gal { background: var(--surface); color: var(--ink);
             padding: clamp(38px, 6vw, 74px) 0; }
  .gsw-gal-in { max-width: var(--wrap, 1140px); margin: 0 auto; padding: 0 20px; }
  .gsw-gal-lab { font-size: 13px; letter-spacing: .18em; text-transform: uppercase;
                 font-weight: 600; color: var(--accent); margin: 0 0 14px; }
  .gsw-gal h2 { margin: 0; }
  .gsw-gal-note { color: var(--muted); margin: 14px 0 30px; max-width: 58ch; }
  .gsw-ba { display: grid; grid-template-columns: 1fr 1fr; gap: 2px; margin-bottom: 2px; }
  .gsw-gal-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 2px; }
  .gsw-gal figure { margin: 0; position: relative; overflow: hidden;
                    background: var(--rule, rgba(0,0,0,.1)); }
  .gsw-gal picture { display: block; }
  /* height:auto matters — the width/height attributes are a presentational
     hint, and without this the 1200px hint beats aspect-ratio. */
  .gsw-gal img { display: block; width: 100%; height: auto; aspect-ratio: 4 / 3;
                 object-fit: cover; transition: transform .5s ease; }
  .gsw-gal figure:hover img { transform: scale(1.035); }
  .gsw-gal figcaption { position: absolute; left: 0; bottom: 0;
                        background: var(--ink); color: var(--surface);
                        font-size: 12px; font-weight: 600; letter-spacing: .14em;
                        text-transform: uppercase; padding: 7px 12px; }
  @media (max-width: 720px) {
    .gsw-ba, .gsw-gal-grid { grid-template-columns: 1fr; }
  }
  @media (prefers-reduced-motion: reduce) {
    .gsw-gal img { transition: none; }
    .gsw-gal figure:hover img { transform: none; }
  }
</style>"""


def picture(trade: str, name: str, caption: str, sizes: str, aspect: str) -> str:
    base = f"../_assets/library/{trade}/{name}"
    srcset = ", ".join(f"{base}-{w}.avif {w}w" for w in AVIF_WIDTHS)
    w, h = (1600, 1200) if aspect == "4:3" else (1600, 900)
    return (
        f'<figure><picture>'
        f'<source type="image/avif" srcset="{srcset}" sizes="{sizes}">'
        f'<img src="{base}-{JPEG_WIDTH}.jpg" width="{w}" height="{h}" '
        f'alt="{html.escape(caption)}" loading="lazy" decoding="async">'
        f'</picture><figcaption>{html.escape(caption)}</figcaption></figure>')


def section(trade: str, spec: dict) -> str:
    caps = CAPTIONS[trade]
    ba = "".join(
        picture(trade, n, caps[n][0], "(max-width: 720px) 100vw, 50vw", caps[n][1])
        for n in ("damage-before", "damage-after"))
    tiles = "".join(
        picture(trade, n, caps[n][0], "(max-width: 720px) 100vw, 33vw", caps[n][1])
        for n in spec["tiles"])
    return (
        f'{MARKER}\n<section class="gsw-gal"><div class="gsw-gal-in">'
        f'<p class="gsw-gal-lab">{html.escape(spec["label"])}</p>'
        f'<h2>{html.escape(spec["heading"])}</h2>'
        f'<p class="gsw-gal-note">{html.escape(spec["note"])}</p>'
        f'<div class="gsw-ba">{ba}</div>'
        f'<div class="gsw-gal-grid">{tiles}</div>'
        f'</div></section>\n{END_MARKER}\n')


def patch(page: Path, trade: str, spec: dict, replace: bool) -> str:
    src = page.read_text()
    if MARKER in src:
        if not replace:
            return "already has a gallery"
        src = re.sub(re.escape(MARKER) + r".*?" + re.escape(END_MARKER) + r"\n?",
                     "", src, flags=re.S)
        src = re.sub(r"\n<style>\n  /\* Recent-work gallery.*?</style>", "",
                     src, flags=re.S)

    if '<section class="close"' not in src:
        return "no closing section to sit above"
    src = src.replace("</head>", CSS + "\n</head>", 1)
    src = src.replace('<section class="close"',
                      section(trade, spec) + '<section class="close"', 1)
    page.write_text(src)
    return "gallery added"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("trades", nargs="+")
    ap.add_argument("--replace", action="store_true",
                    help="regenerate a gallery that is already present")
    args = ap.parse_args()

    for trade in args.trades:
        sets = SETS.get(trade)
        if not sets:
            print(f"  {trade}: no gallery sets defined")
            continue
        missing = [n for n in CAPTIONS[trade]
                   if not (WORK / "_assets" / "library" / trade /
                           f"{n}-{JPEG_WIDTH}.jpg").exists()]
        if missing:
            sys.exit(f"missing encoded library images: {', '.join(missing)}")
        for slug, spec in sets.items():
            page = WORK / trade / f"{slug}.html"
            status = patch(page, trade, spec, args.replace) if page.exists() \
                else "page missing"
            print(f"  {slug:<34} {status}")


if __name__ == "__main__":
    main()
