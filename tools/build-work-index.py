#!/usr/bin/env python3
"""Regenerate work/<industry>/index.html in Grand Street Works branding.

Not part of deploying — Render publishes the repo as-is and there is no build
step. This is a maintenance tool, run by hand when a new batch of reference
builds is copied in from cash_rich.

    python3 tools/build-work-index.py                     # default source
    python3 tools/build-work-index.py --source <dir>      # another demos dir

Source of truth is the demo harness's own index.html in cash_rich/demos, which
carries the direction names, the FIX each one answers, the axis picks and the
accent swatch. This reads those, throws away the harness styling, and writes a
page in the site's design system with a live preview frame.

Re-runnable: it always parses the harness format from --source, never the page
it previously wrote, so running it twice is a no-op.
"""

import argparse
import html
import re
import sys
from pathlib import Path

DEFAULT_SOURCE = Path.home() / "fractal" / "cash_rich" / "demos"
REPO = Path(__file__).resolve().parent.parent
WORK = REPO / "work"

# Labels must match the SEC_04 work grid on the home page.
INDUSTRIES = {
    "01-personal-injury": "Personal injury",
    "02-cosmetic-dentists": "Cosmetic dentistry",
    "03-plastic-surgeons": "Plastic surgery",
    "04-med-spas": "Med spas",
    "05-dermatology": "Dermatology",
    "06-roofing": "Roofing",
    "07-hvac": "Heating &amp; cooling",
    "08-restoration": "Restoration",
    "09-general-contractors": "General contracting",
    "10-luxury-real-estate": "Luxury real estate",
    "11-wealth-management": "Wealth management",
    "12-accounting-cpas": "Accounting &amp; CPAs",
    "13-architecture": "Architecture",
    "14-interior-design": "Interior design",
    "15-custom-home-builders": "Custom home building",
    "16-pool-builders": "Pool building",
    "17-solar": "Solar",
    "18-recruiting": "Recruiting",
    "19-property-management": "Property management",
    "20-veterinary": "Veterinary",
}

# The demo harness emitted a few different card shapes over the twenty builds —
# some carry an accent swatch, some put the accent in a border-left-color, one
# numbers the cards, and a couple use &middot; rather than a literal ·. Match the
# fields independently inside each <li> rather than pinning one exact shape.
LI_RE = re.compile(r"<li>(.*?)</li>", re.S)
HREF_RE = re.compile(r'href="([^"]+)"')
NAME_RE = re.compile(r'class="name">(.*?)</div>', re.S)
WHY_RE = re.compile(r'class="why">(.*?)</p>', re.S)
AXES_RE = re.compile(r'class="axes"[^>]*>(.*?)</p>', re.S)
SW_RE = re.compile(r'class="sw"[^>]*background:\s*([^;"]+)')
BORDER_RE = re.compile(r"border-left-color:\s*([^;\"]+)")
LEADING_SW_RE = re.compile(r'^\s*<span class="sw"[^>]*></span>\s*')


FAVICON = (
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E"
    "%3Crect width='64' height='64' fill='%23050505'/%3E"
    "%3Ccircle cx='14' cy='14' r='5' fill='%23C2D57D'/%3E"
    "%3Ctext x='32' y='50' font-family='Menlo,Consolas,monospace' font-size='26'"
    " font-weight='bold' fill='%23E5E5E6' text-anchor='middle'%3EGW%3C/text%3E%3C/svg%3E"
)


def parse(src_index: Path):
    s = src_index.read_text()

    m = re.search(r"<title>(.*?)\s+—\s+six directions</title>", s)
    if not m:
        raise ValueError(f"no company name in {src_index}")
    # unescaped here, re-escaped at render time — otherwise "&amp;" doubles up
    company = html.unescape(m.group(1).strip())

    m = re.search(r'<p class="sub">(.*?)</p>', s, re.S)
    sub = " ".join(m.group(1).split()) if m else ""
    # The harness repeats the industry as a leading sentence; the section bar
    # says it now, so drop it.
    sub = re.sub(r"^[^.]+\.\s+(?=Fictional)", "", sub)

    m = re.search(r"<footer>(.*?)</footer>", s, re.S)
    disclaimer = " ".join(m.group(1).split()) if m else ""

    directions = []
    for chunk in LI_RE.findall(s):
        href = HREF_RE.search(chunk)
        name = NAME_RE.search(chunk)
        if not href or not name:
            continue
        why = WHY_RE.search(chunk)
        axes = AXES_RE.search(chunk)
        accent = SW_RE.search(chunk) or BORDER_RE.search(chunk)

        plain = " ".join(html.unescape(name.group(1)).split())
        code, _, label = plain.partition(" · ")

        axes_html = " ".join(axes.group(1).split()) if axes else ""
        axes_html = LEADING_SW_RE.sub("", axes_html)

        directions.append(
            {
                "href": href.group(1),
                "code": code.strip() or "D?",
                "label": label.strip() or plain,
                "why": " ".join(why.group(1).split()) if why else "",
                "accent": accent.group(1).strip() if accent else "",
                "axes": axes_html,
            }
        )
    if not directions:
        raise ValueError(f"no directions parsed from {src_index}")
    return company, sub, disclaimer, directions


