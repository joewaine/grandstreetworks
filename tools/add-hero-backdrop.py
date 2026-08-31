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

# build slug -> (plate stem, scrim rgb, side[, drop_plate]) or a dict with the
# same keys plus "target": the section the photograph goes behind — "hero" by
# default, else a class token ("close") or an id ("#services"). Non-hero
# targets load lazily and scope their scrim to that section, so a hero
# backdrop on the same page keeps its own.
# `side` says where the copy sits, which is the side the scrim stays opaque on:
# "left" is the directional Green Circle scrim, "centre" a flat 0.78, and
# "flat:<alpha>" a flat wash at that alpha (0.5 reads as the photograph tinted
# in the build's colour; below 760px it is lifted so full-width copy holds).
# `drop_plate` removes the plate block under the hero, since the same picture
# is now behind it; its object-position carries over to the backdrop.
# The scrim colour must be the build's *ground*, not its ink: a light build with
# dark copy needs a light scrim. Getting this backwards puts grey text on a grey
# photograph, which is what happened to Brightfold first time round.
BACKDROPS = {
    "roofing": {
        # The docket is an opaque bordered panel, so the neighbourhood runs
        # behind it near full strength.
        "sentry-roofing-and-restoration": ("e-whole-neighbourhood", "233 235 236", "flat:0.3", True),
    },
    "hvac": {
        # The flagship: panel over its own plate, and the Veo loop via add-hero-video.
        "beacon-comfort-co": ("e-comfort-inside", "242 245 246", "flat:0.25", True),
    },
    "restoration": {
        "claymore-restoration": ("e-put-right", "245 247 246", "flat:0.25", True),
        "bluewater-restoration": ("b-handled", "242 244 245", "left", True),
    },
    "general-contractors": {
        "bexley-build-group": ("a-finished-on-time", "230 221 204", "flat:0.5", True),
        "marrant-construction": ("b-the-detail", "250 246 236", "left", True),
        "whitfield-build-co": ("a-finished-on-time", "246 242 233", "left", True),
    },
    "wealth-management": {
        "bracken-and-lowe": ("b-calm-geometry", "250 248 244", "left", True),
        "ferrier-wealth-partners": ("a-not-a-sailboat", "247 246 242", "left", True),
    },
    "accounting-cpas": {
        "latimer-accounting": ("b-everything-in-its-place", "248 249 247", "left", True),
        "rennick-cpa": ("e-the-practice", "168 27 98", "flat:0.5", True),
    },
    "architecture": {
        "calderwood-architecture": ("d-drawing-macro", "242 241 237", "left", True),
    },
    "recruiting": {
        "brandt-yates-recruitment": ("d-steel-macro", "10 10 11", "left", True),
    },
    "veterinary": {
        "fernhill-veterinary": ("e-exam-room", "245 242 230", "left", True),
        "hollis-animal-hospital": ("d-soft-texture", "22 36 29", "flat:0.5", True),
    },
    "solar": {
        # D4 opened on a wall of white beside the incentive sheet.
        "brightfold-solar": ("e-street-of-roofs", "250 250 248", "left"),
    },
    # Stock-video builds: the plate is the first frame of the loop, so the
    # still and the clip are the same picture. Grounds measured in-browser
    # 2026-08-29 (Verano rgb(20,22,26) dark; Onyx & Ivory rgb(248,241,236) light).
    "cosmetic-dentists": {
        "verano-cosmetic-dentistry": ("f-the-chair", "20 22 26", "left"),
        # The porcelain macro that sat under Verano's hero moves behind the
        # closing CTA, diffused into the page's dark surface.
        "verano-cosmetic-dentistry:close": {"stem": "d-porcelain-macro", "rgb": "20 22 26",
                                             "side": "flat:0.72", "drop_plate": True,
                                             "target": "close"},
        # Havenwood's hero band (--band) over its plate, same as Rothbury.
        "havenwood-dental": ("e-the-practice", "46 36 31", "flat:0.5", True),
    },
    "med-spas": {
        # Onyx & Ivory was tried first and pulled: its hero is a 3x3 photo grid,
        # so the clip showed as a blur at the edges (the pool-builders rule).
        "palmer-row-med-spa": ("g-candlelit", "35 42 28", "left"),
        "bright-hour-med-spa": ("f-serum", "246 238 225", "left"),
        # Centred dark copy with no panel, so the surface wash runs heavier.
        "verity-skin-and-aesthetics": ("b-clean-flatlay", "246 242 245", "flat:0.35", True),
        # The light-on-water plate under Onyx's lattice hero moves behind the
        # price list, diffused into the page surface so the tiles stay legible.
        "onyx-and-ivory-aesthetics:services": {"stem": "d-light-on-water", "rgb": "248 241 236",
                                                "side": "flat:0.8", "drop_plate": True,
                                                "target": "#services"},
    },
    "plastic-surgeons": {
        # D-something green: the plate had sat as a block under the green hero.
        "rothbury-plastic-surgery": ("c-gloved-precision", "44 58 49", "flat:0.5", True),
        # The hero copy already sits in an opaque bordered panel, so the
        # photograph runs behind it near full strength: a light wash in the
        # page's own surface colour is all it needs.
        "sable-plastic-surgery": ("a-accredited-suite", "252 251 249", "flat:0.2", True),
    },
    "dermatology": {
        # The flagship: its plate is also its Veo clip, wired by add-hero-video.
        # A white counter: the wash stays light and the crop sits low so the
        # tray shows beneath the board card that covers the dermatoscope.
        "colvin-dermatology": {"stem": "b-precision-instrument", "rgb": "239 243 246",
                               "side": "flat:0.3", "drop_plate": True, "focus": "center 70%"},
    },
    "interior-design": {
        "ivory-lane-interiors": ("a-rooms-like-people", "92 44 28", "left"),
        "nocturne-interiors": ("f-after-dark", "18 20 22", "left"),
        # The weave macro that sat under the hero as a crop moves behind
        # "How we work", diffused into the page's ink.
        "nocturne-interiors:services": {"stem": "d-weave-macro", "rgb": "20 21 15",
                                        "side": "flat:0.78", "drop_plate": True,
                                        "target": "#services"},
        # The terrazzo speckle field ran straight under the headline.
        "sorrel-studio": ("e-the-whole-room", "247 243 234", "left"),
    },
}


