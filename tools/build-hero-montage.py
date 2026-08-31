#!/usr/bin/env python3
"""Build the asset manifest for the home-page hero montage.

The home hero can run one of two montages of the twenty flagship builds
(`work/domains-flagship-20.txt`), sourced from the plate each build already
opens on — so the images are the ones picked as best for that trade, not a
second library:

    dissolve   one plate at a time, slow crossfade with a drift
    wall       all twenty at once as a grid, tiles shuffling
    mix        the two alternating: wall, one build, wall, the next build

Where a trade has a hero video loop (`work/_assets/hero/<trade>/*.mp4`) the
single is the clip rather than the still. A clip cut from the build's own
plate is preferred; otherwise the trade's first clip stands in and its own
plate is the poster, since poster and loop have to be the same picture.

All are driven by one manifest — firm, trade, build URL, plate, tile and any
clip — which this script writes to `work/_assets/montage/manifest.json` and
also inlines into `index.html` between the `gsw:montage-manifest` markers, so
the first plate does not wait on a second request. It also encodes a 640px
AVIF tile per build for the wall (the full-width dissolve reuses each build's
existing 1280 AVIF). Harlan & Vega is the photographic
trade and has no AVIF ladder, so its plate is encoded here at both widths.

    python3 tools/build-hero-montage.py            # write what is missing
    python3 tools/build-hero-montage.py --force    # re-encode everything

Needs `avifenc` (brew install libavif) and macOS `sips`, same as
build-responsive-images.py.
"""
from __future__ import annotations

import argparse
import csv
import html
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORK = ROOT / "work"
OUT = WORK / "_assets" / "montage"
FLAGSHIPS = WORK / "domains-flagship-20.txt"
DOMAIN_MAP = WORK / "domain-map.csv"

TILE_WIDTH = 640          # 5 columns on a 1920 desktop is 384px; 640 covers retina
PLATE_WIDTH = 1280        # matches the smallest rung of the hero ladder
AVIF_QUALITY = "50"       # same as build-responsive-images.py
AVIF_SPEED = "6"

# The photographic trade keeps its plate outside the AVIF ladder.
PI_PLATE = WORK / "_assets" / "hero" / "record.jpg"

# Display names as they appear in the home page's work grid.
TRADE_LABELS = {
    "personal-injury": "Personal injury",
    "cosmetic-dentists": "Cosmetic dentistry",
    "plastic-surgeons": "Plastic surgery",
    "med-spas": "Med spas",
    "dermatology": "Dermatology",
    "roofing": "Roofing",
    "hvac": "Heating & cooling",
    "restoration": "Restoration",
    "general-contractors": "General contracting",
    "luxury-real-estate": "Luxury real estate",
    "wealth-management": "Wealth management",
    "accounting-cpas": "Accounting",
    "architecture": "Architecture",
    "interior-design": "Interior design",
    "custom-home-builders": "Custom homes",
    "pool-builders": "Pool building",
    "solar": "Solar",
    "recruiting": "Recruiting",
    "property-management": "Property management",
    "veterinary": "Veterinary",
}

PLATE_RE = re.compile(r"_assets/hero/([a-z0-9_-]+)/([a-z0-9_-]+)-1280\.avif")
TITLE_RE = re.compile(r"<title>([^<]*)</title>")


def sh(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True, capture_output=True)


def encode_avif(src: Path, out: Path, width: int, force: bool) -> bool:
    """sips can resample but not write AVIF, so stage a PNG for avifenc."""
    if out.exists() and not force:
        return False
    with tempfile.TemporaryDirectory() as tmp:
        staged = Path(tmp) / "staged.png"
        sh(["sips", "-Z", str(width), "-s", "format", "png", str(src), "--out", str(staged)])
        sh(["avifenc", "-q", AVIF_QUALITY, "-s", AVIF_SPEED, "-j", "8", str(staged), str(out)])
    return True


def flagship_builds() -> list[tuple[str, str, str]]:
    """(trade, slug, domain) for each flagship, in the list's order."""
    by_domain = {}
    with DOMAIN_MAP.open() as f:
        for row in csv.DictReader(f):
            by_domain[row["domain"]] = (row["vertical"], row["page_slug"])
    out = []
    for domain in FLAGSHIPS.read_text().split():
        if domain not in by_domain:
            sys.exit(f"{domain}: not in {DOMAIN_MAP.name}")
        trade, slug = by_domain[domain]
        out.append((trade, slug, domain))
    return out


def firm_name(page: Path) -> str:
    m = TITLE_RE.search(page.read_text())
    if not m:
        sys.exit(f"{page}: no <title>")
    return html.unescape(m.group(1).split("·")[0].strip())