def swatch(accent):
    """Accent swatch, when the harness recorded one for that direction."""
    if not accent:
        return '<span class="sw sw-none" aria-hidden="true"></span>'
    return f'<span class="sw" style="background:{html.escape(accent)}" aria-hidden="true"></span>'


def render(slug, industry, company, sub, disclaimer, directions):
    ind_no = slug.split("-", 1)[0]
    first = directions[0]
    esc = html.escape

    rail = []
    for i, d in enumerate(directions):
        rail.append(
            f'''      <a class="dir{' is-active' if i == 0 else ''}" href="{esc(d['href'])}"
         data-src="{esc(d['href'])}" data-title="{esc(d['code'] + ' · ' + d['label'])}"
         aria-current="{'true' if i == 0 else 'false'}">
        <span class="dir-top">
          {swatch(d['accent'])}
          <span class="label">{esc(d['code'])}</span>
        </span>
        <span class="dir-name">{esc(d['label'])}</span>
        <span class="dir-why">{d['why']}</span>
        <span class="dir-axes">{d['axes']}</span>
      </a>'''
        )
    rail_html = "\n".join(rail)

    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="robots" content="noindex">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(company)} — six directions · Grand Street Works</title>
<meta name="description" content="Six reference homepage directions for {industry.lower()}. {esc(company)} is a fictional business; the structure is real.">
<link rel="icon" href="{FAVICON}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root {{
    --bg-color: #E5E5E6;
    --text-color: #050505;
    --border-color: #050505;
    --border-light: rgba(5, 5, 5, 0.15);
    --font-sans: 'Inter', -apple-system, sans-serif;
    --font-mono: 'JetBrains Mono', monospace;
    --nav-height: 60px;
    --toolbar-height: 59px;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background-color: var(--bg-color);
    color: var(--text-color);
    font-family: var(--font-sans);
    -webkit-font-smoothing: antialiased;
    line-height: 1.4;
    overflow-x: hidden;
    padding-top: var(--nav-height);
  }}
  a {{ color: inherit; text-decoration: none; }}
  a:focus-visible, button:focus-visible {{ outline: 2px solid var(--text-color); outline-offset: 3px; }}
  h1 {{ font-size: clamp(2rem, 4vw, 3.25rem); font-weight: 500; letter-spacing: -0.03em; line-height: 1.05; }}
  p {{ font-size: 1.125rem; color: rgba(5, 5, 5, 0.8); line-height: 1.5; }}
  .label {{
    font-family: var(--font-mono);
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }}

  header {{
    position: fixed; top: 0; left: 0; width: 100%; height: var(--nav-height);
    display: flex; justify-content: space-between; align-items: center;
    padding: 0 2rem; background-color: var(--bg-color);
    border-bottom: 1px solid var(--border-color); z-index: 100;
  }}
  .logo-mark {{ display: flex; align-items: center; gap: 1rem; }}
  .status-dot {{
    width: 8px; height: 8px; background-color: #C2D57D; border-radius: 50%;
    display: inline-block; box-shadow: 0 0 10px rgba(194, 213, 125, 0.5); flex: none;
  }}

  .section-header {{
    display: flex; align-items: center; gap: 1rem; padding: 1rem 2rem;
    border-bottom: 1px solid var(--border-color);
    background: var(--text-color); color: var(--bg-color);
  }}
  .section-header .label {{ color: var(--bg-color); }}
  .section-header .label.dim {{ color: rgba(229, 229, 230, 0.6); }}
  /* the rail is a left column on wide screens and a row on top below 1000px */
  .hint-narrow {{ display: none; }}

  .intro {{ padding: 3.5rem 2rem; border-bottom: 1px solid var(--border-color); }}
  .intro p {{ margin-top: 1.25rem; max-width: 68ch; }}

  /* ---------- Viewer ---------- */
  .viewer {{
    display: grid;
    grid-template-columns: 340px 1fr;
    align-items: start;
    border-bottom: 1px solid var(--border-color);
  }}
  .rail {{ border-right: 1px solid var(--border-color); }}
  .dir {{
    display: flex; flex-direction: column; gap: 0.5rem;
    padding: 1.25rem 1.5rem;
    border-bottom: 1px solid var(--border-color);
    transition: background-color 0.2s ease;
  }}
  .rail .dir:last-child {{ border-bottom: none; }}
  .dir:hover {{ background-color: #DEDEDF; }}
  .dir.is-active {{ background-color: var(--text-color); color: var(--bg-color); }}
  .dir.is-active .label {{ color: var(--bg-color); }}
  .dir.is-active .dir-why, .dir.is-active .dir-axes {{ color: rgba(229, 229, 230, 0.7); }}
  .dir.is-active .dir-axes b {{ color: var(--bg-color); }}
  .dir-top {{ display: flex; align-items: center; gap: 0.6rem; }}
  .sw {{
    width: 12px; height: 12px; flex: none;
    border: 1px solid rgba(0, 0, 0, 0.25);
  }}
  /* one industry's harness never recorded accents — drop the slot rather than
     showing six empty boxes */
  .sw-none {{ display: none; }}
  .dir.is-active .sw {{ border-color: rgba(255, 255, 255, 0.35); }}
  .dir-name {{ font-size: 1.0625rem; font-weight: 600; letter-spacing: -0.01em; line-height: 1.2; }}
  .dir-why {{ font-size: 0.9375rem; color: rgba(5, 5, 5, 0.7); line-height: 1.45; }}
  .dir-axes {{
    font-family: var(--font-mono); font-size: 0.6875rem;
    text-transform: uppercase; letter-spacing: 0.04em;
    color: rgba(5, 5, 5, 0.55); line-height: 1.6;
  }}
  .dir-axes b {{ color: var(--text-color); font-weight: 500; }}

  .stage {{ position: sticky; top: var(--nav-height); }}
  .toolbar {{
    display: flex; justify-content: space-between; align-items: center;
    gap: 1rem; flex-wrap: wrap;
    padding: 0.75rem 1.5rem;
    border-bottom: 1px solid var(--border-color);
    background: var(--bg-color);
  }}
  .toolbar-right {{ display: flex; align-items: center; gap: 0.75rem; }}
  .widths {{ display: flex; border: 1px solid var(--border-color); }}
  .wbtn {{
    font-family: var(--font-mono); font-size: 0.6875rem;
    text-transform: uppercase; letter-spacing: 0.05em;
    padding: 0.5rem 0.85rem; border: none; background: transparent;
    color: var(--text-color); cursor: pointer;
  }}
  .wbtn + .wbtn {{ border-left: 1px solid var(--border-color); }}
  .wbtn.is-on {{ background: var(--text-color); color: var(--bg-color); }}
  .open {{
    font-family: var(--font-mono); font-size: 0.6875rem;
    text-transform: uppercase; letter-spacing: 0.05em;
    padding: 0.5rem 0.85rem; border: 1px solid var(--border-color);
  }}
  .open:hover {{ background: var(--text-color); color: var(--bg-color); }}

  .frame-well {{
    background: var(--text-color);
    /* viewport, less the fixed header and the toolbar directly above */
    height: calc(100vh - var(--nav-height) - var(--toolbar-height));
    min-height: 520px;
    display: flex; justify-content: center;
    padding: 0;
  }}
  .frame-well[data-mode="phone"] {{ padding: 1.5rem 1rem; }}
  #preview {{
    width: 100%; height: 100%; border: 0; background: #fff;
    display: block;
  }}
  .frame-well[data-mode="phone"] #preview {{
    width: 390px; max-width: 100%;
    box-shadow: 0 0 0 1px rgba(229, 229, 230, 0.25);
  }}
  .noscript-note {{
    padding: 1rem 1.5rem; border-bottom: 1px solid var(--border-color);
    font-family: var(--font-mono); font-size: 0.75rem;
  }}

  footer {{
    display: flex; justify-content: space-between; gap: 1rem; flex-wrap: wrap;
    padding: 1.5rem 2rem; border-top: 1px solid var(--border-color);
  }}
  footer .label {{ color: rgba(5, 5, 5, 0.7); }}

  @media (max-width: 1000px) {{
    .hint-wide {{ display: none; }}
    .hint-narrow {{ display: inline; }}
    .viewer {{ grid-template-columns: 1fr; }}
    .rail {{
      border-right: none; border-bottom: 1px solid var(--border-color);
      display: flex; overflow-x: auto; -webkit-overflow-scrolling: touch;
    }}
    .dir {{
      min-width: 260px; border-bottom: none;
      border-right: 1px solid var(--border-color);
    }}
    .rail .dir:last-child {{ border-right: none; }}
    .stage {{ position: static; }}
    /* At this width the viewport is already the phone the demo was built for. */
    .widths {{ display: none; }}
    .frame-well, .frame-well[data-mode="phone"] {{
      padding: 0; height: 640px; min-height: 0;
    }}
    .frame-well[data-mode="phone"] #preview {{ width: 100%; box-shadow: none; }}
  }}
  @media (max-width: 640px) {{
    /* no room for the hint next to the section label at phone widths, and the
       stacked layout explains itself anyway */
    .hint-wide, .hint-narrow {{ display: none; }}
    header, .intro, .section-header, footer {{ padding-left: 1.25rem; padding-right: 1.25rem; }}
    .toolbar {{ padding-left: 1.25rem; padding-right: 1.25rem; }}
  }}
  @media (prefers-reduced-motion: reduce) {{
    .dir, .open, .wbtn {{ transition: none; }}
  }}
