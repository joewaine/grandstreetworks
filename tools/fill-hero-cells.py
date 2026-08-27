#!/usr/bin/env python3
"""Put real photographs in the hero's CSS placeholder cells.

Several designs draw a small index of case plates beside or under the headline
— Wyeth's four `.cell`s, Marchetti's three `.fr`s — as CSS gradients standing
in for photographs. On a page whose whole argument is "look through the cases",
an empty beige rectangle numbered 01 is the one thing on screen that says
nothing is behind it.

Each build already has its own library set from the per-build pass, so the
cells are filled from that: the image goes in as a `<picture>` inside the
existing cell, the cell keeps its own border, aspect-ratio and number, and the
gradient stays underneath as the loading colour.

    python3 tools/fill-hero-cells.py plastic-surgeons
    python3 tools/fill-hero-cells.py plastic-surgeons --replace

Run after build-responsive-images.py --kind library.
"""

import argparse
import html
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
WORK = REPO / "work"
MARKER = "gsw-cellfill"
AVIF_WIDTHS = (640, 1280)
JPEG_WIDTH = 720

# build slug -> spec. Two shapes:
#   ("class", cls, [(image, alt), ...])       cells are <div class="cls" data-n="NN">
#   ("child", parent_cls, {index: (image, alt)})  cells are the parent's children,
#     filled by position; an index left out keeps the design's own colour block,
#     which is what makes a nine-square feed read as curated rather than uniform.
CELLS = {
    "plastic-surgeons": {
        "wyeth-plastic-surgery": ("class", "cell", [
            ("operating-suite", "The operating suite"),
            ("imaging-room", "Imaging before surgery"),
            ("recovery-room", "A private recovery room"),
            ("consult-room", "The consultation room"),
        ]),
        "marchetti-plastic-surgery": ("class", "fr", [
            ("imaging-room", "Imaging before surgery"),
            ("operating-suite", "The operating suite"),
            ("recovery-room", "A private recovery room"),
        ]),
    },
    "med-spas": {
        "onyx-and-ivory-aesthetics": ("child", "lattice", {
            0: ("treatment-room", "A treatment room"),
            2: ("flatlay", "Set out for the appointment"),
            3: ("injector-hands", "Drawn up in front of you"),
            5: ("lounge", "The lounge"),
            6: ("towel-detail", "Ready for the next appointment"),
            8: ("evening-window", "An evening appointment"),
        }),
    },
}

CSS = f"""
<style>
  /* {MARKER}: photographs in the hero's index cells. The cell keeps its own
     border, ratio and number; the image sits behind them and the design's
     gradient stays as the loading colour. */
  .{MARKER} {{ position: absolute; inset: 0; display: block; }}
  /* The overlay needs a positioned parent; several of these cells have none. */
  .{MARKER}-host {{ position: relative; overflow: hidden; }}
  .{MARKER} img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
</style>"""


def picture(trade: str, slug: str, name: str, alt: str) -> str:
    base = f"../_assets/library/{trade}/{slug}/{name}"
    srcset = ", ".join(f"{base}-{w}.avif {w}w" for w in AVIF_WIDTHS)
    return (f'<span class="{MARKER}"><picture>'
            f'<source type="image/avif" srcset="{srcset}" sizes="(max-width: 760px) 45vw, 22vw">'
            f'<img src="{base}-{JPEG_WIDTH}.jpg" alt="{html.escape(alt, quote=True)}" '
            f'loading="lazy" decoding="async">'
            f'</picture></span>')


def patch(page: Path, trade: str, slug: str, spec, replace: bool) -> str:
    src = page.read_text()
    if MARKER in src:
        if not replace:
            return "cells already filled"
        src = re.sub(rf'<span class="{MARKER}">.*?</span>', "", src, flags=re.S)
        src = re.sub(rf"\n<style>\n  /\* {MARKER}:.*?</style>", "", src, flags=re.S)

    mode, target, images = spec
    wanted = [n for n, _ in (images if mode == "class" else images.values())]
    missing = [n for n in wanted
               if not (WORK / "_assets" / "library" / trade / slug /
                       f"{n}-{JPEG_WIDTH}.jpg").exists()]
    if missing:
        return f"missing encoded images: {', '.join(missing)}"

    counter = {"i": 0}

    if mode == "class":
        cell_re = re.compile(rf'(<div class="{target}" data-n="\d+"[^>]*>)(.*?)(</div>)', re.S)
        if not cell_re.search(src):
            return f"no .{target} cells found"

        def fill(m: re.Match) -> str:
            i = counter["i"]
            counter["i"] += 1
            if i >= len(images):
                return m.group(0)
            name, alt = images[i]
            opener = m.group(1).replace('<div class="', f'<div class="{MARKER}-host ', 1)
            return opener + m.group(2) + picture(trade, slug, name, alt) + m.group(3)

        src = cell_re.sub(fill, src)
        filled = min(counter["i"], len(images))
    else:
        # The parent's direct children, in order; only the named indices filled.
        open_m = re.search(rf'<div class="{target}"[^>]*>', src)
        if not open_m:
            return f"no .{target} found"
        depth, end = 0, open_m.start()
        for m in re.finditer(r"<div\b|</div>", src[open_m.start():]):
            end = open_m.start() + m.end()
            depth += 1 if m.group(0).startswith("<div") else -1
            if depth == 0:
                break
        parent = type("P", (), {"start": lambda self, g: open_m.end(),
                                "end": lambda self, g: end - len("</div>"),
                                "group": lambda self, g: src[open_m.end():end - len("</div>")]})()
        if not parent:
            return f"no .{target} found"
        inner = parent.group(2)
        child_re = re.compile(r"(<div[^>]*>)(</div>)")

        def fill_child(m: re.Match) -> str:
            i = counter["i"]
            counter["i"] += 1
            if i not in images:
                return m.group(0)
            name, alt = images[i]
            opener = m.group(1)
            opener = (opener.replace('<div class="', f'<div class="{MARKER}-host ', 1)
                      if 'class="' in opener else f'<div class="{MARKER}-host"')
            return opener + picture(trade, slug, name, alt) + m.group(2)

        new_inner = child_re.sub(fill_child, inner)
        if new_inner == inner:
            return f"no empty children in .{target}"
        src = src[:parent.start(2)] + new_inner + src[parent.end(2):]
        filled = sum(1 for i in images if i < counter["i"])

    src = src.replace("</head>", CSS + "\n</head>", 1)
    page.write_text(src)
    return f"filled {filled} cells"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("trades", nargs="+")
    ap.add_argument("--replace", action="store_true")
    args = ap.parse_args()

    for trade in args.trades:
        spec = CELLS.get(trade)
        if not spec:
            print(f"  {trade}: no cells defined")
            continue
        for slug, build_spec in spec.items():
            page = WORK / trade / f"{slug}.html"
            status = patch(page, trade, slug, build_spec, args.replace) \
                if page.exists() else "page missing"
            print(f"  {slug:<34} {status}")


if __name__ == "__main__":
    main()
