#!/usr/bin/env python3
"""Re-encode the hero library into a responsive AVIF + JPEG ladder.

The first photography pass shipped one 1600px JPEG per plate. The plates are
full-bleed, so on a 1440px viewport at 2x they were being asked for ~2880px and
given 1600 — about 0.55x density, which reads as a soft, cheap image before
anyone judges the composition. The 2752px originals were on disk the whole time.

This emits, per plate:

    <name>-1280.avif  <name>-1920.avif  <name>-2560.avif   (q50)
    <name>-1600.jpg                                        (fallback, q72)

AVIF q50 was chosen by inspecting shingle granule texture — the hardest content
in the library for a lossy codec. At 2560px it lands around 230KB, which is
*lighter* than the 1600px JPEG it replaces while carrying 1.6x the pixels.

    python3 tools/build-responsive-images.py roofing
    python3 tools/build-responsive-images.py --all --force

Needs `avifenc` (brew install libavif) and macOS `sips`.
"""

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SOURCE = Path.home() / "fractal" / "cash_rich" / "hero_images"
DEST = REPO / "work" / "_assets" / "hero"

# Two AVIF steps, not three: 1280 covers phones and 1x laptops, 2560 covers a
# retina desktop full-bleed, and the 1920 in between earned its weight on
# almost no real viewport.
AVIF_WIDTHS = (1280, 2560)
AVIF_QUALITY = "50"
# Library images are gallery tiles and one wide band, never a full-bleed hero,
# so they top out lower and carry a smaller fallback.
# A gallery tile is at most half the 1140px wrap, so 1280 already covers it at
# 2x; 1920 was never selected by any viewport.
LIBRARY_AVIF_WIDTHS = (640, 1280)
LIBRARY_JPEG_WIDTH = 720
LIBRARY_SOURCE = Path.home() / "fractal" / "cash_rich" / "trade_library"
LIBRARY_DEST = REPO / "work" / "_assets" / "library"
# -s 6 is the speed/size knee; below it the encode time climbs for <2% saving.
AVIF_SPEED = "6"
# The JPEG is a fallback for the few percent of browsers without AVIF, not the
# image anyone is meant to see: it was 44% of the trade's disk for <5% of
# traffic. Smaller and softer is the right trade here.
JPEG_WIDTH = 1280
JPEG_QUALITY = "62"

# personal-injury's plates came from static2, not the hero library.
PI = "personal-injury"


def sips(src: Path, out: Path, width: int, fmt: str, quality: str | None = None) -> None:
    cmd = ["sips", "-Z", str(width), "-s", "format", fmt]
    if quality:
        cmd += ["-s", "formatOptions", quality]
    cmd += [str(src), "--out", str(out)]
    subprocess.run(cmd, check=True, capture_output=True)


def encode_plate(src: Path, out_dir: Path, force: bool,
                 avif_widths=AVIF_WIDTHS, jpeg_width=JPEG_WIDTH) -> tuple[int, int]:
    """Emit the full ladder for one plate. Returns (written, skipped)."""
    stem = src.stem
    written = skipped = 0
    AVIF_WIDTHS_L, JPEG_WIDTH_L = avif_widths, jpeg_width
    targets = [(out_dir / f"{stem}-{w}.avif", w) for w in AVIF_WIDTHS_L]
    targets.append((out_dir / f"{stem}-{JPEG_WIDTH_L}.jpg", JPEG_WIDTH_L))

    if not force and all(t.exists() for t, _ in targets):
        return 0, len(targets)

    # sips cannot write AVIF, so stage a PNG at each width and hand it to avifenc.
    with tempfile.TemporaryDirectory() as tmp:
        for width in AVIF_WIDTHS_L:
            out = out_dir / f"{stem}-{width}.avif"
            if out.exists() and not force:
                skipped += 1
                continue
            staged = Path(tmp) / f"{stem}-{width}.png"
            sips(src, staged, width, "png")
            subprocess.run(
                ["avifenc", "-q", AVIF_QUALITY, "-s", AVIF_SPEED, "-j", "8",
                 str(staged), str(out)],
                check=True, capture_output=True)
            written += 1

    jpg = out_dir / f"{stem}-{JPEG_WIDTH_L}.jpg"
    if force or not jpg.exists():
        sips(src, jpg, JPEG_WIDTH_L, "jpeg", JPEG_QUALITY)
        written += 1
    else:
        skipped += 1
    return written, skipped


def source_dir_for(trade: str) -> Path:
    """Where the highest-resolution originals for a trade live."""
    if trade == PI:
        # The static2 plates are shared at the top of _assets/hero, already 1600px.
        # Nothing higher-resolution exists on disk, so they are left alone.
        return DEST
    return SOURCE / trade


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("trades", nargs="*", help="trade slugs, e.g. roofing")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--kind", choices=("hero", "library"), default="hero",
                    help="library encodes work/_assets/library/<trade> in place")
    args = ap.parse_args()

    for tool in ("avifenc", "sips"):
        if not shutil.which(tool):
            sys.exit(f"missing {tool}")

    if args.all:
        trades = sorted(p.name for p in SOURCE.iterdir() if p.is_dir())
    elif args.trades:
        trades = args.trades
    else:
        sys.exit("name at least one trade, or pass --all")

    total_w = total_s = 0
    if args.kind == "library":
        for trade in trades:
            src_dir = LIBRARY_SOURCE / trade
            d = LIBRARY_DEST / trade
            if not src_dir.is_dir():
                print(f"  {trade:<24} no library, skipped")
                continue
            d.mkdir(parents=True, exist_ok=True)
            for img in sorted(src_dir.glob("*.jpg")):
                w, s_ = encode_plate(img, d, args.force,
                                     LIBRARY_AVIF_WIDTHS, LIBRARY_JPEG_WIDTH)
                total_w += w
                total_s += s_
            kb = sum(f.stat().st_size for f in d.glob("*.avif")) // 1024
            print(f"  {trade:<24} {len(list(d.glob('*.avif')))} avif, {kb}KB")
        print(f"\nwrote {total_w}, skipped {total_s}")
        return

    for trade in trades:
        src_dir = source_dir_for(trade)
        if trade == PI or not src_dir.is_dir():
            print(f"  {trade:<24} no high-resolution source, skipped")
            continue
        out_dir = DEST / trade
        out_dir.mkdir(parents=True, exist_ok=True)
        for plate in sorted(src_dir.glob("*.jpg")):
            w, s = encode_plate(plate, out_dir, args.force)
            total_w += w
            total_s += s
        avif_kb = sum(f.stat().st_size for f in out_dir.glob("*.avif")) // 1024
        print(f"  {trade:<24} {len(list(out_dir.glob('*.avif')))} avif, {avif_kb}KB")

    print(f"\nwrote {total_w}, skipped {total_s}")


if __name__ == "__main__":
    main()
