#!/usr/bin/env python3
"""Add a drag-to-compare before/after slider to a trade's builds.

Three of the six cosmetic dentistry builds are designed around a smile preview
that was never actually there — D2 is titled "THE PREVIEW ONE" and puts the
preview panel beside the headline because "the preview is what this practice is
selling"; D1's own comment calls its preview frame "abstract CSS geometry
standing in for the digital smile preview". This replaces the stand-in with the
thing itself.

No library. The builds make no external requests beyond Google Fonts, and a
comparison slider is about forty lines of CSS over one `<input type="range">`,
which is also what makes it keyboard-operable and touch-draggable for free
rather than through custom pointer handling.

Same borrowing rules as the gallery band: colour from the custom properties each
build already declares, type from a real <h2>, so a dark build gets a dark band
with no special case.

    python3 tools/build-compare-slider.py cosmetic-dentists
    python3 tools/build-compare-slider.py cosmetic-dentists --replace

Run gen-trade-library.py and build-responsive-images.py --kind library first.
"""

import argparse
import html
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
WORK = REPO / "work"
MARKER = "<!-- gsw:compare -->"
END_MARKER = "<!-- /gsw:compare -->"

AVIF_WIDTHS = (640, 1280)
JPEG_WIDTH = 720

# One pair per build: six practices should not display the same patient.
SETS = {
    "cosmetic-dentists": {
        "fairmont-dental-studio": {
            # D1 draws a mock slider in its hero: .preview i is a divider rule and
            # .teeth s:nth-child(n+5) flips the tooth colour from beige to white.
            # The build was asking for this component; it goes in the hero, in
            # place of the stand-in, rather than in a band further down.
            "placement": "hero",
            "pair": "b", "label": "The preview",
            "heading": "See it before it is irreversible.",
            "note": "The same patient, photographed under the same light before and after. "
                    "Drag the handle — the preview is the point, and this is the only "
                    "honest way to show one.",
            "caption": "Staining and tartar removed, gap closed, teeth whitened"},
        "belmont-smile-design": {
            "pair": "c", "label": "Before we start",
            "heading": "The preview is the product.",
            "note": "You approve the result on screen before a single tooth is prepared. "
                    "Drag to compare — nothing here is a stock photograph of somebody "
                    "else's work.",
            "caption": "Deep staining lifted, chipped incisor restored"},
        "verano-cosmetic-dentistry": {
            "pair": "a", "label": "Case 041",
            "heading": "Forty of these, not four.",
            "note": "Every case in the gallery is shot the same way, on the same "
                    "background, under the same light. Drag the handle.",
            "caption": "Years of coffee and tea staining, cleaned and whitened"},
        "aldridge-dental": {
            "pair": "d", "label": "A case",
            "heading": "Worn, stained, and put right.",
            "note": "Years of grinding had flattened the edges and the staining had "
                    "settled into them. Drag to compare the same mouth before and after.",
            "caption": "Worn edges rebuilt, staining removed, shade lifted"},
        "havenwood-dental": {
            "pair": "e", "label": "One of ours",
            "heading": "Nothing here is beyond fixing.",
            "note": "Old repairs darken and staining builds up — both are routine to put "
                    "right. Drag the handle to see the same mouth after treatment.",
            "caption": "Failed old bonding replaced, full clean and whitening"},
        "callaway-dental-arts": {
            "pair": "f", "label": "At the consult",
            "heading": "What we would actually change.",
            "note": "The consult ends with this, on screen, for your own teeth. Drag to "
                    "compare a case we treated end to end.",
            "caption": "Grey banding and deposit cleared, teeth whitened"},
    },
}