</style>
</head>
<body>

<header>
  <div class="logo-mark">
    <span class="status-dot" aria-hidden="true"></span>
    <a href="../../" class="label" style="font-weight: 600;">Grand Street Works</a>
  </div>
  <a href="../" class="label" style="text-decoration: underline;">← All work</a>
</header>

<main>
  <div class="section-header">
    <span class="label">[IND_{ind_no}] {industry}</span>
    <span class="label dim">Reference build</span>
  </div>

  <div class="intro">
    <h1>{esc(company)}</h1>
    <p>{sub}</p>
  </div>

  <div class="section-header">
    <span class="label">[VIEW] Six directions</span>
    <span class="label dim hint-wide">Pick one on the left — it loads on the right</span>
    <span class="label dim hint-narrow">Pick one above — it loads below</span>
  </div>

  <noscript>
    <div class="noscript-note">JavaScript is off, so the preview won't swap. Every direction below is a normal link — open them directly.</div>
  </noscript>

  <div class="viewer">
    <nav class="rail" aria-label="Directions">
{rail_html}
    </nav>
    <div class="stage">
      <div class="toolbar">
        <span class="label" id="now-showing">{esc(first['code'] + ' · ' + first['label'])}</span>
        <div class="toolbar-right">
          <div class="widths" role="group" aria-label="Preview width">
            <button type="button" class="wbtn is-on" data-mode="phone" aria-pressed="true">Phone</button>
            <button type="button" class="wbtn" data-mode="full" aria-pressed="false">Desktop</button>
          </div>
          <a class="open" id="open-full" href="{esc(first['href'])}" target="_blank" rel="noopener">Open full page ↗</a>
        </div>
      </div>
      <div class="frame-well" data-mode="phone">
        <iframe id="preview" src="{esc(first['href'])}" title="Preview of {esc(first['code'] + ' · ' + first['label'])}" loading="eager"></iframe>
      </div>
    </div>
  </div>
