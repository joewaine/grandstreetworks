#!/usr/bin/env python3
"""Move a build's photograph up beside its hero copy, as a second column.

Most builds put their plate full-bleed *under* the hero. That works when the
hero is a wide composition, and reads as an empty fold when the hero is a
narrow card — Willowbank's whole first screen is one status panel, and the
photograph sat below it where nobody scrolling for "do they take new patients"
would look.

This turns the named panel into two columns: the copy it already had on the
left, the photograph on the right. The build's own card keeps its border,
radius, shadow and overflow clipping, so the image is cropped by the card
rather than sitting in a box of its own. The status rail stays full width
across the top, because it is the device the whole design is built around.

The standalone plate is removed in the same pass — the same photograph twice on
one page is worse than either placement alone.

    python3 tools/build-hero-split.py veterinary
    python3 tools/build-hero-split.py veterinary --replace

Run build-responsive-images.py for the trade first; this points at that ladder.
"""

import argparse
import html
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
WORK = REPO / "work"
MARKER = "<!-- gsw:herosplit -->"
END_MARKER = "<!-- /gsw:herosplit -->"

AVIF_WIDTHS = (1280, 2560)
JPEG_WIDTH = 1280

SETS = {
    "veterinary": {
        "willowbank-animal-hospital": {
            # The green status rail is D1's device; it stays full width and the
            # split happens beneath it.
            "full_width_lead": "rail",
            "image": "veterinary/a-taking-new-patients",
            "alt": "The waiting room at Willowbank Animal Hospital",
        },
    },
}

CSS = """
<style>
  /* Hero split. The photograph becomes the panel's right-hand column instead of
     a full-bleed band below the fold. Everything is scoped to .gsw-hs so the
     build's own .panel, .pbody and .badges rules keep working untouched. */
  .gsw-hs-media { margin: 0; }
  .gsw-hs-media img { display: block; width: 100%;
                      height: clamp(200px, 52vw, 300px); object-fit: cover; }
  @media (min-width: 60rem) {
    .gsw-hs { display: grid; grid-template-columns: 1.02fr 0.98fr;
              align-items: stretch; }
    .gsw-hs-copy { display: flex; flex-direction: column; padding-bottom: 20px; }
    /* The panel's own bottom padding becomes the copy column's job, or the
       photograph stops short of the card's bottom edge. */
    .gsw-hs-panel { padding-bottom: 0; }
    .gsw-hs-media { position: relative; border-left: 2px solid var(--ink); }
    .gsw-hs-media img { position: absolute; inset: 0; height: 100%; }
  }
</style>"""


def picture(spec: dict) -> str:
    base = f"../_assets/hero/{spec['image']}"
    srcset = ", ".join(f"{base}-{w}.avif {w}w" for w in AVIF_WIDTHS)
    return (f'<picture><source type="image/avif" srcset="{srcset}" '
            f'sizes="(max-width: 60rem) 100vw, 50vw">'
            f'<img src="{base}-{JPEG_WIDTH}.jpg" width="1600" height="893" '
            f'alt="{html.escape(spec["alt"])}" loading="eager" '
            f'fetchpriority="high" decoding="async"></picture>')


def close_of(src: str, start: int) -> int:
    """Index just past the </div> that closes the tag opening at `start`."""
    depth = 0
    for m in re.finditer(r"<div\b|</div>", src[start:]):
        depth += 1 if m.group(0) != "</div>" else -1
        if depth == 0:
            return start + m.end()
    raise ValueError("unbalanced panel")


def patch(page: Path, spec: dict, replace: bool) -> str:
    src = page.read_text()
    if MARKER in src:
        if not replace:
            return "already split"
        return "already split (--replace not supported; revert the file first)"

    m = re.search(r'<div class="panel"[^>]*>', src)
    if not m:
        return "no .panel to split"
    end = close_of(src, m.start())
    inner = src[m.end():end - len("</div>")]

    lead = re.match(r'\s*<div class="%s"[^>]*>.*?</div>' % spec["full_width_lead"],
                    inner, re.S)
    if not lead:
        return f"no leading .{spec['full_width_lead']} inside the panel"

    rest = inner[lead.end():]
    rebuilt = (
        f'{MARKER}<div class="panel gsw-hs-panel">{lead.group(0)}'
        f'<div class="gsw-hs"><div class="gsw-hs-copy">{rest}</div>'
        f'<figure class="gsw-hs-media">{picture(spec)}</figure>'
        f'</div></div>{END_MARKER}')
    src = src[:m.start()] + rebuilt + src[end:]

    # The same photograph twice on one page is worse than either placement.
    src, dropped = re.subn(r'<figure class="gsw-plate">.*?</figure>\s*', "", src,
                           flags=re.S)
    if dropped:
        # Its injected stylesheet has no consumer left on this page.
        src = re.sub(r"\n<style>\n  /\* Hero plate, added with the photography"
                     r" pass\..*?</style>", "", src, flags=re.S)
    src = src.replace("</head>", CSS + "\n</head>", 1)
    page.write_text(src)
    return f"split into two columns ({dropped} full-bleed plate removed)"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("trades", nargs="+")
    ap.add_argument("--replace", action="store_true")
    args = ap.parse_args()

    for trade in args.trades:
        sets = SETS.get(trade)
        if not sets:
            print(f"  {trade}: no hero-split specs")
            continue
        for slug, spec in sets.items():
            page = WORK / trade / f"{slug}.html"
            if not page.exists():
                print(f"  {slug:<34} page missing")
                continue
            ladder = WORK / "_assets" / "hero" / f"{spec['image']}-{JPEG_WIDTH}.jpg"
            if not ladder.exists():
                sys.exit(f"no encoded ladder for {spec['image']}; "
                         f"run build-responsive-images.py {trade} first")
            print(f"  {slug:<34} {patch(page, spec, args.replace)}")


if __name__ == "__main__":
    main()
