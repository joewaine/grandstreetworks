#!/usr/bin/env python3
"""Rewrite the single-JPEG hero tags in the builds into a responsive <picture>.

Pairs with build-responsive-images.py, which produces the ladder this points at.
Two shapes exist in the builds and both are handled:

    <figure class="gsw-plate"><img src="...jpg" alt="..." loading="lazy"></figure>
    <div class="gsw-backdrop" aria-hidden="true"><img src="...jpg" alt="" loading="eager"></div>

Idempotent: a build already carrying <picture> is left alone.

    python3 tools/wire-responsive-images.py roofing
    python3 tools/wire-responsive-images.py --all
"""

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
WORK = REPO / "work"
ASSETS = WORK / "_assets" / "hero"

AVIF_WIDTHS = (1280, 2560)
JPEG_WIDTH = 1280
# The plates are a uniform 16:9-ish crop out of the generator.
INTRINSIC_W, INTRINSIC_H = 2560, 1429

IMG_RE = re.compile(
    r'<img\s+src="(?P<src>\.\./_assets/hero/[^"]+?)\.jpg"'
    r'(?P<rest>[^>]*)>')

# The figure/div wrappers are block; <picture> defaults to inline, which would
# leave a text-baseline gap under a full-bleed plate.
PICTURE_CSS = """  .gsw-plate picture { display: block; width: 100%; }
  .gsw-backdrop picture { display: block; width: 100%; height: 100%; }
"""


def build_picture(src_base: str, rest: str) -> str:
    """rest carries the original alt/loading attributes; they belong on the img."""
    srcset = ", ".join(f"{src_base}-{w}.avif {w}w" for w in AVIF_WIDTHS)
    eager = 'loading="eager"' in rest
    attrs = rest.strip()
    # An eagerly-loaded backdrop is the LCP element on those pages; say so.
    if eager and "fetchpriority" not in attrs:
        attrs += ' fetchpriority="high"'
    if "decoding=" not in attrs:
        attrs += ' decoding="async"'
    return (
        "<picture>"
        f'<source type="image/avif" srcset="{srcset}" sizes="100vw">'
        f'<img src="{src_base}-{JPEG_WIDTH}.jpg" '
        f'width="{INTRINSIC_W}" height="{INTRINSIC_H}" {attrs}>'
        "</picture>"
    )


def ladder_exists(src_base: str, page: Path) -> bool:
    resolved = (page.parent / f"{src_base}-{JPEG_WIDTH}.jpg").resolve()
    return resolved.exists()


def process(page: Path) -> str:
    html = page.read_text()
    # The compare slider and the gallery band also use <picture>; only the
    # plate's own CSS proves the plate itself has been wired.
    if ".gsw-plate picture" in html:
        return "already wired"

    missing: list[str] = []

    def repl(m: re.Match) -> str:
        src_base = m.group("src")
        if not ladder_exists(src_base, page):
            missing.append(src_base)
            return m.group(0)
        return build_picture(src_base, m.group("rest"))

    new, n = IMG_RE.subn(repl, html)
    if missing:
        return f"no ladder for {missing[0]} — run build-responsive-images.py first"
    if not n:
        return "no hero image found"

    if ".gsw-plate picture" not in new:
        # Anchor the rule to whichever wrapper rule this build carries.
        for anchor in ("  .gsw-plate { margin: 0;", "  .gsw-imaged { position: relative;"):
            if anchor in new:
                new = new.replace(anchor, PICTURE_CSS + anchor, 1)
                break

    page.write_text(new)
    return f"wired {n} image{'s' if n != 1 else ''}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("trades", nargs="*")
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()

    if args.all:
        trades = sorted(p.name for p in WORK.iterdir()
                        if p.is_dir() and p.name != "_assets")
    elif args.trades:
        trades = args.trades
    else:
        sys.exit("name at least one trade, or pass --all")

    for trade in trades:
        for page in sorted((WORK / trade).glob("*.html")):
            if page.name == "index.html":
                continue
            print(f"  {trade}/{page.name:<40} {process(page)}")


if __name__ == "__main__":
    main()
