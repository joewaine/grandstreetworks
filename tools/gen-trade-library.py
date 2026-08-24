#!/usr/bin/env python3
"""Generate the shared per-trade image library the builds draw their gallery from.

The photography pass gave every build exactly one plate. One photograph is a
placeholder pattern, not a finished site: real trade sites carry a project
gallery, a before/after, process detail and a job-site shot.

The obvious move — a private library per build — is wrong. Six builds x 120
pages of their own photography blows the repo past 100MB, and a trade index page
already loads six full builds in iframes at once. So the split is:

    shared per trade   trade-generic texture, process, detail  <- this file
    unique per build   mark, favicon, social card, hero plate  <- identity kits

Sharing the trade-generic half is invisible to a visitor; the identity half is
what makes the six read as six businesses, and it costs almost nothing.

    python3 tools/gen-trade-library.py roofing
    python3 tools/gen-trade-library.py roofing --only damage-after --force

Needs GEMINI_API_KEY. Same model and negative prompt as cash_rich/gen_heroes.py.
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

REPO = Path(__file__).resolve().parent.parent
# Originals are 3-4MB each and are the source, not the deliverable: they live
# beside the hero library in cash_rich, exactly as hero_images does. The repo
# only ever carries the encoded ladder that build-responsive-images.py emits.
OUT = Path.home() / "fractal" / "cash_rich" / "trade_library"
MODEL = "gemini-3-pro-image"
URL = "https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={k}"
SIZE = "2K"

# Same rule the hero library was generated under. Faces stay out: these are
# invented businesses, and inventing identifiable people to staff them is a
# line the set has not crossed. Text stays out because a legible brand name
# baked into a shared image would break the sharing.
NEGATIVE = (
    "No text, no lettering, no signage, no logos, no watermarks, no UI elements. "
    "No recognisable faces. Nothing that reads as stock photography."
)

# `after` names an earlier image in the same set to pass back as a reference, so
# the before/after pair is demonstrably the same house rather than two houses.
LIBRARIES = {
    "cosmetic-dentists": [
        ("smile-a-before",
         "Clinical dental photograph cropped to the lower face only — lips and teeth, no eyes, no nose, no full face; the top edge of the frame sits below the nostrils. The photograph fills the entire frame edge to edge — no border, no letterboxing, no inset. Neutral grey backdrop, flat clinical lighting, unretouched, 100mm macro. "
         "Upper and lower front teeth heavily stained a dull yellow-brown from years of coffee and tea, the colour deepest near the gum line and between the teeth.", "4:3", None),
        ("smile-a-after",
         "The same mouth, the same lips, the same skin, and exactly the same framing, angle and lighting as the reference image, after professional cleaning and whitening: the teeth are now distinctly white, bright and clean — all staining, discolouration and deposit completely gone, surfaces polished and even. The change in shade must be dramatic and obvious at a glance while the teeth still look like real teeth with natural form and a little translucency at the edges. Keep the crop, the lip shape and the lighting identical; change only the teeth. ", "4:3", "smile-a-before"),
        ("smile-b-before",
         "Clinical dental photograph cropped to the lower face only — lips and teeth, no eyes, no nose, no full face; the top edge of the frame sits below the nostrils. The photograph fills the entire frame edge to edge — no border, no letterboxing, no inset. Neutral grey backdrop, flat clinical lighting, unretouched, 100mm macro. "
         "Upper front teeth deeply yellowed with brown nicotine staining and visible hardened tartar along the gum line, plus a gap between the central incisors.", "4:3", None),
        ("smile-b-after",
         "The same mouth, the same lips, the same skin, and exactly the same framing, angle and lighting as the reference image, after professional cleaning and whitening: the teeth are now distinctly white, bright and clean — all staining, discolouration and deposit completely gone, surfaces polished and even. The change in shade must be dramatic and obvious at a glance while the teeth still look like real teeth with natural form and a little translucency at the edges. Keep the crop, the lip shape and the lighting identical; change only the teeth. ", "4:3", "smile-b-before"),
        ("smile-c-before",
         "Clinical dental photograph cropped to the lower face only — lips and teeth, no eyes, no nose, no full face; the top edge of the frame sits below the nostrils. The photograph fills the entire frame edge to edge — no border, no letterboxing, no inset. Neutral grey backdrop, flat clinical lighting, unretouched, 100mm macro. "
         "Upper front teeth discoloured a blotchy yellow-grey with dark staining in the gaps between them, and a chipped corner on one central incisor.", "4:3", None),
        ("smile-c-after",
         "The same mouth, the same lips, the same skin, and exactly the same framing, angle and lighting as the reference image, after professional cleaning and whitening: the teeth are now distinctly white, bright and clean — all staining, discolouration and deposit completely gone, surfaces polished and even. The change in shade must be dramatic and obvious at a glance while the teeth still look like real teeth with natural form and a little translucency at the edges. Keep the crop, the lip shape and the lighting identical; change only the teeth. ", "4:3", "smile-c-before"),
        ("smile-d-before",
         "Clinical dental photograph cropped to the lower face only — lips and teeth, no eyes, no nose, no full face; the top edge of the frame sits below the nostrils. The photograph fills the entire frame edge to edge — no border, no letterboxing, no inset. Neutral grey backdrop, flat clinical lighting, unretouched, 100mm macro. "
         "Upper front teeth yellowed and dulled, the edges worn flat and square from grinding, with brown staining collected in the worn surfaces.", "4:3", None),
        ("smile-d-after",
         "The same mouth, the same lips, the same skin, and exactly the same framing, angle and lighting as the reference image, after professional cleaning and whitening: the teeth are now distinctly white, bright and clean — all staining, discolouration and deposit completely gone, surfaces polished and even. The change in shade must be dramatic and obvious at a glance while the teeth still look like real teeth with natural form and a little translucency at the edges. Keep the crop, the lip shape and the lighting identical; change only the teeth. ", "4:3", "smile-d-before"),
        ("smile-e-before",
         "Clinical dental photograph cropped to the lower face only — lips and teeth, no eyes, no nose, no full face; the top edge of the frame sits below the nostrils. The photograph fills the entire frame edge to edge — no border, no letterboxing, no inset. Neutral grey backdrop, flat clinical lighting, unretouched, 100mm macro. "
         "Upper front teeth badly discoloured, with two dark ageing composite repairs on the central incisors that have gone brown against an already yellow arch.", "4:3", None),
        ("smile-e-after",
         "The same mouth, the same lips, the same skin, and exactly the same framing, angle and lighting as the reference image, after professional cleaning and whitening: the teeth are now distinctly white, bright and clean — all staining, discolouration and deposit completely gone, surfaces polished and even. The change in shade must be dramatic and obvious at a glance while the teeth still look like real teeth with natural form and a little translucency at the edges. Keep the crop, the lip shape and the lighting identical; change only the teeth. ", "4:3", "smile-e-before"),
        ("smile-f-before",
         "Clinical dental photograph cropped to the lower face only — lips and teeth, no eyes, no nose, no full face; the top edge of the frame sits below the nostrils. The photograph fills the entire frame edge to edge — no border, no letterboxing, no inset. Neutral grey backdrop, flat clinical lighting, unretouched, 100mm macro. "
         "Upper front teeth stained an uneven grey-brown with dark horizontal banding through the enamel and heavy deposit along the gum line.", "4:3", None),
        ("smile-f-after",
         "The same mouth, the same lips, the same skin, and exactly the same framing, angle and lighting as the reference image, after professional cleaning and whitening: the teeth are now distinctly white, bright and clean — all staining, discolouration and deposit completely gone, surfaces polished and even. The change in shade must be dramatic and obvious at a glance while the teeth still look like real teeth with natural form and a little translucency at the edges. Keep the crop, the lip shape and the lighting identical; change only the teeth. ", "4:3", "smile-f-before"),
        ("chairside-preview",
         "Documentary photograph of a dental surgery: a large monitor on an articulated "
         "arm showing an abstract, unreadable three-dimensional render, a clinician's "
         "gloved hands at the edge of frame, no face. Calm oak and off-white room, "
         "daylight from the left. 35mm, shallow depth of field.", "4:3", None),
        ("shade-guide",
         "Close documentary photograph of a porcelain shade guide fanned out on a clean "
         "white worktop beside a small mirror, tabs graded from warm to bright. Soft "
         "daylight, strong shallow focus on the middle tabs. 100mm macro.", "4:3", None),
    ],
    "roofing": [
        ("tear-off",
         "Documentary photograph of a roofing crew stripping old asphalt shingles from "
         "a suburban roof, seen from behind and above so no face is in frame. Torn felt, "
         "a flat bar, stacked debris. Overcast midday light, honest and unstyled. 35mm.",
         "4:3", None),
        ("underlayment",
         "Documentary photograph of synthetic roofing underlayment rolled out over fresh "
         "plywood decking, one course half-unrolled, cap nails in a neat line. Bright "
         "diffuse daylight, strong texture. 50mm, slight top-down angle.", "4:3", None),
        ("courses",
         "Close documentary photograph of new architectural asphalt shingles being laid "
         "in courses, a nail gun and one gloved hand at the edge of frame, no face. "
         "Raking afternoon light picking out the granule texture. 50mm.", "4:3", None),
        ("ridge-vent",
         "Close documentary photograph of a finished ridge line on an asphalt shingle "
         "roof — ridge cap shingles over a low-profile ridge vent, clean straight run "
         "against open sky. Late afternoon light. 85mm compression.", "4:3", None),
        ("flashing",
         "Close documentary photograph of new step flashing where an asphalt shingle "
         "roof meets a brick chimney, counter-flashing tucked into the mortar joint, "
         "sealant line neat. Hard directional sun. 85mm, shallow depth of field.",
         "4:3", None),
        ("drip-edge",
         "Close documentary photograph of a new aluminium drip edge and seamless gutter "
         "along a roof eave, shingle overhang crisp above it, soffit below in shadow. "
         "Clear morning light. 50mm.", "4:3", None),
        ("damage-before",
         "Documentary photograph of a storm-damaged suburban roof: a patch of asphalt "
         "shingles torn away exposing dark underlayment, lifted tabs around it, a blue "
         "tarp weighted at one edge. Flat grey light after rain, wet shingles. 35mm, "
         "three-quarter view of the roof plane from a neighbouring height.", "4:3", None),
        ("damage-after",
         "Documentary photograph of the same house and the same roof plane from the same "
         "angle and distance, now fully re-shingled: continuous new architectural "
         "shingles, no tarp, no missing tabs, clean ridge. Keep the house, the roof "
         "geometry, the surroundings and the framing identical to the reference image; "
         "change only the roof condition and give it clear light after the storm.",
         "4:3", "damage-before"),
        ("jobsite",
         "Documentary photograph of a tidy residential roofing job site: a pickup truck "
         "with ladders on the rack, a small debris container on plywood protecting the "
         "driveway, bundles of shingles stacked. No people in frame. Early morning, long "
         "shadows. 35mm.", "4:3", None),
        ("finished-home",
         "Photograph of a well-kept suburban two-storey house with a newly finished "
         "architectural shingle roof, shot from the front garden. Warm late-afternoon "
         "light, deep blue sky, mature planting. Wide establishing view. 35mm.",
         "16:9", None),
    ],
}


def request(parts: list, size: str, aspect: str, key: str, retries: int = 3):
    body = {"contents": [{"parts": parts}],
            "generationConfig": {"imageConfig": {"aspectRatio": aspect,
                                                 "imageSize": size}}}
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


def generate(trade: str, name: str, prompt: str, aspect: str, ref: str | None,
             key: str, force: bool) -> str:
    out_dir = OUT / trade
    out_dir.mkdir(parents=True, exist_ok=True)
    dest = out_dir / f"{name}.jpg"
    if dest.exists() and not force:
        return f"{name}: skipped (exists)"

    parts: list = [{"text": f"{prompt} {NEGATIVE}"}]
    if ref:
        ref_path = out_dir / f"{ref}.jpg"
        if not ref_path.exists():
            return f"{name}: reference {ref} not generated yet"
        parts.insert(0, {"inlineData": {
            "mimeType": "image/jpeg",
            "data": base64.b64encode(ref_path.read_bytes()).decode()}})

    data, err = request(parts, SIZE, aspect, key)
    if err:
        return f"{name}: {err}"
    dest.write_bytes(data)
    return f"{name}: {len(data) // 1024}KB"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("trade")
    ap.add_argument("--only", nargs="*", help="generate just these names")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        sys.exit("GEMINI_API_KEY not set")
    items = LIBRARIES.get(args.trade)
    if not items:
        sys.exit(f"no library defined for {args.trade}")
    if args.only:
        items = [i for i in items if i[0] in args.only]

    # Reference-chained entries have to run after what they point at.
    independent = [i for i in items if not i[3]]
    dependent = [i for i in items if i[3]]

    for batch in (independent, dependent):
        if not batch:
            continue
        with ThreadPoolExecutor(max_workers=4) as pool:
            for line in pool.map(
                    lambda i: generate(args.trade, i[0], i[1], i[2], i[3],
                                       key, args.force), batch):
                print(f"  {line}")


if __name__ == "__main__":
    main()
