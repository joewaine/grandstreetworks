#!/usr/bin/env python3
"""Search and pull landscape hero clips from Pexels.

The video twin of fetch-stock-photos.py, for the trades where a Veo
image-to-video of a no-face plate has nothing to animate - a dentist's chair,
a med spa, a lawyer's desk - and for real client sites. The Pexels licence is
commercial use, no attribution, and covers client websites; the only terms
worth remembering are "don't resell the clip on its own" and that identifiable
people in a clip are covered by copyright licence, not personality rights, so
a real face on an invented business is still the wrong call.

    python3 tools/fetch-stock-video.py --search "dental clinic" --min-width 1920
    python3 tools/fetch-stock-video.py --get 3195394 --out cosmetic-dentists/chair

Search prints candidates: duration, the best landscape file's size, and the
page URL to preview. --get downloads that best file to
~/fractal/cash_rich/stock/video/<out>.mp4 for encode-hero-video.py.

Needs PEXELS_API_KEY. It is not in this repo's environment; the fallback reads
it from the faceless-YouTube pipeline's env file, which is where the key lives.
"""

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

STOCK = Path.home() / "fractal" / "cash_rich" / "stock" / "video"
API = "https://api.pexels.com/videos/"
# Pexels answers 403 to Python's default User-Agent; anything descriptive passes.
UA = "grandstreetworks/1.0 (reference builds)"
# The key was issued for the faceless-YouTube pipeline and is only stored there.
KEY_FILE = Path.home() / "fractal" / "youtube_faceless" / "pipeline" / "cron" / ".env"
# A hero is painted up to 1920 wide; below that it softens full-bleed.
MIN_WIDTH = 1920
# Hero loops are cut to 7-8s; anything under that cannot be looped from.
MIN_SECONDS = 8


def api_key() -> str:
    key = os.environ.get("PEXELS_API_KEY")
    if not key and KEY_FILE.exists():
        m = re.search(r"^PEXELS_API_KEY=\"?([^\"\n]+)", KEY_FILE.read_text(), re.M)
        key = m.group(1).strip() if m else None
    if not key:
        sys.exit(f"PEXELS_API_KEY not set and not found in {KEY_FILE}")
    return key


def get_json(url: str, key: str) -> dict:
    req = urllib.request.Request(url, headers={"Authorization": key, "User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"pexels {e.code} on {url.split('?')[0]}: "
                 f"{e.read().decode(errors='replace')[:300]}")


def best_file(video: dict, min_width: int) -> dict | None:
    """Widest landscape mp4 that clears the floor; None if nothing does."""
    files = [f for f in video.get("video_files", [])
             if f.get("file_type") == "video/mp4"
             and (f.get("width") or 0) >= min_width
             and (f.get("width") or 0) > (f.get("height") or 0)]
    return max(files, key=lambda f: f["width"]) if files else None


def search(query: str, limit: int, min_width: int, key: str) -> None:
    params = urllib.parse.urlencode({
        "query": query, "orientation": "landscape",
        "size": "large" if min_width > 1920 else "medium", "per_page": 80,
    })
    data = get_json(API + "search?" + params, key)
    print(f"  {data.get('total_results', 0)} results for {query!r}; "
          f"showing landscape >= {min_width}px, >= {MIN_SECONDS}s")
    shown = 0
    for v in data.get("videos", []):
        f = best_file(v, min_width)
        if not f or v.get("duration", 0) < MIN_SECONDS:
            continue
        shown += 1
        who = (v.get("user") or {}).get("name", "?")
        print(f"  {v['id']:>9}  {v['duration']:3}s  {f['width']}x{f['height']}  "
              f"{who[:22]:22}  {v['url']}")
        if shown >= limit:
            break
    if not shown:
        print("  nothing cleared the floor; try a looser query or --min-width 1280")


def get(video_id: int, out: str, min_width: int, key: str) -> None:
    v = get_json(API + f"videos/{video_id}", key)
    f = best_file(v, min_width)
    if not f:
        sys.exit(f"no landscape file >= {min_width}px on video {video_id}")
    dest = STOCK / f"{out}.mp4"
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(f["link"], headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=300) as r:
        dest.write_bytes(r.read())
    dest.with_suffix(".json").write_text(json.dumps({
        "pexels_id": video_id, "page": v.get("url"),
        "photographer": (v.get("user") or {}).get("name"),
        "width": f["width"], "height": f["height"], "duration": v.get("duration"),
    }, indent=1))
    print(f"  {dest.relative_to(Path.home())}  {dest.stat().st_size // 1024 // 1024}MB  "
          f"{f['width']}x{f['height']}  {v.get('duration')}s")
    print(f"\nnext:\n  python3 tools/encode-hero-video.py {dest} --name <stem> "
          f"--dest work/_assets/hero/<trade> --seamless 1 --start 00:00:00")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--search")
    ap.add_argument("--limit", type=int, default=10)
    ap.add_argument("--min-width", type=int, default=MIN_WIDTH)
    ap.add_argument("--get", type=int, help="Pexels video id")
    ap.add_argument("--out", help="path under cash_rich/stock/video, no extension")
    args = ap.parse_args()

    key = api_key()
    if args.search:
        search(args.search, args.limit, args.min_width, key)
    elif args.get:
        if not args.out:
            sys.exit("--get needs --out")
        get(args.get, args.out, args.min_width, key)
    else:
        sys.exit("pass --search or --get")


if __name__ == "__main__":
    main()