</main>

<footer>
  <div class="label">{disclaimer}</div>
  <div class="label"><a href="../" style="text-decoration: underline;">← All work</a></div>
</footer>

<script>
(function () {{
  var frame = document.getElementById('preview');
  var openFull = document.getElementById('open-full');
  var nowShowing = document.getElementById('now-showing');
  var well = document.querySelector('.frame-well');
  if (!frame || !well) return;

  document.querySelectorAll('.rail .dir').forEach(function (link) {{
    link.addEventListener('click', function (e) {{
      // Cmd/ctrl/middle click keeps its normal meaning: open in a new tab.
      if (e.metaKey || e.ctrlKey || e.shiftKey || e.button !== 0) return;
      e.preventDefault();
      var src = link.getAttribute('data-src');
      var title = link.getAttribute('data-title');
      frame.src = src;
      frame.title = 'Preview of ' + title;
      openFull.href = src;
      nowShowing.textContent = title;
      document.querySelectorAll('.rail .dir').forEach(function (other) {{
        var on = other === link;
        other.classList.toggle('is-active', on);
        other.setAttribute('aria-current', on ? 'true' : 'false');
      }});
    }});
  }});

  document.querySelectorAll('.wbtn').forEach(function (btn) {{
    btn.addEventListener('click', function () {{
      well.setAttribute('data-mode', btn.getAttribute('data-mode'));
      document.querySelectorAll('.wbtn').forEach(function (other) {{
        var on = other === btn;
        other.classList.toggle('is-on', on);
        other.setAttribute('aria-pressed', on ? 'true' : 'false');
      }});
    }});
  }});
}})();
</script>
</body>
</html>
'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, default=DEFAULT_SOURCE,
                    help="demos directory holding the harness index.html files")
    args = ap.parse_args()

    written = 0
    for slug, industry in INDUSTRIES.items():
        src = args.source / slug / "index.html"
        dest = WORK / slug / "index.html"
        if not src.exists():
            print(f"skip {slug}: no source at {src}", file=sys.stderr)
            continue
        if not dest.parent.exists():
            print(f"skip {slug}: no {dest.parent}", file=sys.stderr)
            continue
        company, sub, disclaimer, directions = parse(src)
        dest.write_text(render(slug, industry, company, sub, disclaimer, directions))
        written += 1
        print(f"{slug}: {company} — {len(directions)} directions")

    print(f"\nwrote {written} index pages")
    if written != len(INDUSTRIES):
        sys.exit(1)


if __name__ == "__main__":
    main()
