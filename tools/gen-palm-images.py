#!/usr/bin/env python3
"""Generate Gemini backdrops for the Palm Construction client site
(sites/palm-construction).

Same request shape and negative prompt as gen-fencing-images.py. Palm's own
imagery is two 1080p drone reels and a folder of 640px phone photos; the reels
give the hero and the gallery, and these three plates carry the atmospheric
bands (about, financing, closing) where a photograph of a specific job would
be the wrong register anyway. They are atmosphere, not portfolio, and the
site README says so. Originals live outside the repo in
~/fractal/clients/palm-construction/originals; build-palm-site.py encodes
the ladder the repo carries.

    python3 tools/gen-palm-images.py
    python3 tools/gen-palm-images.py --only dusk --force

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

SLUG = "palm-construction"
OUT = Path.home() / "fractal" / "clients" / SLUG / "originals"
MODEL = "gemini-3-pro-image"
URL = "https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={k}"
SIZE = "2K"

NEGATIVE = (
    "No text, no lettering, no signage, no logos, no watermarks, no UI elements. "
    "No recognisable faces. Nothing that reads as stock photography."
)

PNW = ("Pacific Northwest setting in western Washington state: Douglas fir and "
       "cedar trees, soft light, the air a little damp. Architectural photograph, "
       "natural colour, no HDR, no filter.")

# (name, prompt, aspect)
IMAGES = [
    ("dusk",
     "Wide photograph of a modern Pacific Northwest home at dusk, seen from the "
     "back garden: a covered outdoor living room under a timber-framed roof with "
     "black steel posts, warm recessed lighting, a long composite deck in a deep "
     "walnut tone with a horizontal cable railing, a linear gas fire table, and "
     "floor-to-ceiling glass doors open to a lit kitchen inside. Cedar and dark "
     "board-and-batten siding, a low-pitched standing-seam roof. Puget Sound "
     "water and a far shoreline glimpsed between tall Douglas firs, the sky a "
     "deep blue with the last light on the horizon. " + PNW +
     " 24mm, tripod at chest height, long exposure, the house glowing.", "16:9"),
    ("kitchen",
     "Photograph of a newly remodelled high-end kitchen in a Pacific Northwest "
     "home: a long island in honed white quartz with a waterfall edge, flat-panel "
     "rift white oak cabinetry, a matte black range with a plaster hood, a full-"
     "height marble-look slab backsplash, brass hardware, wide-plank white oak "
     "floors, and a wall of black-framed windows looking onto evergreen trees in "
     "soft overcast light. Nothing on the counters but a wooden board and a bowl "
     "of lemons. " + PNW + " 28mm, camera at counter height, straight on to the "
     "island, sharp end to end.", "16:9"),
    ("plans",
     "Close photograph of a remodel being planned on a walnut dining table: a set "
     "of architectural drawings for a deck and covered patio partly unrolled, a "
     "sample of walnut-brown composite decking board and a square of white oak "
     "flooring laid on the drawings, a brass scale ruler, a pencil, a ceramic cup "
     "of coffee, and one hand at the edge of the frame pointing at a detail, no "
     "face in frame. Soft daylight from a window to the left. " + PNW +
     " 50mm, shallow depth of field on the drawing and the samples.", "4:3"),
]


def request(parts, aspect, key, retries=3):
    body = {"contents": [{"parts": parts}],
            "generationConfig": {"imageConfig": {"aspectRatio": aspect,
                                                 "imageSize": SIZE}}}
    req = urllib.request.Request(
        URL.format(m=MODEL, k=key), data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"})
    for attempt in range(1, retries + 1):
        try:
            resp = json.load(urllib.request.urlopen(req, timeout=300))
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as e:
            detail = e.read().decode() if hasattr(e, "read") else str(e)
            if "credits are depleted" in detail or "billing" in detail:
                return None, f"BILLING: {detail[:160]}"
            if attempt == retries:
                return None, f"FAILED after {retries}: {detail[:160]}"
            time.sleep(4 * attempt)
            continue
        for part in resp["candidates"][0]["content"]["parts"]:
            if "inlineData" in part:
                return base64.b64decode(part["inlineData"]["data"]), None
        return None, "no image returned: " + json.dumps(resp)[:200]
    return None, "exhausted retries"


def generate(name, prompt, aspect, key, force):
    OUT.mkdir(parents=True, exist_ok=True)
    dest = OUT / f"{name}.jpg"
    if dest.exists() and not force:
        return f"{name}: skipped (exists)"
    data, err = request([{"text": f"{prompt} {NEGATIVE}"}], aspect, key)
    if err:
        return f"{name}: {err}"
    dest.write_bytes(data)
    return f"{name}: {len(data) // 1024}KB"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", action="append", default=[])
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        sys.exit("GEMINI_API_KEY not set (source ~/.gemini/.env)")
    tasks = [t for t in IMAGES if not a.only or t[0] in a.only]
    with ThreadPoolExecutor(max_workers=3) as pool:
        for line in pool.map(lambda t: generate(t[0], t[1], t[2], key, a.force), tasks):
            print(f"  {line}", flush=True)


if __name__ == "__main__":
    main()
