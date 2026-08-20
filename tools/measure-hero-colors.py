#!/usr/bin/env python3
"""Record each backdrop hero's own background colour, measured in a browser.

A scrim only protects legibility if it is the colour the design already uses
behind that text. Parsing it out of the stylesheet is guesswork — the value is
usually a custom property resolved several rules deep — so we ask Chrome what
it actually painted, and cache the answer.

    python3 tools/measure-hero-colors.py            # needs the dev server up
    python3 tools/measure-hero-colors.py --port 8777

Writes tools/hero_colors.json. Re-run after adding a trade to hero_backdrops.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "tools" / "hero_colors.json"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

PROBE = """<script>window.addEventListener("load",function(){
 var h=document.querySelector("section");
 var el=h, bg="rgba(0, 0, 0, 0)";
 while(el && bg==="rgba(0, 0, 0, 0)"){ bg=getComputedStyle(el).backgroundColor; el=el.parentElement; }
 var t=h.querySelector("h1")||h;
 document.title="GSW|"+bg+"|"+getComputedStyle(t).color;
});</script></body>"""


def measure(url, page_path):
    probe = page_path.with_suffix(".gswprobe.html")
    probe.write_text(page_path.read_text().replace("</body>", PROBE, 1))
    try:
        out = subprocess.run(
            [CHROME, "--headless=new", "--disable-gpu", "--virtual-time-budget=8000",
             "--dump-dom", url.replace(page_path.name, probe.name)],
            capture_output=True, text=True, timeout=90).stdout
        m = re.search(r"<title>GSW\|([^|]+)\|([^<]+)</title>", out)
        return (m.group(1), m.group(2)) if m else (None, None)
    finally:
        probe.unlink(missing_ok=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8777)
    args = ap.parse_args()

    sys.path.insert(0, str(REPO / "tools"))
    from hero_backdrops import BACKDROPS

    colors = json.loads(OUT.read_text()) if OUT.exists() else {}
    for trade, indexes in BACKDROPS.items():
        pages = sorted((REPO / "work" / trade).glob("*.html"))
        pages = [p for p in pages if p.name != "index.html"]
        for p in pages:
            url = f"http://localhost:{args.port}/work/{trade}/{p.name}"
            bg, fg = measure(url, p)
            if not bg:
                print(f"  ! {trade}/{p.name}: no reading")
                continue
            colors[f"{trade}/{p.name}"] = {"bg": bg, "fg": fg}
            print(f"  {trade}/{p.name:<38} {bg:<24} text {fg}")
    OUT.write_text(json.dumps(colors, indent=1, sort_keys=True))
    print(f"\nwrote {len(colors)} readings to {OUT.relative_to(REPO)}")


if __name__ == "__main__":
    main()
