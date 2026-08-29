#!/usr/bin/env python3
"""Put a moving picture behind a build's hero, on top of the still it already has.

The build must already open on a `.gsw-backdrop` photograph (build-demo-copy.py
or add-hero-backdrop.py put it there). This drops a muted, looping `<video>`
over that `<picture>` inside the same backdrop, so:

  * the AVIF/JPEG plate is the poster - it paints first, and the clip fades in
    over it once enough has buffered, so nothing flashes;
  * the scrim, the copy, the contrast measurements and the reduced-motion and
    forced-colours rules all stay exactly as they are - the video sits under
    the same `::after` the photograph does;
  * `prefers-reduced-motion` and print hide the video and leave the still;
  * without JavaScript the video still plays (it is plain autoplay markup).

Preload is `metadata`, not `auto`: the plate carries the first paint and the
2MB clip streams in behind it rather than ahead of the copy.

    python3 tools/add-hero-video.py roofing halloran-roofing a-storm-clearing
    python3 tools/add-hero-video.py roofing halloran-roofing a-storm-clearing --remove

Idempotent; run it again after a rebuild.
"""

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
WORK = REPO / "work"
MARKER = "<!-- gsw:video -->"
END_MARKER = "<!-- /gsw:video -->"
STYLE_HEAD = "  /* gsw:video"

CSS = """
<style>
  /* gsw:video - the still plate is the poster; the loop fades in over it. */
  .gsw-backdrop video { position: absolute; inset: 0; width: 100%; height: 100%;
                        object-fit: cover; object-position: center;
                        opacity: 0; transition: opacity 1.2s ease-out; }
  .gsw-backdrop video.gsw-playing { opacity: 1; }
  @media (prefers-reduced-motion: reduce) { .gsw-backdrop video { display: none; } }
  @media print { .gsw-backdrop video { display: none; } }
</style>"""

# `canplay` rather than `playing`: Safari fires the latter unreliably for
# muted autoplay, and the fade only needs the first frames decoded.
SCRIPT = """<script>
(function(){var v=document.querySelector('.gsw-backdrop video');if(!v)return;
var on=function(){v.classList.add('gsw-playing')};
v.addEventListener('canplay',on,{once:true});if(v.readyState>=3)on();
if(window.matchMedia('(prefers-reduced-motion: reduce)').matches){v.pause();v.removeAttribute('autoplay');}})();
</script>"""


def video_tag(trade: str, stem: str) -> str:
    base = f"../_assets/hero/{trade}/{stem}"
    # H.264 first: it plays everywhere, and the VP9 copy - when one exists at
    # all - came out larger on Veo output, so it is only ever a fallback.
    sources = f'<source src="{base}.mp4" type="video/mp4">'
    if (WORK / "_assets" / "hero" / trade / f"{stem}.webm").exists():
        sources += f'<source src="{base}.webm" type="video/webm">'
    return (f'<video autoplay muted loop playsinline preload="metadata" '
            f'disablepictureinpicture disableremoteplayback aria-hidden="true" tabindex="-1">'
            f'{sources}</video>')


def strip(src: str) -> str:
    src = re.sub(re.escape(MARKER) + r".*?" + re.escape(END_MARKER), "", src, flags=re.S)
    src = re.sub(r"\n<style>\n" + re.escape(STYLE_HEAD) + r".*?</style>", "", src, flags=re.S)
    src = src.replace("\n" + SCRIPT, "")
    return src


def patch(page: Path, trade: str, stem: str, remove: bool) -> str:
    src = page.read_text()
    had = MARKER in src
    src = strip(src)
    if remove:
        page.write_text(src)
        return "video removed" if had else "no video to remove"

    if not (WORK / "_assets" / "hero" / trade / f"{stem}.mp4").exists():
        return f"missing encoded clip: {stem}.mp4 (run encode-hero-video.py --dest)"

    # Land inside the backdrop, after the <picture>, so the still stays the poster.
    m = re.search(r'<div class="gsw-backdrop"[^>]*>.*?</picture>', src, flags=re.S)
    if not m:
        return "no .gsw-backdrop picture - add-hero-backdrop.py first"
    src = src[:m.end()] + MARKER + video_tag(trade, stem) + END_MARKER + src[m.end():]
    src = src.replace("</head>", CSS + "\n</head>", 1)
    src = src.replace("</body>", SCRIPT + "\n</body>", 1)
    page.write_text(src)
    return "video replaced" if had else f"video added ({stem})"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("trade")
    ap.add_argument("slug")
    ap.add_argument("stem", help="clip basename under work/_assets/hero/<trade>/")
    ap.add_argument("--remove", action="store_true")
    args = ap.parse_args()

    page = WORK / args.trade / f"{args.slug}.html"
    if not page.exists():
        sys.exit(f"no build at {page.relative_to(REPO)}")
    print(f"  {args.slug:<34} {patch(page, args.trade, args.stem, args.remove)}")


if __name__ == "__main__":
    main()
