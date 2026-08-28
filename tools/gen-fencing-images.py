#!/usr/bin/env python3
"""Generate the photography for the fencing client site (sites/northline-fence).

Same model, request shape and negative prompt as gen-trade-library.py, but a
client site rather than a reference build: one library, Washington-specific
(western red cedar, Douglas fir, overcast light, windstorm damage), and the
originals live outside the repo in ~/fractal/clients/<slug>/originals. The repo
only carries the encoded ladder that build-fencing-site.py emits.

    python3 tools/gen-fencing-images.py
    python3 tools/gen-fencing-images.py --only hero --force

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

SLUG = "northline-fence"
OUT = Path.home() / "fractal" / "clients" / SLUG / "originals"
MODEL = "gemini-3-pro-image"
URL = "https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={k}"
SIZE = "2K"

NEGATIVE = (
    "No text, no lettering, no signage, no logos, no watermarks, no UI elements. "
    "No recognisable faces. Nothing that reads as stock photography."
)

PNW = ("Pacific Northwest setting in western Washington state: tall Douglas fir and "
       "cedar trees behind, soft overcast daylight, damp green lawn, moss on a nearby "
       "tree trunk. Documentary photograph, natural colour, no HDR, no filter.")

# (name, prompt, aspect, reference-name or None)
IMAGES = [
    ("hero",
     "Wide photograph of a brand-new western red cedar privacy fence, six feet tall, "
     "boards a warm fresh-cut salmon-pink cedar colour with a horizontal cap rail and "
     "a rot board at the base, running along the edge of a suburban backyard. "
     "The fence recedes from the lower left toward the middle distance. " + PNW +
     " 35mm, camera at chest height, the fence sharp end to end.", "16:9", None),
    ("storm-before",
     "Photograph of an old grey weathered wooden fence in a suburban backyard after a "
     "windstorm: two panels blown over and lying on the wet lawn, a snapped rotten "
     "post stump still in the ground, moss and algae on the boards that are still "
     "standing, a downed fir branch on the grass. " + PNW +
     " 35mm, camera at chest height, three-quarter angle from the left.", "4:3", None),
    ("storm-after",
     "The same backyard, the same lawn, the same trees and exactly the same framing, "
     "angle and lighting as the reference image, after the fence has been replaced: "
     "a brand-new six-foot western red cedar privacy fence in fresh salmon-pink cedar "
     "with a horizontal cap rail, straight and plumb, standing where the collapsed "
     "grey fence was. The lawn is tidy and the downed branch and debris are gone. "
     "Keep everything about the scene identical; change only the fence. " + PNW,
     "4:3", "storm-before"),
    ("post-setting",
     "Close documentary photograph of a fence post being set: a pressure-treated "
     "four-by-four post standing in a freshly dug hole with a torpedo level clamped "
     "to it, a taut orange string line at the top, a wheelbarrow of wet concrete and "
     "a shovel beside it, gloved hands steadying the post at the edge of frame, no "
     "face in frame. Wet dark soil, gravel in the base of the hole. " + PNW +
     " 50mm, shallow depth of field on the post.", "4:3", None),
    ("cedar-detail",
     "Macro photograph of new western red cedar fence boards, tight vertical grain, "
     "with a stainless ring-shank nail head flush in the board and a pressure-treated "
     "rot board along the bottom edge sitting just above crushed gravel. Rain "
     "droplets beading on the fresh cedar. Soft overcast light. 100mm macro, the "
     "grain sharp, the background falling soft.", "4:3", None),
    ("gate",
     "Photograph of a custom western red cedar garden gate with a steel frame, black "
     "powder-coated heavy-duty hinges and a black gravity latch, set between two "
     "cedar posts with pyramid post caps, a gravel path leading through it. The gate "
     "is closed and hangs perfectly square. " + PNW +
     " 50mm, straight on, camera at waist height.", "4:3", None),
    ("chain-link",
     "Photograph of a new black vinyl-coated chain link fence, five feet tall with "
     "black posts and top rail, running along the side of a property beside a gravel "
     "driveway, a detached garage in the distance. " + PNW +
     " 35mm, three-quarter angle, the fence sharp along its length.", "4:3", None),
    ("ranch",
     "Photograph of a new three-rail wooden ranch fence with woven wire field fencing "
     "on the inside, along a green pasture in rural western Washington, a red barn "
     "far off, the snowy Cascade mountains faint on the horizon under a broken "
     "overcast sky. Early morning, mist in the low ground. 50mm, the fence line "
     "leading from the foreground into the distance.", "4:3", None),
    ("ornamental",
     "Photograph of a new black ornamental aluminum fence, four feet tall with flat-"
     "top pickets, along the front lawn of a craftsman-style house with a covered "
     "porch and grey shingle siding, rhododendrons in bloom along the fence line. "
     + PNW + " 35mm, from the sidewalk, three-quarter angle.", "4:3", None),
    ("finished-street",
     "Wide photograph of a finished western red cedar fence with a horizontal cap "
     "rail, seen from the street along the front of a corner lot, a driveway gate in "
     "matching cedar, a modest two-storey house behind with grey siding, wet asphalt "
     "in the foreground reflecting the overcast sky. " + PNW +
     " 35mm, camera at chest height.", "16:9", None),
    ("horizontal",
     "Photograph of a modern horizontal-board western red cedar fence, boards laid "
     "flat with narrow shadow gaps, black steel posts, along the side of a "
     "contemporary house with black window frames, a gravel and fern planting bed "
     "at its base. " + PNW + " 50mm, a slight angle so the boards recede.",
     "4:3", None),
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


def generate(name, prompt, aspect, ref, key, force):
    OUT.mkdir(parents=True, exist_ok=True)
    dest = OUT / f"{name}.jpg"
    if dest.exists() and not force:
        return f"{name}: skipped (exists)"
    parts = [{"text": f"{prompt} {NEGATIVE}"}]
    if ref:
        ref_path = OUT / f"{ref}.jpg"
        if not ref_path.exists():
            return f"{name}: reference {ref} not generated yet"
        parts.insert(0, {"inlineData": {
            "mimeType": "image/jpeg",
            "data": base64.b64encode(ref_path.read_bytes()).decode()}})
    data, err = request(parts, aspect, key)
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
    independent = [t for t in tasks if not t[3]]
    dependent = [t for t in tasks if t[3]]
    for batch in (independent, dependent):
        if not batch:
            continue
        with ThreadPoolExecutor(max_workers=4) as pool:
            for line in pool.map(
                    lambda t: generate(t[0], t[1], t[2], t[3], key, a.force), batch):
                print(f"  {line}", flush=True)


if __name__ == "__main__":
    main()
