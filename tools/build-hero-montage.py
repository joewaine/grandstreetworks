#!/usr/bin/env python3
"""Build the asset manifest for the home-page hero montage.

The home hero runs one of two variants (split per browser by the page):

    dissolve   one flagship build at a time, full bleed, crossfading; a build
               whose trade has a hero clip plays it, the rest show the still
    wall       a grid of plates, tiles trading places
    mix        the two alternating (view only, ?hero=mix)

Singles come from `work/domains-flagship-20.txt`, one build per trade, each
opening on the plate its page already uses. The wall draws from a curated
folder, `~/fractal/cash_rich/montage_picks/`, holding `<trade>--<stem>.jpg`
copies of every plate in the library: delete what should not be on the wall
and re-run. Twenty tiles show at a time; a larger pool rotates through. With
no picks folder the wall falls back to the twenty flagship plates.

The manifest — `{"singles": [...], "wall": [...]}` — is written to
`work/_assets/montage/manifest.json` and inlined into `index.html` between
the `gsw:montage-manifest` markers, so the first plate does not wait on a
second request. Wall tiles are 640px AVIFs encoded here from the full-size
plates; the dissolve reuses each build's existing 1280 AVIF. Harlan & Vega
is the photographic trade and has no AVIF ladder, so its plate is encoded
here at both widths.

Where the build's own plate has a hero video loop
(`work/_assets/hero/<trade>/<stem>.mp4`) the single is the clip rather than
the still, with the plate as its poster.

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

# The photographic trade keeps its plates outside the AVIF ladder.
PI = "personal-injury"
PI_PLATE = WORK / "_assets" / "hero" / "record.jpg"
# The wall's curated pool: <trade>--<stem>.jpg, one per plate the wall may show.
PICKS = Path.home() / "fractal" / "cash_rich" / "montage_picks"

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
    """(clip, poster stem): only a clip cut from the build's own plate.

    Borrowing a sibling's clip was the bridge while the flagships had no
    clips of their own; it put a different picture in the single from the
    one on the wall. A plate with no clip of its own shows as a still."""
    clip = WORK / "_assets" / "hero" / trade / f"{plate_stem}.mp4"
    return (clip, clip.stem) if clip.exists() else None


INDEX = ROOT / "index.html"
MARK_OPEN = "<!-- gsw:montage-manifest -->"
MARK_CLOSE = "<!-- /gsw:montage-manifest -->"


def inline_manifest(entries: dict) -> None:
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


def plate_source(trade: str, stem: str) -> Path:
    """The best on-disk original for a plate: the 2560 AVIF, or PI's JPEG."""
    if trade == PI:
        return WORK / "_assets" / "hero" / f"{stem}.jpg"
    return WORK / "_assets" / "hero" / trade / f"{stem}-2560.avif"


def builds_by_plate(trade: str) -> dict[str, tuple[str, Path]]:
    """stem -> (firm, page) for every build in the trade, first page wins."""
    out: dict[str, tuple[str, Path]] = {}
    for page in sorted((WORK / trade).glob("*.html")):
        if page.name == "index.html":
            continue
        text = page.read_text()
        m = PLATE_RE.search(text)
        stem = m.group(2) if m else None
        if trade == PI:
            pm = re.search(r"_assets/hero/([a-z0-9_-]+)\.jpg", text)
            stem = pm.group(1) if pm else None
        if stem and stem not in out:
            out[stem] = (firm_name(page), page)
    return out


def wall_entries(singles: list[dict], force: bool) -> tuple[list[dict], int]:
    """The wall's pool from the picks folder, or the flagship plates without one."""
    picks = sorted(PICKS.glob("*.jpg")) if PICKS.is_dir() else []
    written = 0
    if not picks:
        print(f"no picks in {PICKS}: wall falls back to the flagship plates")
        picks = None

    wanted = []
    if picks is None:
        for e in singles:
            wanted.append((e["trade"], e["plate_stem"]))
    else:
        for f in picks:
            if "--" not in f.stem:
                sys.exit(f"{f.name}: expected <trade>--<stem>.jpg")
            trade, stem = f.stem.split("--", 1)
            if trade not in TRADE_LABELS:
                sys.exit(f"{f.name}: unknown trade {trade!r}")
            wanted.append((trade, stem))

    by_trade: dict[str, dict[str, tuple[str, Path]]] = {}
    flagship = {(e["trade"], e["plate_stem"]): e for e in singles}
    entries = []
    for trade, stem in wanted:
        src = plate_source(trade, stem)
        if not src.exists():
            sys.exit(f"{src}: missing (picked as {trade}--{stem})")
        tile = OUT / f"{trade}--{stem}-{TILE_WIDTH}.avif"
        written += encode_avif(src, tile, TILE_WIDTH, force)

        if (trade, stem) in flagship:
            e = flagship[(trade, stem)]
            firm, url = e["firm"], e["url"]
        else:
            by_trade.setdefault(trade, builds_by_plate(trade))
            hit = by_trade[trade].get(stem)
            if hit:
                firm, url = hit[0], f"work/{hit[1].relative_to(WORK)}"
            else:
                firm, url = TRADE_LABELS[trade], f"work/{trade}/"
        entries.append({
            "trade": trade,
            "label": TRADE_LABELS[trade],
            "firm": firm,
            "url": url,
            "tile": f"work/{tile.relative_to(WORK)}",
        })

    # The first twenty are what a visitor sees before any tile has turned, so
    # deal the pool out one trade at a time rather than alphabetically, which
    # would open on a wall of accountants.
    by_trade_order: dict[str, list[dict]] = {}
    for e in entries:
        by_trade_order.setdefault(e["trade"], []).append(e)
    dealt = []
    while any(by_trade_order.values()):
        for trade in list(by_trade_order):
            if by_trade_order[trade]:
                dealt.append(by_trade_order[trade].pop(0))
    entries = dealt

    # Tiles for plates no longer picked would otherwise linger in the repo.
    keep = {ROOT / e["tile"] for e in entries}
    for stale in OUT.glob(f"*-{TILE_WIDTH}.avif"):
        if stale not in keep:
            stale.unlink()
    return entries, written


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

        if trade == PI:
            plate = OUT / f"{slug}-{PLATE_WIDTH}.avif"
            written += encode_avif(src, plate, PLATE_WIDTH, args.force)
            plate_rel = plate.relative_to(WORK)
        else:
            plate_rel = Path(str(src.relative_to(WORK)).replace("-2560.avif", f"-{PLATE_WIDTH}.avif"))

        video = None
        if trade != PI:
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
            "plate_stem": src.stem.replace("-2560", "") if trade != PI else src.stem,
            **video_fields,
        })

    wall, wall_written = wall_entries(entries, args.force)
    written += wall_written
    for e in entries:
        del e["plate_stem"]

    manifest_data = {"singles": entries, "wall": wall}
    manifest = OUT / "manifest.json"
    manifest.write_text(json.dumps(manifest_data, indent=1) + "\n")
    inline_manifest(manifest_data)
    tiles_kb = sum((ROOT / e["tile"]).stat().st_size for e in wall) // 1024
    plates_kb = sum((ROOT / e["plate"]).stat().st_size for e in entries) // 1024
    clips = [e for e in entries if "video" in e]
    print(f"{len(entries)} singles ({plates_kb}KB of plates), "
          f"{len(wall)} wall tiles ({tiles_kb}KB), {written} files encoded")
    for e in clips:
        kb = (ROOT / e["video"]).stat().st_size // 1024
        print(f"  video  {e['slug']:<32} {Path(e['video']).name} ({kb}KB)")
    print(f"wrote {manifest.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