CSS = """
<style>
  /* Before/after comparison. The control is a real range input, laid over the
     frame at full size and made invisible: it brings keyboard operation, touch
     dragging and assistive-tech semantics that a custom pointer handler would
     have to reimplement badly. */
  .gsw-cmp-band { background: var(--surface); color: var(--ink);
                  padding: clamp(38px, 6vw, 74px) 0; }
  .gsw-cmp-in { max-width: var(--wrap, 1120px); margin: 0 auto; padding: 0 20px; }
  .gsw-cmp-lab { font-size: 13px; letter-spacing: .18em; text-transform: uppercase;
                 font-weight: 600; color: var(--accent); margin: 0 0 14px; }
  .gsw-cmp-band h2 { margin: 0; }
  .gsw-cmp-note { color: var(--muted); margin: 14px 0 28px; max-width: 58ch; }

  .gsw-cmp { --pos: 50%; margin: 0; max-width: 760px; }
  /* The overlays position against the image alone. Anchoring them to the
     figure let the rule and the tags run down over the caption. */
  .gsw-cmp-frame { position: relative; overflow: hidden; touch-action: pan-y; }
  .gsw-cmp picture, .gsw-cmp img { display: block; width: 100%; height: auto; }
  .gsw-cmp img { aspect-ratio: 4 / 3; object-fit: cover; }
  /* The "before" is the clipped layer, so the handle reveals the past by
     dragging right — the direction people expect from a slider. */
  .gsw-cmp-before { position: absolute; inset: 0;
                    clip-path: inset(0 calc(100% - var(--pos)) 0 0); }
  .gsw-cmp-line { position: absolute; top: 0; bottom: 0; left: var(--pos);
                  width: 2px; background: #fff; transform: translateX(-1px);
                  box-shadow: 0 0 0 1px rgb(0 0 0 / .28); pointer-events: none; }
  .gsw-cmp-grip { position: absolute; top: 50%; left: 50%; width: 42px; height: 42px;
                  transform: translate(-50%, -50%); border-radius: 50%;
                  background: #fff; box-shadow: 0 2px 10px rgb(0 0 0 / .34);
                  display: grid; place-items: center; }
  .gsw-cmp-grip::before { content: "‹ ›"; font: 600 15px/1 system-ui, sans-serif;
                          color: #111; letter-spacing: .06em; }
  .gsw-cmp-tag { position: absolute; bottom: 12px; font-size: 12px; font-weight: 600;
                 letter-spacing: .14em; text-transform: uppercase; padding: 6px 11px;
                 background: rgb(0 0 0 / .62); color: #fff; pointer-events: none; }
  .gsw-cmp-tag-b { left: 12px; }
  .gsw-cmp-tag-a { right: 12px; }
  .gsw-cmp-range { position: absolute; inset: 0; width: 100%; height: 100%;
                   margin: 0; opacity: 0; cursor: ew-resize;
                   -webkit-appearance: none; appearance: none; background: transparent; }
  .gsw-cmp-range::-webkit-slider-thumb { -webkit-appearance: none; width: 44px;
                                         height: 100%; }
  .gsw-cmp-range::-moz-range-thumb { width: 44px; height: 100%; border: 0;
                                     background: transparent; }
  /* The input is invisible, so the focus ring has to be drawn on the frame. */
  .gsw-cmp-frame:has(.gsw-cmp-range:focus-visible) { outline: 3px solid var(--accent);
                                                     outline-offset: 3px; }
  .gsw-cmp-cap { margin: 12px 0 0; font-size: 14px; color: var(--muted); }
  /* Hero placement: the build's own .preview card keeps its radius, border and
     shadow, and the comparison fills it. Its 16:7 crop is deliberate — it holds
     the smile and drops the chin. */
  .gsw-cmp-inset { max-width: none; height: 100%; }
  .gsw-cmp-inset .gsw-cmp-frame { height: 100%; }
  .gsw-cmp-inset img { height: 100%; aspect-ratio: auto; object-fit: cover; }
  .gsw-cmp-herocap { margin: 12px auto 0; max-width: 620px; text-align: center;
                     font-size: 13px; color: var(--muted); }
  /* Without JavaScript the handle cannot move, so it is not offered: the frame
     falls back to a static half-and-half with both labels still readable. */
  .gsw-cmp:not([data-live]) .gsw-cmp-range,
  .gsw-cmp:not([data-live]) .gsw-cmp-grip { display: none; }
</style>"""

SCRIPT = """
<script>
/* One listener per frame. Writing the position to a custom property keeps the
   clip, the rule and the grip on a single source of truth. */
(function () {
  document.querySelectorAll('.gsw-cmp').forEach(function (frame) {
    var range = frame.querySelector('.gsw-cmp-range');
    if (!range) return;
    var apply = function () { frame.style.setProperty('--pos', range.value + '%'); };
    range.addEventListener('input', apply);
    frame.setAttribute('data-live', '');
    apply();
  });
})();
</script>"""


