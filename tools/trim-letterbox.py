#!/usr/bin/env python3
"""Trim flat letterbox borders off generated library images.

The image model mostly fills the frame, but occasionally returns the photograph
inset on a flat field — a grey band along one or more edges. Full-bleed in a
slider or a gallery tile, that band reads as a broken image.

Detection is on row/column uniformity rather than colour, so it catches a band
of any shade: a letterbox row has essentially no variance across its width
(std well under 1), while even a soft out-of-focus row of real photograph sits
several times higher.

Paired images are trimmed together. A before/after pair whose two halves were
cropped differently would drift apart under the comparison slider's handle,
which is the one thing that pair has to get right.

    python3 tools/trim-letterbox.py cosmetic-dentists
    python3 tools/trim-letterbox.py cosmetic-dentists --dry-run

Operates on the originals in cash_rich, so re-encode afterwards.
"""

import argparse
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

SOURCE = Path.home() / "fractal" / "cash_rich" / "trade_library"
# A flat band sits under ~1; the softest real photograph rows measured ~5.
FLAT_STD = 2.5


def load(path: Path):
    meta = subprocess.run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", str(path)],
                          capture_output=True, text=True).stdout
    w = int([l for l in meta.splitlines() if "pixelWidth" in l][0].split(":")[1])
    h = int([l for l in meta.splitlines() if "pixelHeight" in l][0].split(":")[1])
    raw = subprocess.run(["ffmpeg", "-v", "quiet", "-i", str(path), "-f", "rawvideo",
                          "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.uint8).reshape(h, w, 3), w, h


def content_box(a: np.ndarray) -> tuple[int, int, int, int]:
    """(top, bottom, left, right) of the non-flat region, inclusive."""
    rows = a.astype(np.int16).std(axis=1).mean(axis=1)
    cols = a.astype(np.int16).std(axis=0).mean(axis=1)
    live_r = np.flatnonzero(rows >= FLAT_STD)
    live_c = np.flatnonzero(cols >= FLAT_STD)
    if not len(live_r) or not len(live_c):
        return 0, a.shape[0] - 1, 0, a.shape[1] - 1
    return int(live_r[0]), int(live_r[-1]), int(live_c[0]), int(live_c[-1])


def crop(path: Path, x: int, y: int, w: int, h: int) -> None:
    """ffmpeg, not sips: `sips --cropOffset` is silently ignored and crops from
    the centre, which takes the content off the opposite edge and leaves the
    band in place. Verified with a half-black/half-white test image."""
    tmp = path.with_suffix(".trim.jpg")
    subprocess.run(["ffmpeg", "-v", "quiet", "-y", "-i", str(path),
                    "-vf", f"crop={w}:{h}:{x}:{y}", "-q:v", "2", str(tmp)],
                   check=True)
    tmp.replace(path)


def pair_key(stem: str) -> str:
    """Images that must be trimmed identically share a key."""
    for suffix in ("-before", "-after"):
        if stem.endswith(suffix):
            return stem[: -len(suffix)]
    return stem


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("trades", nargs="+")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    for trade in args.trades:
        d = SOURCE / trade
        if not d.is_dir():
            print(f"  {trade}: no library")
            continue
        groups: dict[str, list[Path]] = defaultdict(list)
        for p in sorted(d.glob("*.jpg")):
            groups[pair_key(p.stem)].append(p)

        for key, paths in groups.items():
            boxes = []
            for p in paths:
                a, w, h = load(p)
                boxes.append((*content_box(a), w, h))
            # The intersection, so a pair is cropped to the same window.
            top = max(b[0] for b in boxes)
            bottom = min(b[1] for b in boxes)
            left = max(b[2] for b in boxes)
            right = min(b[3] for b in boxes)
            w, h = boxes[0][4], boxes[0][5]
            new_w, new_h = right - left + 1, bottom - top + 1
            if new_w >= w - 2 and new_h >= h - 2:
                continue
            names = ", ".join(p.stem for p in paths)
            print(f"  {names}: {w}x{h} -> {new_w}x{new_h} "
                  f"(trimmed t{top} b{h - 1 - bottom} l{left} r{w - 1 - right})")
            if args.dry_run:
                continue
            for p in paths:
                crop(p, left, top, new_w, new_h)


if __name__ == "__main__":
    main()
