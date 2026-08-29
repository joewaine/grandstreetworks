#!/usr/bin/env python3
"""Animate a hero plate into an 8-second Veo clip, image-to-video.

The plates under ~/fractal/cash_rich/hero_images are Gemini-generated, which
is what keeps 120 invented businesses free of stock-site faces and other
people's premises. A stock clip breaks that: it is a real roofer on a real
roof, with a model release the invented business does not hold. Veo 3.1's
image-to-video takes the plate the build already opens on and moves it, so
the video hero is the still hero, breathing, and nothing new needs licensing.

    python3 tools/gen-hero-video.py roofing a-storm-clearing \\
        --motion "clouds drift after the storm, light moves across the wet shingles"
    python3 tools/gen-hero-video.py roofing a-storm-clearing --model standard --force

Writes ~/fractal/cash_rich/hero_video/<trade>/<stem>.mp4 (the original, kept
outside the repo like every other original) plus a .json sidecar recording the
prompt and model, then prints the encode command that turns it into the
2MB loop the page can afford. Needs GEMINI_API_KEY (source ~/.gemini/.env).

Veo always renders audio; encode-hero-video.py strips it. Output carries an
invisible SynthID watermark. The server keeps the file for two days, which is
why this downloads immediately rather than handing back a URI.
"""

import argparse
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

HERO_IMAGES = Path.home() / "fractal" / "cash_rich" / "hero_images"
HERO_VIDEO = Path.home() / "fractal" / "cash_rich" / "hero_video"
API = "https://generativelanguage.googleapis.com/v1beta/"

# Gemini API list prices, $/second, 1080p with audio (Aug 2026). Printed so the
# spend is visible before the request goes out.
MODELS = {
    "lite":     ("veo-3.1-lite-generate-preview", 0.08),
    "fast":     ("veo-3.1-fast-generate-preview", 0.12),
    "standard": ("veo-3.1-generate-preview",      0.40),
}
# 1080p and 4k are only offered at 8 seconds; 8 is also what the loop wants.
DURATION = 8
POLL_SECONDS = 10
TIMEOUT_SECONDS = 15 * 60

# The plate is the composition; the clip must not re-stage it. "Slow push-in"
# was tried first and Veo turned it into a travelling shot along the roof, so
# the loop's head and tail no longer matched and the crossfade ghosted. A
# locked-off camera is what it actually honours, and a static frame with only
# weather and light moving loops invisibly.
CAMERA = {
    "locked": ("Locked-off tripod shot: the camera does not move, pan, tilt, "
               "zoom or drift at all. The framing is identical to the image "
               "from the first frame to the last."),
    "push":   ("Very slow, steady push-in on the same framing, no cuts, no pans."),
}
STYLE = ("Cinematic, photorealistic, documentary. {camera} "
         "Natural motion only: {motion}. "
         "No people enter the frame, no text, no lettering, no logos. "
         "Colour, light and weather stay as they are in the image.")


def api_key():
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        sys.exit("GEMINI_API_KEY not set: source ~/.gemini/.env")
    return key


def request(method, url, key, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "x-goog-api-key": key, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit("%s %s -> %s\n%s" % (method, url.split("?")[0], e.code,
                                      e.read().decode(errors="replace")[:2000]))


def submit(key, model, plate, prompt, resolution):
    body = {
        "instances": [{
            "prompt": prompt,
            # predictLongRunning takes the Vertex-style shape, not Gemini's
            # inlineData; the API rejects the latter with a 400.
            "image": {"bytesBase64Encoded": base64.b64encode(plate.read_bytes()).decode(),
                      "mimeType": "image/jpeg"},
        }],
        "parameters": {
            "aspectRatio": "16:9",
            "resolution": resolution,
            "durationSeconds": DURATION,
        },
    }
    op = request("POST", API + "models/%s:predictLongRunning" % model, key, body)
    return op["name"]


def wait(key, op_name):
    deadline = time.time() + TIMEOUT_SECONDS
    while time.time() < deadline:
        op = request("GET", API + op_name, key)
        if op.get("done"):
            if "error" in op:
                sys.exit("generation failed: %s" % json.dumps(op["error"])[:1000])
            resp = op.get("response", {})
            samples = resp.get("generateVideoResponse", {}).get("generatedSamples", [])
            if not samples:
                # Safety filters report here rather than as an error.
                sys.exit("no video returned:\n%s" % json.dumps(resp, indent=1)[:2000])
            return samples[0]["video"]["uri"]
        print("  ...rendering", flush=True)
        time.sleep(POLL_SECONDS)
    sys.exit("timed out after %ds waiting on %s" % (TIMEOUT_SECONDS, op_name))


def download(key, uri, dest):
    req = urllib.request.Request(uri, headers={"x-goog-api-key": key})
    with urllib.request.urlopen(req, timeout=300) as r:
        # Google redirects to a signed URL; urllib follows it and keeps the header.
        dest.write_bytes(r.read())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("trade")
    ap.add_argument("stem", help="plate basename without .jpg, e.g. a-storm-clearing")
    ap.add_argument("--motion", required=True,
                    help="what moves, in a phrase: 'clouds drift, branches sway'")
    ap.add_argument("--model", choices=MODELS, default="fast")
    ap.add_argument("--resolution", choices=["720p", "1080p", "4k"], default="1080p")
    ap.add_argument("--camera", choices=CAMERA, default="locked")
    ap.add_argument("--suffix", default="",
                    help="name the output <stem>-<suffix> to keep an earlier take")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    plate = HERO_IMAGES / args.trade / ("%s.jpg" % args.stem)
    if not plate.exists():
        sys.exit("no plate at %s" % plate)
    out_stem = args.stem + ("-%s" % args.suffix if args.suffix else "")
    dest = HERO_VIDEO / args.trade / ("%s.mp4" % out_stem)
    if dest.exists() and not args.force:
        sys.exit("%s exists; --force to regenerate (it costs money)" % dest)

    key = api_key()
    model, rate = MODELS[args.model]
    prompt = STYLE.format(camera=CAMERA[args.camera], motion=args.motion)
    print("model    %s  (~$%.2f for %ds at %s)" % (model, rate * DURATION, DURATION,
                                                  args.resolution))
    print("plate    %s" % plate.relative_to(Path.home()))

    started = time.time()
    op_name = submit(key, model, plate, prompt, args.resolution)
    print("op       %s" % op_name)
    uri = wait(key, op_name)

    dest.parent.mkdir(parents=True, exist_ok=True)
    download(key, uri, dest)
    dest.with_suffix(".json").write_text(json.dumps({
        "model": model, "prompt": prompt, "resolution": args.resolution,
        "duration": DURATION, "camera": args.camera, "plate": str(plate),
        "operation": op_name,
    }, indent=1))
    print("wrote    %s  %.1f MB in %ds" % (dest.relative_to(Path.home()),
                                          dest.stat().st_size / 1e6, time.time() - started))
    print("\nnext:\n  python3 tools/encode-hero-video.py %s --name %s "
          "--dest work/_assets/hero/%s --seamless 1" % (dest, out_stem, args.trade))


if __name__ == "__main__":
    main()
