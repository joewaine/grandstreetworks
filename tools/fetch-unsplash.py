#!/usr/bin/env python3
"""Source real photographs from Unsplash and encode them into the asset ladders.

The shared libraries are generated imagery, which is right for premises that do
not exist. It is wrong for animals and people: a generated dog reads as a
generated dog to anyone who has owned one. When a build needs a real
photograph, this fetches one from Unsplash (free licence: commercial use, no
attribution required — https://unsplash.com/license) and encodes it exactly the
way build-responsive-images.py encodes the rest of the store.

    python3 tools/fetch-unsplash.py --search "labrador at the vet" [--n 12]
    python3 tools/fetch-unsplash.py --get <photo id> --library veterinary/beckett-animal-care --name lab-exam
    python3 tools/fetch-unsplash.py --get <photo id> --hero veterinary --name f-golden-retriever

--search prints candidates (id, size, photographer, orientation, description).
Only free photos are listed; Unsplash+ (plus.unsplash.com) results are dropped
because that licence is per-subscriber.

--library writes <name>-640.avif, <name>-1280.avif, <name>-720.jpg into
work/_assets/library/<industry>/<slug>/ (the gallery-tile ladder).
--hero writes <name>-1280.avif, <name>-2560.avif, <name>-1280.jpg into
work/_assets/hero/<industry>/ (the full-bleed ladder). Hero names should carry
a letter prefix beyond the existing ones (a–e are taken in most industries).

Every download is appended to work/_assets/UNSPLASH-PROVENANCE.tsv with the
photo id, photographer, page URL and where it landed, so a page can be traced
back to its source without a Canva or Gemini record. The original download is
kept in ~/fractal/cash_rich/unsplash/<id>.jpg and never enters the repo.

Needs `avifenc` (brew install libavif) and macOS `sips`. No API key: this uses
the same endpoint the unsplash.com search page calls.
"""

import argparse
import json
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ASSETS = REPO / "work" / "_assets"
ORIGINALS = Path.home() / "fractal" / "cash_rich" / "unsplash"
PROVENANCE = ASSETS / "UNSPLASH-PROVENANCE.tsv"
SEARCH_API = "https://unsplash.com/napi/search/photos"
PHOTO_API = "https://unsplash.com/napi/photos/"
# A browser user agent gets a 307 to the HTML page; a plain client UA gets JSON.
UA = {"User-Agent": "grandstreetworks/1.0 (reference builds)", "Accept": "application/json"}

# Mirrors build-responsive-images.py so a fetched photo is indistinguishable
# from the rest of the ladder on disk.
HERO_AVIF_WIDTHS = (1280, 2560)
HERO_JPEG_WIDTH = 1280
LIBRARY_AVIF_WIDTHS = (640, 1280)
LIBRARY_JPEG_WIDTH = 720
AVIF_QUALITY = "50"
AVIF_SPEED = "6"
JPEG_QUALITY = "62"
# A gallery tile survives a 1200px source; a full-bleed plate needs 2560.
MIN_WIDTH = {"library": 1200, "hero": 2560}
DOWNLOAD_WIDTH = 3200


def fetch_json(url: str) -> dict:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def search(query: str, n: int) -> None:
    params = urllib.parse.urlencode({"query": query, "per_page": n * 2})
    data = fetch_json(f"{SEARCH_API}?{params}")
    shown = 0
    for r in data.get("results", []):
        if "plus.unsplash.com" in r["urls"]["raw"]:
            continue  # Unsplash+ — not covered by the free licence
        w, h = r["width"], r["height"]
        orient = "landscape" if w > h * 1.15 else "portrait" if h > w * 1.15 else "square"
        desc = (r.get("alt_description") or r.get("description") or "")[:70]
        print(f"  {r['id']:<12} {w:>5}x{h:<5} {orient:<9} {r['user']['name'][:22]:<22} {desc}")
        shown += 1
        if shown >= n:
            break
    if not shown:
        print(f"  nothing free for {query!r}")


