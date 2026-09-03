#!/usr/bin/env python3
"""Animate one of the Zach Becker aerial plates into an 8s Veo clip
(image-to-video) for the hero loop. Same API shape as gen-hero-video.py,
different plate folder.

    python3 tools/gen-zach-becker-video.py lake-washington-dusk --camera drone
    python3 tools/gen-zach-becker-video.py lake-washington-dusk --camera locked --suffix locked

Writes ~/fractal/clients/zach-becker/video/<stem>[-suffix].mp4 + .json.
Needs GEMINI_API_KEY (source ~/.gemini/.env). ~$0.96 per take on veo fast.
"""
import argparse, base64, json, os, sys, time, urllib.error, urllib.request
from pathlib import Path

PLATES = Path.home() / "fractal/clients/zach-becker/originals/aerials"
OUT = Path.home() / "fractal/clients/zach-becker/video"
API = "https://generativelanguage.googleapis.com/v1beta/"
MODELS = {"fast": "veo-3.1-fast-generate-preview", "standard": "veo-3.1-generate-preview"}
CAMERA = {
    "locked": "Locked-off shot: the camera does not move, pan, tilt, zoom or drift at all; the framing is identical from first frame to last. Only the water surface, the light and a few clouds move.",
    "drone":  "A drone hovering almost still, drifting forward very slowly and evenly over the water toward the far shore, no pans, no tilts, no cuts; the horizon stays level and in the same place.",
}
STYLE = ("Cinematic, photorealistic aerial real-estate footage of Lake Washington at dusk. {camera} "
         "Natural motion only: gentle ripples on the lake, soft light shifting on the far city, boats still. "
         "No people, no text, no lettering, no logos. Colour, light and weather stay exactly as in the image.")

def key():
    k = os.environ.get("GEMINI_API_KEY")
    if not k:
        for line in (Path.home()/".gemini/.env").read_text().splitlines():
            if line.startswith("GEMINI_API_KEY="): k = line.split("=",1)[1].strip().strip('"')
    if not k: sys.exit("GEMINI_API_KEY not set")
    return k

def req(method, url, k, body=None):
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(url, data=data, method=method,
        headers={"x-goog-api-key": k, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(r, timeout=120) as resp: return json.load(resp)
    except urllib.error.HTTPError as e:
        sys.exit("%s %s -> %s\n%s" % (method, url.split("?")[0], e.code, e.read().decode(errors="replace")[:1500]))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stem"); ap.add_argument("--camera", choices=CAMERA, default="drone")
    ap.add_argument("--model", choices=MODELS, default="fast"); ap.add_argument("--suffix", default="")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    plate = PLATES / (a.stem + ".jpg")
    if not plate.exists(): sys.exit("no plate %s" % plate)
    dest = OUT / ("%s%s.mp4" % (a.stem, "-" + a.suffix if a.suffix else ""))
    if dest.exists() and not a.force: sys.exit("%s exists" % dest)
    k = key(); model = MODELS[a.model]
    prompt = STYLE.format(camera=CAMERA[a.camera])
    body = {"instances": [{"prompt": prompt,
             "image": {"bytesBase64Encoded": base64.b64encode(plate.read_bytes()).decode(), "mimeType": "image/jpeg"}}],
            "parameters": {"aspectRatio": "16:9", "resolution": "1080p", "durationSeconds": 8}}
    t0 = time.time()
    op = req("POST", API + "models/%s:predictLongRunning" % model, k, body)["name"]
    print("op", op, flush=True)
    while time.time() - t0 < 900:
        o = req("GET", API + op, k)
        if o.get("done"):
            if "error" in o: sys.exit("failed: %s" % json.dumps(o["error"])[:800])
            s = o.get("response", {}).get("generateVideoResponse", {}).get("generatedSamples", [])
            if not s: sys.exit("no video: %s" % json.dumps(o)[:800])
            uri = s[0]["video"]["uri"]; break
        time.sleep(10)
    else:
        sys.exit("timeout")
    OUT.mkdir(parents=True, exist_ok=True)
    r = urllib.request.Request(uri, headers={"x-goog-api-key": k})
    with urllib.request.urlopen(r, timeout=300) as resp: dest.write_bytes(resp.read())
    dest.with_suffix(".json").write_text(json.dumps({"model": model, "prompt": prompt, "plate": str(plate), "camera": a.camera, "op": op}, indent=1))
    print("wrote", dest, "%.1f MB in %ds" % (dest.stat().st_size/1e6, time.time()-t0))

if __name__ == "__main__": main()
