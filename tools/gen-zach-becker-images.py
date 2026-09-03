#!/usr/bin/env python3
"""Generate aerial (drone-style) plates for the Zach Becker redesign runs.

Zach Becker's live site publishes one exterior photograph, a headshot, the
BHHS logos and the Leading Edge Society badge — nothing aerial. Joe asked for
drone real-estate shots, so these plates are generated once here and shared
by every benchmark run, exactly as the fencing and Palm plates were: same
model, same negative prompt, originals kept outside the repo in
~/fractal/clients/zach-becker/originals, provenance noted in the folder README.

    python3 tools/gen-zach-becker-images.py
    python3 tools/gen-zach-becker-images.py --only lake-washington --force

Needs GEMINI_API_KEY (source ~/.gemini/.env).
"""

import argparse
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

SLUG = "zach-becker"
OUT = Path.home() / "fractal" / "clients" / SLUG / "originals" / "aerials"
MODEL = "gemini-3-pro-image"
URL = "https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={k}"
SIZE = "2K"
WORKERS = 2  # the image endpoint rate-limits a burst of six

NEGATIVE = (
    "No text, no lettering, no signage, no logos, no watermarks, no UI elements. "
    "No recognisable faces, no people close to camera. Nothing that reads as "
    "stock photography. No HDR halos, no oversaturation."
)

DRONE = ("Aerial photograph taken from a drone at about 80 metres, wide lens, "
         "the horizon straight, fine detail in the trees and rooftops, natural "
         "colour, soft Pacific Northwest light. Professional real-estate "
         "photography, western Washington state. ")

# (name, prompt, aspect)
IMAGES = [
    ("lake-washington-dusk",
     DRONE + "Looking west across Lake Washington from above the Bellevue "
     "shoreline at dusk: waterfront homes with docks along a tree-lined shore in "
     "the foreground, the wide calm lake reflecting a soft peach-and-blue sky, "
     "the Seattle skyline small and dark on the far shore, the Olympic Mountains "
     "faint behind it. Douglas firs and cedars between the houses, a few "
     "windows lit.", "16:9"),
    ("eastside-neighborhood",
     DRONE + "A quiet Eastside neighbourhood near Kirkland in late-afternoon "
     "summer light: curving streets, generous lots with mature Douglas firs, a "
     "mix of modern and craftsman homes with grey and cedar siding, green lawns "
     "and a small park, the ground falling away toward Lake Washington with "
     "the water visible at the top of the frame, the Cascade foothills in the "
     "haze beyond.", "16:9"),
    ("modern-home-aerial",
     DRONE + "Directly above and slightly in front of a single contemporary "
     "home on a wooded lot: low-pitched roof with standing-seam metal, cedar "
     "soffits, a stone-and-grey-clapboard facade, a long driveway, a lawn, a "
     "back deck with an outdoor table, tall evergreens all around casting long "
     "morning shadows. The house fills about a third of the frame.", "3:2"),
    ("kirkland-waterfront",
     DRONE + "Kirkland waterfront on a clear morning: a marina with white "
     "sailboats, a lakeside park with a paved path and a small beach, "
     "mid-rise condominiums and older homes stepping up the hill behind, "
     "Lake Washington filling the lower half of the frame, Mount Rainier "
     "pale on the horizon to the south-east.", "16:9"),
    ("cascade-foothills-homes",
     DRONE + "High over the Sammamish plateau on an autumn afternoon: "
     "newer craftsman-style homes among big-leaf maples turning gold and dark "
     "evergreens, a trail through the trees, Lake Sammamish glinting in the "
     "middle distance and the snow-dusted Cascade Range across the whole "
     "horizon.", "16:9"),
    ("portrait-lakeside",
     DRONE + "Vertical composition for a phone screen: looking down the "
     "length of a wooded lakeshore at golden hour, a row of waterfront homes "
     "with docks, the lake to the left, tall firs to the right, the far shore "
     "and the Olympic Mountains at the top of the frame.", "9:16"),
]


def request(parts, aspect, key, retries=3):
    body = {"contents": [{"parts": parts}],
            "generationConfig": {"imageConfig": {"aspectRatio": aspect,
                                                 "imageSize": SIZE},
                                 "responseModalities": ["IMAGE"]}}
    req = urllib.request.Request(
        URL.format(m=MODEL, k=key), data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"})
    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=240) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            text = e.read().decode(errors="replace")[:300]
            if e.code in (429, 500, 502, 503) and attempt < retries:
                wait = 15 * attempt
                print(f"  HTTP {e.code}, retry in {wait}s: {text}", file=sys.stderr)
                time.sleep(wait)
                continue
            raise SystemExit(f"HTTP {e.code}: {text}")
        except (urllib.error.URLError, TimeoutError) as e:
            if attempt < retries:
                time.sleep(15 * attempt)
                continue
            raise SystemExit(f"request failed: {e}")


def image_from(resp):
    for cand in resp.get("candidates", []):
        for part in cand.get("content", {}).get("parts", []):
            data = part.get("inlineData")
            if data and data.get("mimeType", "").startswith("image/"):
                return base64.b64decode(data["data"]), data["mimeType"]
    reason = resp.get("candidates", [{}])[0].get("finishReason", "?")
    raise SystemExit(f"no image in response (finishReason={reason}): "
                     f"{json.dumps(resp)[:400]}")


def generate(item, key, force):
    name, prompt, aspect = item
    ext = "png"
    out = OUT / f"{name}.{ext}"
    if out.exists() and not force:
        print(f"  {name}: exists, skipping")
        return out
    print(f"  {name}: generating ({aspect}, {SIZE})")
    resp = request([{"text": prompt + " " + NEGATIVE}], aspect, key)
    data, mime = image_from(resp)
    if mime == "image/jpeg":
        out = OUT / f"{name}.jpg"
    out.write_bytes(data)
    (OUT / f"{name}.json").write_text(json.dumps(
        {"model": MODEL, "aspect": aspect, "size": SIZE, "prompt": prompt,
         "negative": NEGATIVE, "generated": time.strftime("%Y-%m-%dT%H:%M:%S")},
        indent=2))
    print(f"  {name}: {out.name} {len(data)//1024} KB")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", action="append", default=[])
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        env = Path.home() / ".gemini" / ".env"
        if env.exists():
            for line in env.read_text().splitlines():
                if line.startswith("GEMINI_API_KEY="):
                    key = line.split("=", 1)[1].strip().strip('"')
    if not key:
        raise SystemExit("GEMINI_API_KEY not set (source ~/.gemini/.env)")
    OUT.mkdir(parents=True, exist_ok=True)
    items = [i for i in IMAGES if not a.only or i[0] in a.only]
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        list(ex.map(lambda i: generate(i, key, a.force), items))


if __name__ == "__main__":
    main()