MOBILE_FLAT_LIFT = 0.3   # flat scrims gain this much alpha below the breakpoint


def flat_alpha(side: str) -> float | None:
    return float(side.split(":", 1)[1]) if side.startswith("flat:") else None


def scrim(rgb: str, side: str) -> str:
    if side == "centre":
        return f"rgb({rgb} / 0.78)"
    if (a := flat_alpha(side)) is not None:
        return f"rgb({rgb} / {a:g})"
    return (f"linear-gradient(100deg, rgb({rgb} / 0.96) 0%, rgb({rgb} / 0.92) 42%, "
            f"rgb({rgb} / 0.70) 72%, rgb({rgb} / 0.48) 100%)")


def css(rgb: str, side: str, focus: str | None = None, target: str = "hero") -> str:
    mobile = min(0.95, (flat_alpha(side) or 0.9) + MOBILE_FLAT_LIFT) \
        if flat_alpha(side) is not None else 0.9
    # A second backdrop on the same page scopes its scrim to its own section;
    # the hero keeps the unscoped rule the fourteen existing builds rely on.
    scope = "" if target == "hero" else f".gsw-imaged--{target} "
    tag = "gsw:backdrop" if target == "hero" else f"gsw:backdrop:{target}"
    return f"""
<style>
  /* {tag} — the section opens on the work. The scrim is this build's own
     ink, heavy where the copy sits and thinning away from it, so the text
     never depends on what the photograph happens to be doing. */
  .gsw-imaged {{ position: relative; isolation: isolate; overflow: hidden; }}
  .gsw-imaged > *:not(.gsw-backdrop) {{ position: relative; z-index: 1; }}
  .gsw-backdrop {{ position: absolute; inset: 0; z-index: 0; }}
  .gsw-backdrop picture {{ display: block; width: 100%; height: 100%; }}
  {scope}.gsw-backdrop img {{ width: 100%; height: 100%; object-fit: cover;
                       object-position: {focus or "center"}; }}
  {scope}.gsw-backdrop::after {{ content: ""; position: absolute; inset: 0;
                          background: {scrim(rgb, side)}; }}
  /* Below the breakpoint the copy spans the full width, so the scrim goes flat. */
  @media (max-width: 760px) {{
    {scope}.gsw-backdrop::after {{ background: rgb({rgb} / {mobile:g}); }}
  }}
</style>"""


