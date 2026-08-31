#!/usr/bin/env python3
"""Count the hero's headline numbers up from zero when they come into view.

A board of figures — a fee, a guarantee, a placement time — reads as a claim
when it sits still and as a result when it arrives. This adds one small
script to a build that animates the numbers in the elements a selector
picks: each is parsed as an optional prefix, a number and a suffix
("20%", "90d", "$1.2m", "1"), counts from zero to its value over about a
second with an ease-out, staggered a little, and settles on the original
text so nothing depends on the script having run. Reduced motion shows the
figures as they are.

    python3 tools/add-countup.py recruiting copperfield-industrial-search ".board .brow b"
    python3 tools/add-countup.py recruiting copperfield-industrial-search ".board .brow b" --replace

Idempotent; the block sits between gsw:countup markers before </body>.
"""

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
WORK = REPO / "work"
MARKER = "<!-- gsw:countup -->"
END_MARKER = "<!-- /gsw:countup -->"

SCRIPT = """
<script>
/* gsw:countup — the figures in SELECTOR count up from zero once they are on
   screen. The text is parsed, not replaced: whatever was written is what the
   count settles on, so the page reads the same with the script off. */
(function () {
  var els = document.querySelectorAll(SELECTOR);
  if (!els.length) return;
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  var DURATION = 1100, STAGGER = 120;
  var parse = function (text) {
    var m = /^([^0-9]*)([0-9][0-9,]*(?:\\.[0-9]+)?)(.*)$/.exec(text.trim());
    if (!m) return null;
    var num = parseFloat(m[2].replace(/,/g, ''));
    var decimals = (m[2].split('.')[1] || '').length;
    var grouped = m[2].indexOf(',') !== -1;
    return { prefix: m[1], value: num, decimals: decimals, grouped: grouped, suffix: m[3], text: text };
  };
  var format = function (p, v) {
    var s = v.toFixed(p.decimals);
    if (p.grouped) s = s.replace(/\\B(?=(\\d{3})+(?!\\d))/g, ',');
    return p.prefix + s + p.suffix;
  };
  var run = function (el, p, delay) {
    var start = null;
    var frame = function (t) {
      if (start === null) start = t + delay;
      var k = Math.min(1, Math.max(0, (t - start) / DURATION));
      var eased = 1 - Math.pow(1 - k, 3);
      el.textContent = k < 1 ? format(p, p.value * eased) : p.text;
      if (k < 1) requestAnimationFrame(frame);
    };
    requestAnimationFrame(frame);
  };
  var items = [];
  els.forEach(function (el) {
    var p = parse(el.textContent);
    if (p) { items.push([el, p]); el.textContent = format(p, 0); }
  });
  if (!items.length) return;
  var started = false;
  var go = function () {
    if (started) return;
    started = true;
    items.forEach(function (it, i) { run(it[0], it[1], i * STAGGER); });
  };
  if (!('IntersectionObserver' in window)) { go(); return; }
  var io = new IntersectionObserver(function (entries) {
    if (entries.some(function (e) { return e.isIntersecting; })) { go(); io.disconnect(); }
  }, { threshold: 0.3 });
  io.observe(items[0][0]);
})();
</script>"""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("trade")
    ap.add_argument("slug")
    ap.add_argument("selector")
    ap.add_argument("--replace", action="store_true")
    args = ap.parse_args()
    page = WORK / args.trade / f"{args.slug}.html"
    if not page.exists():
        sys.exit(f"{page}: missing")
    src = page.read_text()
    if MARKER in src:
        if not args.replace:
            print(f"  {args.slug:<34} already has a count-up")
            return
        src = re.sub(re.escape(MARKER) + r".*?" + re.escape(END_MARKER) + r"\n?", "", src, flags=re.S)
    block = MARKER + SCRIPT.replace("SELECTOR", json.dumps(args.selector)) + "\n" + END_MARKER + "\n"
    src = src.replace("</body>", block + "</body>", 1)
    page.write_text(src)
    print(f"  {args.slug:<34} count-up added ({args.selector})")


if __name__ == "__main__":
    main()