def sips(src: Path, out: Path, width: int, fmt: str, quality: str | None = None) -> None:
    cmd = ["sips", "-Z", str(width), "-s", "format", fmt]
    if quality:
        cmd += ["-s", "formatOptions", quality]
    cmd += [str(src), "--out", str(out)]
    subprocess.run(cmd, check=True, capture_output=True)


def encode(src: Path, out_dir: Path, name: str, avif_widths, jpeg_width: int) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    with tempfile.TemporaryDirectory() as tmp:
        for width in avif_widths:
            staged = Path(tmp) / f"{name}-{width}.png"
            sips(src, staged, width, "png")
            out = out_dir / f"{name}-{width}.avif"
            subprocess.run(["avifenc", "-q", AVIF_QUALITY, "-s", AVIF_SPEED, "-j", "8",
                            str(staged), str(out)], check=True, capture_output=True)
            written.append(out)
    jpg = out_dir / f"{name}-{jpeg_width}.jpg"
    sips(src, jpg, jpeg_width, "jpeg", JPEG_QUALITY)
    written.append(jpg)
    return written


def get(photo_id: str, kind: str, target: str, name: str) -> None:
    meta = fetch_json(PHOTO_API + photo_id)
    raw = meta["urls"]["raw"]
    if "plus.unsplash.com" in raw:
        sys.exit(f"{photo_id} is an Unsplash+ photo; not covered by the free licence")
    if meta["width"] < MIN_WIDTH[kind]:
        sys.exit(f"{photo_id} is {meta['width']}px wide; a {kind} image needs {MIN_WIDTH[kind]}")

    ORIGINALS.mkdir(parents=True, exist_ok=True)
    original = ORIGINALS / f"{photo_id}.jpg"
    if not original.exists():
        url = f"{raw}&w={DOWNLOAD_WIDTH}&q=90&fm=jpg"
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=120) as r, open(original, "wb") as f:
            f.write(r.read())
        # Unsplash asks integrations to register a download; it is a courtesy
        # ping, not a licence condition, so a failure is not fatal.
        try:
            dl = meta.get("links", {}).get("download_location")
            if dl:
                urllib.request.urlopen(urllib.request.Request(dl, headers=UA), timeout=15).read()
        except Exception:
            pass

    if kind == "library":
        out_dir = ASSETS / "library" / target
        written = encode(original, out_dir, name, LIBRARY_AVIF_WIDTHS, LIBRARY_JPEG_WIDTH)
    else:
        out_dir = ASSETS / "hero" / target
        written = encode(original, out_dir, name, HERO_AVIF_WIDTHS, HERO_JPEG_WIDTH)

    if not PROVENANCE.exists():
        PROVENANCE.write_text("date\tphoto_id\tphotographer\tpage\tlanded_in\tname\n")
    with open(PROVENANCE, "a") as f:
        f.write("\t".join([date.today().isoformat(), photo_id, meta["user"]["name"],
                           meta["links"]["html"], f"{kind}/{target}", name]) + "\n")
    for p in written:
        print(f"  wrote {p.relative_to(REPO)}  {p.stat().st_size // 1024} KB")
    print(f"  photo by {meta['user']['name']} — {meta['links']['html']}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--search")
    ap.add_argument("--n", type=int, default=12)
    ap.add_argument("--get", metavar="PHOTO_ID")
    ap.add_argument("--library", metavar="INDUSTRY/SLUG")
    ap.add_argument("--hero", metavar="INDUSTRY")
    ap.add_argument("--name", help="file stem for the encoded ladder")
    a = ap.parse_args()

    if a.search:
        search(a.search, a.n)
        return
    if a.get:
        if not a.name or not (a.library or a.hero):
            sys.exit("--get needs --name and one of --library INDUSTRY/SLUG or --hero INDUSTRY")
        kind, target = ("library", a.library) if a.library else ("hero", a.hero)
        get(a.get, kind, target, a.name)
        return
    ap.print_help()


if __name__ == "__main__":
    main()