def picture(trade: str, stem: str, target: str = "hero") -> str:
    base = f"../_assets/hero/{trade}/{stem}"
    srcset = ", ".join(f"{base}-{w}.avif {w}w" for w in AVIF_WIDTHS)
    loading = 'loading="eager" fetchpriority="high"' if target == "hero" else 'loading="lazy"'
    return (f'<div class="gsw-backdrop" aria-hidden="true"><picture>'
            f'<source type="image/avif" srcset="{srcset}" sizes="100vw">'
            f'<img src="{base}-{JPEG_WIDTH}.jpg" width="2560" height="1429" alt="" '
            f'{loading} decoding="async">'
            f'</picture></div>')


PLATE_RE = re.compile(r'\n?<figure class="gsw-plate">.*?</figure>\n?', re.S)
FOCUS_RE = re.compile(r'style="object-position: ([^"]+)"')


def patch(page: Path, trade: str, spec, replace: bool) -> str:
    if isinstance(spec, dict):
        stem, rgb, side = spec["stem"], spec["rgb"], spec["side"]
        drop_plate, target = spec.get("drop_plate", False), spec.get("target", "hero")
        focus_override = spec.get("focus")
    else:
        stem, rgb, side = spec[:3]
        drop_plate, target = len(spec) > 3 and spec[3], "hero"
        focus_override = None
    by_id = target.startswith("#")
    key = target.lstrip("#")
    marker = MARKER if target == "hero" else f"<!-- gsw:backdrop:{key} -->"
    end_marker = END_MARKER if target == "hero" else f"<!-- /gsw:backdrop:{key} -->"
    css_tag = "gsw:backdrop" if target == "hero" else f"gsw:backdrop:{key}"
    wrapped = "gsw-imaged" if target == "hero" else f"gsw-imaged gsw-imaged--{key}"
    src = page.read_text()
    focus = None
    if drop_plate:
        m = PLATE_RE.search(src)
        if m:
            if stem not in m.group(0):
                return f"plate under the hero is not {stem}; not dropping it"
            fm = FOCUS_RE.search(m.group(0))
            focus = fm.group(1) if fm else None
            src = src[:m.start()] + "\n" + src[m.end():]
    focus = focus_override or focus
    if marker in src:
        if not replace:
            return "already has a backdrop"
        src = re.sub(re.escape(marker) + r".*?" + re.escape(end_marker), "", src, flags=re.S)
        src = re.sub(r"\n<style>\n  /\* " + re.escape(css_tag) + r" .*?</style>", "", src, flags=re.S)
        src = src.replace(f'<section class="{wrapped} ', '<section class="', 1)

    if not (WORK / "_assets" / "hero" / trade / f"{stem}-{JPEG_WIDTH}.jpg").exists():
        return f"missing encoded plate: {stem}"

    if target == "hero":
        # The hero is the first top-level section, whatever the design calls it.
        m = re.search(r'<section class="((?:(?!gsw-imaged)[^"])*)"([^>]*)>', src)
    elif by_id:
        m = re.search(r'<section class="((?:(?!gsw-imaged)[^"])*)"([^>]*\bid="' + re.escape(key)
                      + r'"[^>]*)>', src)
    else:
        m = re.search(r'<section class="((?:(?!gsw-imaged)[^"])*\b' + re.escape(key)
                      + r'\b[^"]*)"([^>]*)>', src)
    if not m:
        return f"no {target} section found"
    src = (src[:m.start()]
           + f'<section class="{wrapped} {m.group(1)}"{m.group(2)}>'
           + marker + picture(trade, stem, "hero" if target == "hero" else key) + end_marker
           + src[m.end():])
    src = src.replace("</head>", css(rgb, side, focus, "hero" if target == "hero" else key) + "\n</head>", 1)
    page.write_text(src)
    return f"backdrop added ({stem}) behind {target}"


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
        for key, spec in builds.items():
            slug = key.split(":", 1)[0]
            page = WORK / trade / f"{slug}.html"
            status = patch(page, trade, spec, args.replace) if page.exists() else "page missing"
            print(f"  {slug:<34} {status}")


if __name__ == "__main__":
    main()
