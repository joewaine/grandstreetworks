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
#   ("fld", parent_cls, [(image, alt), ...])  cells are the <span class="fld">
#     placeholders inside that container, in order — the shape the estate-agency
#     designs all use for their plate sets.
#   ("slides", (plate_cls, register_cls), [(image, alt), ...])  one plate with a
#     numbered register beneath it: becomes a real slideshow the register drives.
#   ("cover", cls, [(image, alt), ...])  each element with that class is itself
#     one plate, drawn in CSS; the photograph covers the drawing.
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
    "luxury-real-estate": {
        # The whole trade argues "six photographs is not enough", and every one
        # of these six designs drew its plate set in CSS.
        "rathmore-and-finch": ("fld", "plates", [
            ("entry-hall", "The entry"), ("kitchen", "Kitchen at twilight"),
            ("bathroom", "Principal bath"), ("pool-terrace", "Terrace and pool"),
            ("drone-estate", "The estate from above"), ("twilight-facade", "Twilight, from the drive"),
        ]),
        "ellery-and-vane": ("fld", "frames", [
            ("film-crew", "Filmed, not photographed"), ("entry-hall", "The entry"),
            ("pool-terrace", "Terrace and pool"), ("garden-path", "The garden"),
            ("kitchen", "Kitchen at twilight"), ("twilight-facade", "Twilight, from the drive"),
        ]),
        "marlowe-and-hart": ("fld", "frieze", [
            ("twilight-facade", "Twilight, from the drive"), ("threshold", "The threshold"),
            ("garden-path", "The garden"), ("drone-estate", "The estate from above"),
            ("entry-hall", "The entry"), ("library-room", "The study"),
        ]),
        "thornbury-property-group": ("fld", "wall", [
            ("drone-estate", "The estate from above"), ("kitchen", "Kitchen at twilight"),
            ("pool-terrace", "Terrace and pool"), ("entry-hall", "The entry"),
            ("film-crew", "Filmed, not photographed"), ("twilight-facade", "Twilight, from the drive"),
        ]),
        "ashcroft-residential": ("slides", ("plateone", "register"), [
            ("threshold", "The threshold"), ("entry-hall", "The entry"),
            ("library-room", "The study"), ("garden-path", "The garden"),
            ("bathroom", "Principal bath"), ("twilight-facade", "Twilight, from the drive"),
        ]),
        "bellamy-estates": ("fld", "gauge", [
            ("twilight-facade", "Twilight, from the drive"), ("entry-hall", "The entry"),
            ("kitchen", "Kitchen at twilight"), ("pool-terrace", "Terrace and pool"),
            ("library-room", "The study"), ("drone-estate", "The estate from above"),
        ]),
    },
    "custom-home-builders": {
        # "the portfolio is the product and it's underbuilt" — four numbered
        # plates drawn in CSS as the index.
        "kingsmere-build": ("cover", "pdraw", [
            ("exterior-evening", "Evening, from the drive"),
            ("interior-finish", "The great room, finished"),
            ("kitchen", "Kitchen, handed over"),
            ("house-finished", "Move-in"),
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
  /* Slideshow: the plates stack, the register switches them. Without
     JavaScript the first plate is simply the one that shows. */
  .{MARKER}-slide {{ position: absolute; inset: 0; opacity: 0; transition: opacity .45s ease; }}
  .{MARKER}-slide:first-of-type {{ opacity: 1; }}
  .{MARKER}-slide[data-on] {{ opacity: 1; }}
  .{MARKER}-live .{MARKER}-slide:first-of-type:not([data-on]) {{ opacity: 0; }}
  .{MARKER}-reg button {{ font: inherit; color: inherit; background: none; border: 0;
                          padding: 0; cursor: pointer; opacity: .45;
                          transition: opacity .2s ease; }}
  .{MARKER}-reg button[aria-current="true"] {{ opacity: 1; }}
  .{MARKER}-reg button:focus-visible {{ outline: 2px solid currentColor; outline-offset: 3px; }}
  @media (prefers-reduced-motion: reduce) {{
    .{MARKER}-slide {{ transition: none; }}
  }}
  .{MARKER} img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
  .gsw-sr {{ position: absolute; width: 1px; height: 1px; overflow: hidden;
             clip-path: inset(50%); white-space: nowrap; }}
</style>"""


SCRIPT = f"""
<script>
/* One slideshow per page. The register buttons drive `data-on`; the CSS does
   the rest, so a plate is visible before this runs and stays visible if it
   never does. */
(function () {{
  var reg = document.querySelector('.{MARKER}-reg');
  if (!reg) return;
  var slides = document.querySelectorAll('.{MARKER}-slide');
  var num = document.querySelector('.{MARKER}-num');
  if (!slides.length) return;
  document.documentElement.classList.add('{MARKER}-live');
  var show = function (i) {{
    slides.forEach(function (s, k) {{
      if (k === i) {{ s.setAttribute('data-on', ''); }} else {{ s.removeAttribute('data-on'); }}
    }});
    reg.querySelectorAll('button').forEach(function (b, k) {{
      b.setAttribute('aria-current', k === i ? 'true' : 'false');
    }});
    if (num) num.textContent = String(i + 1).padStart(2, '0');
  }};
  reg.querySelectorAll('button').forEach(function (b, k) {{
    b.addEventListener('click', function () {{ show(k); }});
  }});
  show(0);
}})();
</script>"""


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
        src = re.sub(rf'<span class="{MARKER}-slide">.*?</span></span>', "", src, flags=re.S)
        src = re.sub(rf'<span class="{MARKER}">.*?</span>', "", src, flags=re.S)
        src = src.replace(f'{MARKER}-reg ', "").replace(f'{MARKER}-host ', "")
        src = src.replace(f' {MARKER}-num', "")
        src = re.sub(r'<li><button type="button"[^>]*>(.*?)<span class="gsw-sr">.*?</span></button></li>',
                     r"<li>\1</li>", src, flags=re.S)
        src = re.sub(rf"\n<style>\n  /\* {MARKER}:.*?</style>", "", src, flags=re.S)
        src = re.sub(rf"\n<script>\n/\* One slideshow per page\..*?</script>", "", src, flags=re.S)

    mode, target, images = spec
    wanted = [n for n, _ in (images.values() if isinstance(images, dict) else images)]
    missing = [n for n in wanted
               if not (WORK / "_assets" / "library" / trade / slug /
                       f"{n}-{JPEG_WIDTH}.jpg").exists()]
    if missing:
        return f"missing encoded images: {', '.join(missing)}"

    counter = {"i": 0}

    if mode == "slides":
        plate_cls, reg_cls = target
        plate = re.search(rf'(<div class="{plate_cls}"[^>]*>)(.*?)(</div>)', src, re.S)
        reg = re.search(rf'(<ul class="{reg_cls}"[^>]*>)(.*?)(</ul>)', src, re.S)
        if not plate or not reg:
            return f"no .{plate_cls} / .{reg_cls} found"
        stack = "".join(
            f'<span class="{MARKER}-slide">' + picture(trade, slug, n, a) + "</span>"
            for n, a in images)
        # The slides go inside the plate's own frame, so its padding, border and
        # number stay outside the photograph.
        inner = plate.group(2).replace(
            '<span class="fld"></span>',
            f'<span class="fld {MARKER}-host">{stack}</span>', 1)
        inner = inner.replace('<span class="n">', f'<span class="n {MARKER}-num">', 1)
        new_plate = plate.group(1) + inner + plate.group(3)
        src = src[:plate.start()] + new_plate + src[plate.end():]

        reg = re.search(rf'(<ul class="{reg_cls}"[^>]*>)(.*?)(</ul>)', src, re.S)
        items = re.findall(r"<li[^>]*>(.*?)</li>", reg.group(2), re.S)
        new_items = "".join(
            f'<li><button type="button" aria-current="{"true" if i == 0 else "false"}">'
            f'{t}<span class="gsw-sr">, show plate {t}</span></button></li>'
            for i, t in enumerate(items))
        new_reg = (reg.group(1).replace('<ul class="', f'<ul class="{MARKER}-reg ', 1)
                   + new_items + reg.group(3))
        src = src[:reg.start()] + new_reg + src[reg.end():]
        # The register was decorative; it is now a control.
        src = src.replace('<div aria-hidden="true">\n    <div class="gsw-cellfill-host',
                          '<div>\n    <div class="gsw-cellfill-host', 1)
        src = src.replace("</body>", SCRIPT + "\n</body>", 1)
        filled = len(images)
    elif mode == "cover":
        cover_re = re.compile(rf'(<div class="{target}"[^>]*>)(.*?)(</div>)', re.S)
        if not cover_re.search(src):
            return f"no .{target} found"

        def fill_cover(m: re.Match) -> str:
            i = counter["i"]
            counter["i"] += 1
            if i >= len(images):
                return m.group(0)
            name, alt = images[i]
            opener = m.group(1).replace('<div class="', f'<div class="{MARKER}-host ', 1)
            return opener + m.group(2) + picture(trade, slug, name, alt) + m.group(3)

        src = cover_re.sub(fill_cover, src)
        filled = min(counter["i"], len(images))
    elif mode == "fld":
        open_m = re.search(rf'<(ul|div)[^>]*class="[^"]*\b{target}\b[^"]*"[^>]*>', src)
        if not open_m:
            return f"no .{target} found"
        tag = open_m.group(1)
        depth, end = 0, open_m.start()
        for m in re.finditer(rf"<{tag}\b|</{tag}>", src[open_m.start():]):
            end = open_m.start() + m.end()
            depth += 1 if not m.group(0).startswith("</") else -1
            if depth == 0:
                break
        inner = src[open_m.end():end - len(f"</{tag}>")]
        fld_re = re.compile(r'<span class="fld"></span>')

        def fill_fld(m: re.Match) -> str:
            i = counter["i"]
            counter["i"] += 1
            if i >= len(images):
                return m.group(0)
            name, alt = images[i]
            return (f'<span class="fld {MARKER}-host">'
                    + picture(trade, slug, name, alt) + "</span>")

        new_inner = fld_re.sub(fill_fld, inner)
        if new_inner == inner:
            return f"no .fld placeholders in .{target}"
        src = src[:open_m.end()] + new_inner + src[end - len(f"</{tag}>"):]
        filled = min(counter["i"], len(images))
    elif mode == "class":
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
