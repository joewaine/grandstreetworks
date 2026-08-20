#!/usr/bin/env python3
"""Resample the generated hero plates into work/_assets/hero/<trade>/.

The originals in cash_rich/hero_images are 2752px and 2.8–4MB each, which is
the right size to keep and the wrong size to serve. These go out at 1600px,
which is sharp full-bleed on a retina laptop and roughly a fifteenth of the
weight.

    python3 tools/prep-hero-images.py [--force]

Skips anything already present unless --force. macOS `sips` does the work.
"""

import argparse
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SOURCE = Path.home() / "fractal" / "cash_rich" / "hero_images"
DEST = REPO / "work" / "_assets" / "hero"
WIDTH = "1600"
QUALITY = "66"
# personal-injury already carries the static2 plates
SKIP = {"personal-injury"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    if not SOURCE.exists():
        sys.exit(f"no source library at {SOURCE}")

    done = skipped = 0
    for trade_dir in sorted(p for p in SOURCE.iterdir() if p.is_dir()):
        if trade_dir.name in SKIP:
            continue
        out_dir = DEST / trade_dir.name
        out_dir.mkdir(parents=True, exist_ok=True)
        for img in sorted(trade_dir.glob("*.jpg")):
            out = out_dir / img.name
            if out.exists() and not args.force:
                skipped += 1
                continue
            subprocess.run(
                ["sips", "-Z", WIDTH, "-s", "format", "jpeg",
                 "-s", "formatOptions", QUALITY, str(img), "--out", str(out)],
                check=True, capture_output=True)
            done += 1
        if out_dir.exists():
            kb = sum(f.stat().st_size for f in out_dir.glob("*.jpg")) // 1024
            print(f"  {trade_dir.name:<24} {len(list(out_dir.glob('*.jpg')))} plates, {kb}KB")
    print(f"\nresampled {done}, skipped {skipped}")


if __name__ == "__main__":
    main()
