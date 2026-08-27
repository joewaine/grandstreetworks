#!/usr/bin/env python3
"""Fetch real, licence-clean photographs from Openverse.

The rest of the imagery in this set is generated, which is right for invented
businesses whose premises do not exist. Animals are the exception: a vet's site
is selling the feeling of handing your dog to someone, and a generated dog
reads as a generated dog to anyone who has owned one.

Openverse aggregates openly licensed images and needs no API key. This filters
to **CC0 only** — public domain, no attribution required, commercial use fine —
which is the only licence that behaves like the generated images do everywhere
else in the set. CC-BY would put an attribution line on a page belonging to an
invented business, which is worse than a generated photograph.

    python3 tools/fetch-stock-photos.py --search "golden retriever vet"
    python3 tools/fetch-stock-photos.py --get <url> --out veterinary/dog-exam

Search prints candidates with their dimensions; --get downloads one to
cash_rich/stock/<out>.jpg so the normal encode step can pick it up.
"""

import argparse
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

STOCK = Path.home() / "fractal" / "cash_rich" / "stock"
API = "https://api.openverse.org/v1/images/"
UA = {"User-Agent": "grandstreetworks/1.0 (reference builds)"}
# Below this a full-bleed plate visibly softens; gallery tiles are fine smaller.
MIN_WIDTH = 1000


def search(query: str, limit: int) -> None:
    params = urllib.parse.urlencode({
        "q": query, "license": "cc0", "page_size": limit * 3,
        "mature": "false", "category": "photograph",
    })
    req = urllib.request.Request(API + "?" + params, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    shown = 0
    for item in data.get("results", []):
        w, h = item.get("width") or 0, item.get("height") or 0
        if w < MIN_WIDTH:
            continue
        shown += 1
        print(f"  {w}x{h}  {item.get('license', '?'):5}  {item.get('title', '')[:44]:44}  {item['url']}")
        if shown >= limit:
            break
    if not shown:
        print(f"  nothing CC0 over {MIN_WIDTH}px for {query!r}")


def get(url: str, out: str) -> None:
    dest = STOCK / f"{out}.jpg"
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
    dest.write_bytes(data)
    print(f"  {dest.relative_to(Path.home())}  {len(data) // 1024}KB")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--search")
    ap.add_argument("--limit", type=int, default=8)
    ap.add_argument("--get")
    ap.add_argument("--out")
    args = ap.parse_args()

    if args.search:
        search(args.search, args.limit)
    elif args.get:
        if not args.out:
            sys.exit("--get needs --out")
        get(args.get, args.out)
    else:
        sys.exit("pass --search or --get")


if __name__ == "__main__":
    main()
