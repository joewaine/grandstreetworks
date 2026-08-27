#!/usr/bin/env python3
"""Put a photograph behind a build's hero copy.

Fourteen builds already open on a photograph with a scrim in their own ink
colour; the rest open on flat colour and meet their first photograph a screen
down. For a trade whose buying decision is almost entirely visual — interiors,
estates — that is the wrong order: the visitor should see the work before they
read the claim.

This adds the same structure the existing backdrop builds use — a
`.gsw-backdrop` inside the hero section, a scrim over it in the build's own ink,
and the hero's own children lifted above it — to a build that was built flat.
The scrim follows the Green Circle rule already used in `build-demo-copy.py`:
the copy side is opaque enough to hold on its own and thins toward the side the
text does not reach, so legibility never depends on the photograph.

    python3 tools/add-hero-backdrop.py interior-design
    python3 tools/add-hero-backdrop.py interior-design --replace
"""

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
WORK = REPO / "work"
MARKER = "<!-- gsw:backdrop -->"
END_MARKER = "<!-- /gsw:backdrop -->"
AVIF_WIDTHS = (1280, 2560)
JPEG_WIDTH = 1280

# build slug -> (plate stem, scrim rgb, "left" | "centre")
# `side` says where the copy sits, which is the side the scrim stays opaque on.
# The scrim colour must be the build's *ground*, not its ink: a light build with
# dark copy needs a light scrim. Getting this backwards puts grey text on a grey
# photograph, which is what happened to Brightfold first time round.
BACKDROPS = {
    "solar": {
        # D4 opened on a wall of white beside the incentive sheet.
        "brightfold-solar": ("e-street-of-roofs", "250 250 248", "left"),
    },
    "interior-design": {
        "ivory-lane-interiors": ("a-rooms-like-people", "92 44 28", "left"),
        "nocturne-interiors": ("f-after-dark", "18 20 22", "left"),
        # The terrazzo speckle field ran straight under the headline.
        "sorrel-studio": ("e-the-whole-room", "31 41 34", "left"),
    },
}


def scrim(rgb: str, side: str) -> str:
    if side == "centre":
        return f"rgb({rgb} / 0.78)"
    return (f"linear-gradient(100deg, rgb({rgb} / 0.96) 0%, rgb({rgb} / 0.92) 42%, "
            f"rgb({rgb} / 0.70) 72%, rgb({rgb} / 0.48) 100%)")


def css(rgb: str, side: str) -> str:
    return f"""
<style>
  /* gsw:backdrop — the hero opens on the work. The scrim is this build's own
     ink, heavy where the copy sits and thinning away from it, so the text
     never depends on what the photograph happens to be doing. */
  .gsw-imaged {{ position: relative; isolation: isolate; overflow: hidden; }}
  .gsw-imaged > *:not(.gsw-backdrop) {{ position: relative; z-index: 1; }}
  .gsw-backdrop {{ position: absolute; inset: 0; z-index: 0; }}
  .gsw-backdrop picture {{ display: block; width: 100%; height: 100%; }}
  .gsw-backdrop img {{ width: 100%; height: 100%; object-fit: cover;
                       object-position: center; }}
  .gsw-backdrop::after {{ content: ""; position: absolute; inset: 0;
                          background: {scrim(rgb, side)}; }}
  /* Below the breakpoint the copy spans the full width, so the scrim goes flat. */
  @media (max-width: 760px) {{
    .gsw-backdrop::after {{ background: rgb({rgb} / 0.9); }}
  }}
</style>"""


def picture(trade: str, stem: str) -> str:
    base = f"../_assets/hero/{trade}/{stem}"
    srcset = ", ".join(f"{base}-{w}.avif {w}w" for w in AVIF_WIDTHS)
    return (f'<div class="gsw-backdrop" aria-hidden="true"><picture>'
            f'<source type="image/avif" srcset="{srcset}" sizes="100vw">'
            f'<img src="{base}-{JPEG_WIDTH}.jpg" width="2560" height="1429" alt="" '
            f'loading="eager" fetchpriority="high" decoding="async">'
            f'</picture></div>')


def patch(page: Path, trade: str, spec, replace: bool) -> str:
    stem, rgb, side = spec
    src = page.read_text()
    if MARKER in src:
        if not replace:
            return "already has a backdrop"
        src = re.sub(re.escape(MARKER) + r".*?" + re.escape(END_MARKER), "", src, flags=re.S)
        src = re.sub(r"\n<style>\n  /\* gsw:backdrop.*?</style>", "", src, flags=re.S)
        src = src.replace('<section class="gsw-imaged ', '<section class="', 1)

    if not (WORK / "_assets" / "hero" / trade / f"{stem}-{JPEG_WIDTH}.jpg").exists():
        return f"missing encoded plate: {stem}"

    # The hero is the first top-level section, whatever the design calls it.
    m = re.search(r'<section class="((?:(?!gsw-imaged)[^"])*)"([^>]*)>', src)
    if not m:
        return "no opening section found"
    src = (src[:m.start()]
           + f'<section class="gsw-imaged {m.group(1)}"{m.group(2)}>'
           + MARKER + picture(trade, stem) + END_MARKER
           + src[m.end():])
    src = src.replace("</head>", css(rgb, side) + "\n</head>", 1)
    page.write_text(src)
    return f"backdrop added ({stem})"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("trades", nargs="+")
    ap.add_argument("--replace", action="store_true")
    args = ap.parse_args()

    for trade in args.trades:
        builds = BACKDROPS.get(trade)
        if not builds:
            print(f"  {trade}: no backdrops defined")
            continue
        for slug, spec in builds.items():
            page = WORK / trade / f"{slug}.html"
            status = patch(page, trade, spec, args.replace) if page.exists() else "page missing"
            print(f"  {slug:<34} {status}")


if __name__ == "__main__":
    main()
