#!/usr/bin/env python3
"""Bring a build's hero device in, one part at a time.

Several designs draw their argument as a small mechanism beside the headline —
a portal checklist whose rows are all already ticked, a ledger with a row still
open, a four-station year. Statically they read as a screenshot. Revealed in
sequence they read as the thing working, which is what the copy is claiming.

Each part fades and rises together with a stagger, and where a part is a tick
or a checkbox its mark draws in after its row has landed. The whole thing runs
once, when the device first scrolls into view, and never on a page the visitor
has scrolled past.

Everything is gated on a class the script adds, so a device is fully visible
before this runs and stays visible if it never does. `prefers-reduced-motion`
turns the movement off and leaves the marks drawn.

    python3 tools/animate-hero-devices.py accounting-cpas
    python3 tools/animate-hero-devices.py accounting-cpas --replace
"""

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
WORK = REPO / "work"
MARKER = "gsw-seq"

# build slug -> (container class, part selectors in reveal order, mark selector)
# `mark` names the element inside a part that draws itself in last: a tick, a
# checkbox, a station dot. None where the part has no such mark.
DEVICES = {
    "accounting-cpas": {
        "ashby-and-kerr-cpas": ("plist", "li", ".chk"),
        "latimer-accounting": ("ledger", ".ledrow", ".tick"),
        "rennick-cpa": ("track", ".station", None),
    },
}


def css(container: str, part: str, mark: str | None) -> str:
    mark_rules = ""
    if mark:
        mark_rules = f"""
  .{MARKER}-on .{container} {part} {mark} {{
    opacity: 0; transform: scale(.72);
    transition: opacity .28s ease, transform .28s cubic-bezier(.2,1.5,.4,1);
  }}
  .{MARKER}-on .{container} {part}.{MARKER}-in {mark} {{
    opacity: 1; transform: none; transition-delay: .34s;
  }}"""
    return f"""
<style>
  /* {MARKER}: the hero device arrives a part at a time. Gated on .{MARKER}-on,
     which only the script adds, so without JavaScript the device is simply
     there. */
  .{MARKER}-on .{container} {part} {{
    opacity: 0; transform: translateY(9px);
    transition: opacity .5s cubic-bezier(.2,.6,.2,1), transform .5s cubic-bezier(.2,.6,.2,1);
  }}
  .{MARKER}-on .{container} {part}.{MARKER}-in {{ opacity: 1; transform: none; }}{mark_rules}
  @media (prefers-reduced-motion: reduce) {{
    .{MARKER}-on .{container} {part},
    .{MARKER}-on .{container} {part} {mark or "*"} {{
      opacity: 1; transform: none; transition: none;
    }}
  }}
</style>"""


def script(container: str, part: str) -> str:
    return f"""
<script>
/* One device per page. Parts land left to right (or top to bottom) 110ms
   apart, once, the first time the device is on screen. */
(function () {{
  var box = document.querySelector('.{container}');
  if (!box || !('IntersectionObserver' in window)) return;
  var parts = box.querySelectorAll('{part}');
  if (!parts.length) return;
  document.documentElement.classList.add('{MARKER}-on');
  var run = function () {{
    parts.forEach(function (p, i) {{
      setTimeout(function () {{ p.classList.add('{MARKER}-in'); }}, i * 110);
    }});
  }};
  var io = new IntersectionObserver(function (entries) {{
    entries.forEach(function (e) {{
      if (e.isIntersecting) {{ run(); io.disconnect(); }}
    }});
  }}, {{ threshold: 0.35 }});
  io.observe(box);
}})();
</script>"""


def patch(page: Path, spec, replace: bool) -> str:
    container, part, mark = spec
    src = page.read_text()
    if MARKER in src:
        if not replace:
            return "already animated"
        src = re.sub(rf"\n<style>\n  /\* {MARKER}:.*?</style>", "", src, flags=re.S)
        src = re.sub(rf"\n<script>\n/\* One device per page\..*?</script>", "", src, flags=re.S)

    if not re.search(rf'class="[^"]*\b{container}\b', src):
        return f"no .{container} found"
    src = src.replace("</head>", css(container, part, mark) + "\n</head>", 1)
    src = src.replace("</body>", script(container, part) + "\n</body>", 1)
    page.write_text(src)
    return "animated"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("trades", nargs="+")
    ap.add_argument("--replace", action="store_true")
    args = ap.parse_args()

    for trade in args.trades:
        builds = DEVICES.get(trade)
        if not builds:
            print(f"  {trade}: no devices defined")
            continue
        for slug, spec in builds.items():
            page = WORK / trade / f"{slug}.html"
            status = patch(page, spec, args.replace) if page.exists() else "page missing"
            print(f"  {slug:<34} {status}")


if __name__ == "__main__":
    main()