def frame(trade: str, spec: dict, inset: bool = False) -> str:
    pair = spec["pair"]
    def pic(side: str) -> str:
        base = f"../_assets/library/{trade}/smile-{pair}-{side}"
        srcset = ", ".join(f"{base}-{w}.avif {w}w" for w in AVIF_WIDTHS)
        alt = ("Before treatment" if side == "before" else "After treatment")
        # In the hero the comparison is the LCP element, so it is not lazy.
        load = ('loading="eager" fetchpriority="high"' if inset
                else 'loading="lazy"')
        return (f'<picture><source type="image/avif" srcset="{srcset}" '
                f'sizes="(max-width: 800px) 100vw, 760px">'
                f'<img src="{base}-{JPEG_WIDTH}.jpg" width="1600" height="1200" '
                f'alt="{alt}" {load} decoding="async"></picture>')
    cls = "gsw-cmp gsw-cmp-inset" if inset else "gsw-cmp"
    return (
        f'<figure class="{cls}"><div class="gsw-cmp-frame">'
        + pic("after")
        + f'<div class="gsw-cmp-before">{pic("before")}</div>'
        '<span class="gsw-cmp-line" aria-hidden="true"><span class="gsw-cmp-grip"></span></span>'
        '<span class="gsw-cmp-tag gsw-cmp-tag-b">Before</span>'
        '<span class="gsw-cmp-tag gsw-cmp-tag-a">After</span>'
        '<input class="gsw-cmp-range" type="range" min="0" max="100" value="50" step="0.5" '
        'aria-label="Drag to compare the before and after photographs">'
        '</div>'
        + ('' if inset else
           f'<figcaption class="gsw-cmp-cap">{html.escape(spec["caption"])}</figcaption>')
        + '</figure>')


def section(trade: str, spec: dict) -> str:
    return (
        f'{MARKER}\n<section class="gsw-cmp-band"><div class="gsw-cmp-in">'
        f'<p class="gsw-cmp-lab">{html.escape(spec["label"])}</p>'
        f'<h2>{html.escape(spec["heading"])}</h2>'
        f'<p class="gsw-cmp-note">{html.escape(spec["note"])}</p>'
        f'{frame(trade, spec)}'
        f'</div></section>\n{END_MARKER}\n')


def patch(page: Path, trade: str, spec: dict, replace: bool) -> str:
    src = page.read_text()
    if MARKER in src:
        if not replace:
            return "already has a comparison slider"
        src = re.sub(re.escape(MARKER) + r".*?" + re.escape(END_MARKER) + r"\n?",
                     "", src, flags=re.S)
        # A hero placement consumed the stand-in; put a bare card back so the
        # replacement below has something to match.
        if spec.get("placement") == "hero" and '<div class="preview"' not in src:
            src = src.replace("</div></section>",
                              '<div class="preview" aria-hidden="true"></div>\n</div></section>', 1)
        src = re.sub(r"\n<style>\n  /\* Before/after comparison\..*?</style>", "",
                     src, flags=re.S)
        src = re.sub(r"\n<script>\n/\* One listener per frame\..*?</script>", "",
                     src, flags=re.S)

    src = src.replace("</head>", CSS + "\n</head>", 1)

    if spec.get("placement") == "hero":
        stand_in = re.search(r'<div class="preview"[^>]*>.*?</div>\s*</div>', src, re.S)
        if not stand_in:
            return "no .preview stand-in found"
        # Keep the card (radius, border, shadow) and fill it with the real thing.
        # The match ends on the stand-in's own closing tag, so nothing is re-added.
        replacement = (f'{MARKER}<div class="preview">{frame(trade, spec, inset=True)}</div>'
                       f'<p class="gsw-cmp-herocap">{html.escape(spec["caption"])}</p>'
                       f'{END_MARKER}')
        src = src[:stand_in.start()] + replacement + src[stand_in.end():]
        src = src.replace("</body>", SCRIPT + "\n</body>", 1)
        page.write_text(src)
        return "slider replaced the hero stand-in"

    if '<section class="close"' not in src:
        return "no closing section to sit above"
    src = src.replace('<section class="close"',
                      section(trade, spec) + '<section class="close"', 1)
    src = src.replace("</body>", SCRIPT + "\n</body>", 1)
    page.write_text(src)
    return "slider added"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("trades", nargs="+")
    ap.add_argument("--replace", action="store_true")
    args = ap.parse_args()

    for trade in args.trades:
        sets = SETS.get(trade)
        if not sets:
            print(f"  {trade}: no slider sets defined")
            continue
        lib = WORK / "_assets" / "library" / trade
        missing = [f"smile-{s['pair']}-{side}"
                   for s in sets.values() for side in ("before", "after")
                   if not (lib / f"smile-{s['pair']}-{side}-{JPEG_WIDTH}.jpg").exists()]
        if missing:
            sys.exit("missing encoded images: " + ", ".join(sorted(set(missing))))
        for slug, spec in sets.items():
            page = WORK / trade / f"{slug}.html"
            status = patch(page, trade, spec, args.replace) if page.exists() \
                else "page missing"
            print(f"  {slug:<34} {status}")


if __name__ == "__main__":
    main()
