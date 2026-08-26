#!/usr/bin/env python3
"""Give the builds a little motion: a scroll reveal and a hero fade.

One page in 140 had a keyframe animation before this. The pass is deliberately
small — motion is where a page starts to read as generated, so this is the
minimum that makes a page feel alive rather than a showcase of effects:

  * every section after the hero rises 14px and fades in the first time it
    enters the viewport, once;
  * gallery tiles do the same, staggered by their position in the band;
  * the hero photograph fades in over the first second of the page.

No library, no external request. The script is a few lines around an
IntersectionObserver; without JavaScript nothing is ever hidden, because the
hiding styles only apply under a class the script adds. `prefers-reduced-
motion` turns all of it off.

    python3 tools/build-motion.py hvac
    python3 tools/build-motion.py --all
    python3 tools/build-motion.py hvac --replace
"""

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
WORK = REPO / "work"
MARKER = "<!-- gsw:motion -->"
END_MARKER = "<!-- /gsw:motion -->"
# personal-injury is the photographic set and is left as it is.
SKIP = {"personal-injury"}

BLOCK = f"""{MARKER}
<style>
  /* Motion pass. Everything here is gated on .gsw-m, which only the script
     below adds, so a page without JavaScript never hides anything. */
  .gsw-m [data-gsw-reveal] {{
    opacity: 0; transform: translateY(14px);
    transition: opacity .7s cubic-bezier(.2,.6,.2,1), transform .7s cubic-bezier(.2,.6,.2,1);
  }}
  .gsw-m [data-gsw-reveal].gsw-in {{ opacity: 1; transform: none; }}
  .gsw-m .gsw-gal figure[data-gsw-reveal]:nth-child(2) {{ transition-delay: .08s; }}
  .gsw-m .gsw-gal figure[data-gsw-reveal]:nth-child(3) {{ transition-delay: .16s; }}
  .gsw-m .gsw-gal figure[data-gsw-reveal]:nth-child(4) {{ transition-delay: .24s; }}
  .gsw-m .gsw-gal figure[data-gsw-reveal]:nth-child(5) {{ transition-delay: .32s; }}
  .gsw-m .gsw-gal figure[data-gsw-reveal]:nth-child(6) {{ transition-delay: .40s; }}
  @keyframes gsw-hero-in {{ from {{ opacity: 0; transform: scale(1.025); }} to {{ opacity: 1; transform: none; }} }}
  .gsw-m .gsw-plate img, .gsw-m .gsw-backdrop img {{ animation: gsw-hero-in 1s ease-out both; }}
  @media (prefers-reduced-motion: reduce) {{
    .gsw-m [data-gsw-reveal] {{ opacity: 1; transform: none; transition: none; }}
    .gsw-m .gsw-plate img, .gsw-m .gsw-backdrop img {{ animation: none; }}
  }}
</style>
<script>
(function () {{
  if (!('IntersectionObserver' in window)) return;
  var targets = [].slice.call(document.querySelectorAll('body > section, .gsw-gal figure'));
  // The first section is the hero; it is on screen already and owns its own entrance.
  var first = document.querySelector('body > section');
  targets = targets.filter(function (el) {{ return el !== first; }});
  if (!targets.length) return;
  document.documentElement.classList.add('gsw-m');
  targets.forEach(function (el) {{ el.setAttribute('data-gsw-reveal', ''); }});
  var io = new IntersectionObserver(function (entries) {{
    entries.forEach(function (e) {{
      if (e.isIntersecting) {{ e.target.classList.add('gsw-in'); io.unobserve(e.target); }}
    }});
  }}, {{ rootMargin: '0px 0px -8% 0px', threshold: 0.08 }});
  targets.forEach(function (el) {{ io.observe(el); }});
}})();
</script>
{END_MARKER}
"""


def patch(page: Path, replace: bool) -> str:
    src = page.read_text()
    if MARKER in src:
        if not replace:
            return "already has motion"
        src = re.sub(re.escape(MARKER) + r".*?" + re.escape(END_MARKER) + r"\n?", "",
                     src, flags=re.S)
    if "</body>" not in src:
        return "no </body>"
    src = src.replace("</body>", BLOCK + "</body>", 1)
    page.write_text(src)
    return "motion added"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("trades", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--replace", action="store_true")
    args = ap.parse_args()

    if args.all:
        trades = sorted(p.name for p in WORK.iterdir()
                        if p.is_dir() and p.name != "_assets" and p.name not in SKIP)
    elif args.trades:
        trades = args.trades
    else:
        sys.exit("name at least one trade, or pass --all")

    for trade in trades:
        for page in sorted((WORK / trade).glob("*.html")):
            if page.name == "index.html":
                continue
            print(f"  {trade}/{page.stem:<34} {patch(page, args.replace)}")


if __name__ == "__main__":
    main()