def source_plate(trade: str, page: Path) -> Path:
    """The original the build's hero plate was cut from."""
    if trade == "personal-injury":
        return PI_PLATE
    m = PLATE_RE.search(page.read_text())
    if not m:
        sys.exit(f"{page}: no 1280 AVIF hero plate found")
    # Encode tiles from the 2560 rung rather than upsampling the 1280 one.
    return WORK / "_assets" / "hero" / m.group(1) / f"{m.group(2)}-2560.avif"


def trade_video(trade: str, plate_stem: str | None) -> tuple[Path, str] | None:
    """(clip, poster stem) for the trade, favouring a clip of the build's own plate."""
    clips = sorted((WORK / "_assets" / "hero" / trade).glob("*.mp4"))
    if not clips:
        return None
    own = [c for c in clips if c.stem == plate_stem]
    clip = own[0] if own else clips[0]
    return clip, clip.stem


INDEX = ROOT / "index.html"
MARK_OPEN = "<!-- gsw:montage-manifest -->"
MARK_CLOSE = "<!-- /gsw:montage-manifest -->"


def inline_manifest(entries: list[dict]) -> None:
    """Replace the manifest script in index.html; idempotent."""
    s = INDEX.read_text()
    start, end = s.find(MARK_OPEN), s.find(MARK_CLOSE)
    if start < 0 or end < 0:
        sys.exit(f"{INDEX.name}: {MARK_OPEN} markers not found")
    # "</" inside JSON would end the script element early; there is none in
    # our own data, but escape it rather than trust that.
    body = json.dumps(entries, separators=(",", ":")).replace("</", "<\\/")
    block = (f'{MARK_OPEN}<script type="application/json" id="hero-montage-manifest">'
             f"{body}</script>")
    INDEX.write_text(s[:start] + block + s[end:])


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--force", action="store_true", help="re-encode existing tiles")
    args = ap.parse_args()

    for tool in ("avifenc", "sips"):
        if not shutil.which(tool):
            sys.exit(f"{tool} not found on PATH")

    OUT.mkdir(parents=True, exist_ok=True)
    entries, written = [], 0
    for trade, slug, domain in flagship_builds():
        page = WORK / trade / f"{slug}.html"
        if not page.exists():
            sys.exit(f"{page}: missing")
        src = source_plate(trade, page)
        if not src.exists():
            sys.exit(f"{src}: missing")

        tile = OUT / f"{slug}-{TILE_WIDTH}.avif"
        written += encode_avif(src, tile, TILE_WIDTH, args.force)

        if trade == "personal-injury":
            plate = OUT / f"{slug}-{PLATE_WIDTH}.avif"
            written += encode_avif(src, plate, PLATE_WIDTH, args.force)
            plate_rel = plate.relative_to(WORK)
        else:
            plate_rel = Path(str(src.relative_to(WORK)).replace("-2560.avif", f"-{PLATE_WIDTH}.avif"))

        video = None
        if trade != "personal-injury":
            video = trade_video(trade, src.stem.replace("-2560", ""))
        if video:
            clip, poster_stem = video
            poster = WORK / "_assets" / "hero" / trade / f"{poster_stem}-{PLATE_WIDTH}.avif"
            if not poster.exists():
                sys.exit(f"{poster}: missing poster for {clip.name}")
            video_fields = {
                "video": f"work/{clip.relative_to(WORK)}",
                "poster": f"work/{poster.relative_to(WORK)}",
            }
        else:
            video_fields = {}

        entries.append({
            "slug": slug,
            "trade": trade,
            "label": TRADE_LABELS[trade],
            "firm": firm_name(page),
            "domain": domain,
            "url": f"work/{trade}/{slug}.html",
            "plate": f"work/{plate_rel}",
            "tile": f"work/{tile.relative_to(WORK)}",
            **video_fields,
        })

    manifest = OUT / "manifest.json"
    manifest.write_text(json.dumps(entries, indent=1) + "\n")
    inline_manifest(entries)
    tiles_kb = sum((OUT / f"{e['slug']}-{TILE_WIDTH}.avif").stat().st_size for e in entries) // 1024
    plates_kb = sum((ROOT / e["plate"]).stat().st_size for e in entries) // 1024
    clips = [e for e in entries if "video" in e]
    print(f"{len(entries)} builds, {written} files encoded, tiles {tiles_kb}KB, plates {plates_kb}KB")
    for e in clips:
        kb = (ROOT / e["video"]).stat().st_size // 1024
        print(f"  video  {e['slug']:<32} {Path(e['video']).name} ({kb}KB)")
    print(f"wrote {manifest.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
