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
import importlib
import re
import sys
from pathlib import Path
from urllib.parse import quote

# Run as a script, so tools/ is sys.path[0] and this resolves.
import identity_specs

DEFAULT_SOURCE = Path.home() / "fractal" / "cash_rich" / "demos"
REPO = Path(__file__).resolve().parent.parent
WORK = REPO / "work"


def umami_id() -> str:
    """The analytics id, read from the home page so there is one source of truth.

    This template used to carry a literal UMAMI_ID_GRANDSTREETWORKS placeholder
    and the real id was substituted into the twenty pages by hand afterwards, so
    every regeneration silently switched analytics off on the highest-intent
    pages on the site. Reading it here means that cannot happen again.
    """
    m = re.search(r'cloud\.umami\.is/script\.js" data-website-id="([^"]+)"',
                  (REPO / "index.html").read_text())
    if not m or m.group(1).startswith("UMAMI_ID"):
        print("warning: no analytics id on the home page; pages will ship without one",
              file=sys.stderr)
        return ""
    return m.group(1)

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

# Industries whose directions are photographic builds from cash_rich/static2.
# Their metadata lives in the copy deck rather than in the demo harness.
PHOTO_SETS = {
    "01-personal-injury": ("photo_copy_pi", "Injury and accident firms"),
    "21-estate-law": ("photo_copy_estate", "Estate, trust and corporate counsel"),
}


def photo_directions(module):
    """Directions for a photographic set, read from its copy deck."""
    import importlib
    deck = importlib.import_module(module)
    out = []
    for i, spec in enumerate(deck.PAGES.values(), 1):
        out.append({
            "href": slugify(spec["firm"]) + ".html",
            "code": f"D{i}",
            "label": spec["name"],
            "why": spec["why"],
            "accent": spec.get("accent", ""),
            "axes": spec.get("axes", ""),
        })
    return out


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
                "href": href.group(1),   # rewritten below to the client's own name
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


# Two trade names read badly with "Clients" appended in the plural.
HEADER_LABELS = {
    "Med spas": "Med Spa",
    "Accounting &amp; CPAs": "Accounting &amp; CPA",
}

def slugify(name):
    """A business name as a URL segment: 'Fair Oaks Roofing' -> fair-oaks-roofing."""
    s = name.lower().replace("&", "and")
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def trade_dir(source_slug):
    """Published directory for a trade: '06-roofing' -> 'roofing'."""
    return re.sub(r"^\d+-", "", source_slug)

def titled(industry):
    """Trade name in title case, leaving CPAs and the like as they are."""
    if industry in HEADER_LABELS:
        return HEADER_LABELS[industry]
    return " ".join(w.capitalize() if w.islower() else w for w in industry.split())


def firm_of(page):
    """The business name a build is for, read from its own <title>.

    Every build titles itself "<Firm> · <line>", photographic and CSS-only
    alike, so this picks up distinct names the moment a set gets them. The
    nineteen harness sets still name one firm across all six of their builds.
    """
    try:
        t = re.search(r"<title>(.*?)</title>", page.read_text(), re.S)
    except OSError:
        return ""
    if not t:
        return ""
    return html.unescape(" ".join(t.group(1).split())).split(" · ")[0].strip()


def swatch(accent, trade_slug=None, build_slug=None):
    """The build's own mark where the identity pass has given it one.

    A row of six colour chips says the six builds differ; a row of six marks
    shows it, on the page a prospect actually lands on. Falls back to the
    harness accent chip for trades the identity pass has not reached yet.
    """
    spec = identity_specs.resolve(trade_slug, build_slug) if trade_slug else None
    if spec:
        mark = identity_specs.mark_svg(spec).replace(
            "<svg ", '<svg class="sw sw-mark" aria-hidden="true" ', 1)
        return re.sub(r' role="img" aria-label="[^"]*"', "", mark)
    if not accent:
        return '<span class="sw sw-none" aria-hidden="true"></span>'
    return f'<span class="sw" style="background:{html.escape(accent)}" aria-hidden="true"></span>'


def render(slug, industry, company, sub, disclaimer, directions):
    """One page per trade: the six builds stacked, each at container width."""
    esc = html.escape

    # Values used by the closing CTA band. trade_slug is the published
    # directory name, which is also the value /start/ expects for its trade
    # question — so arriving from a gallery skips that question entirely.
    trade_slug = trade_dir(slug)
    uid = umami_id()
    umami = (f'<script defer src="https://cloud.umami.is/script.js" '
             f'data-website-id="{uid}"></script>') if uid else ""
    # titled() is HTML-escaped; a mailto subject is URL-escaped, not HTML,
    # so unescape first or the recipient reads a literal "&amp;".
    mail_subject = quote(f"Rebuild our homepage: {html.unescape(titled(industry))}")

    blocks = []
    for i, d in enumerate(directions):
        title = f"C{i + 1} · {d['label']}"
        blocks.append(f'''      <section class="build">
        <div class="bar">
          <span class="bar-head">
            {swatch(d['accent'], trade_slug, Path(d['href']).stem)}
            <span class="label">C{i + 1}</span>
            <span class="bar-name">{esc(firm_of(WORK / trade_dir(slug) / d['href']) or d['label'])}</span>
          </span>
          <div class="bar-actions">
            <a class="open" href="{esc(d['href'])}" target="_blank" rel="noopener">View full site ↗</a>
          </div>
        </div>
        <div class="frame-well">
          <iframe src="{esc(d['href'])}" title="{esc(title)}"
                  loading="{'eager' if i == 0 else 'lazy'}"></iframe>
        </div>
      </section>''')
    builds = "\n".join(blocks)

    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="robots" content="noindex">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titled(industry)}: six builds · Grand Street Works</title>
<meta name="description" content="Six reference homepage builds for {industry.lower()}, each for a different business.">
<meta property="og:image" content="https://grandstreetworks.com/assets/social/gw-og-card.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{FAVICON}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<!-- Umami, same site ID as the rest of grandstreetworks.com. These pages are
     noindex, but which trades get browsed is the cheapest read we have on
     which verticals to point advertising at. -->
{umami}
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
    --frame-height: min(82vh, 940px);
    /* the stack sits on a neutral ground so each build reads as an object
       rather than as the page itself */
    --ground: #CFCFD1;
    --stage: #B7B7B9;
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
  .logo-mark {{ display: flex; align-items: center; gap: 1rem; min-width: 0; }}
  .portfolio-of {{ color: rgba(5, 5, 5, 0.45); white-space: nowrap; }}
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

  /* ---------- One build: the site, then its bar ---------- */
  /* Two up: the six builds sit in pairs so they can be compared side by
     side, the way a client actually looks at options. */
  .builds {{
    background: var(--ground);
    padding: 3rem 5%;
    border-bottom: 1px solid var(--border-color);
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 2rem;
  }}
  .build {{
    min-width: 0;
    border: 1px solid var(--border-color);
    background: var(--bg-color);
  }}
  .frame-well {{
    background: var(--stage);
    height: var(--frame-height);
    min-height: 520px;
    display: flex; justify-content: center;
    overflow: hidden;
  }}
  .build iframe {{
    width: 100%; height: 100%; border: 0; background: #fff; display: block;
  }}
  /* Desktop preview at half scale: a half-width column is ~630px, which
     would otherwise show the site's tablet layout. Rendering the frame at
     twice the column and scaling it down keeps a real desktop layout in
     each pane. */
  .frame-well {{ justify-content: flex-start; }}
  .frame-well iframe {{
    flex: none; width: 200%; height: 200%;
    transform: scale(0.5); transform-origin: 0 0;
  }}

  .bar {{
    display: flex; align-items: center; justify-content: space-between;
    gap: 2rem; padding: 0.85rem 1.5rem;
    border-bottom: 1px solid var(--border-color);
    background: var(--bg-color);
  }}
  .bar-head {{ display: flex; align-items: center; gap: 0.7rem; min-width: 0; }}
  .bar-name {{
    font-size: 1.0625rem; font-weight: 600; letter-spacing: -0.01em;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  }}
  .sw {{ width: 12px; height: 12px; flex: none; border: 1px solid rgba(0, 0, 0, 0.25); }}
  /* The mark carries its own ground, so it takes no chip border. */
  .sw-mark {{ width: 17px; height: 17px; border: 0; display: block; }}
  /* one trade's harness never recorded accents — drop the slot rather than
     showing six empty boxes */
  .sw-none {{ display: none; }}

  .bar-actions {{ display: flex; align-items: center; gap: 0.75rem; flex: none; }}
  .open {{
    font-family: var(--font-mono); font-size: 0.6875rem;
    text-transform: uppercase; letter-spacing: 0.05em;
    padding: 0.5rem 0.85rem; border: 1px solid var(--border-color);
    white-space: nowrap;
  }}
  .open:hover {{ background: var(--text-color); color: var(--bg-color); }}

  footer {{
    display: flex; justify-content: space-between; gap: 1rem; flex-wrap: wrap;
    padding: 1.5rem 2rem; border-top: 1px solid var(--border-color);
  }}
  footer .label {{ color: rgba(5, 5, 5, 0.7); }}

  /* Closing band. Six finished homepages is the most persuasive moment on
     the site and it used to end in a back link, so this is where the ask
     goes. Same URL capture as the home page hero, pre-seeding the trade
     so the diagnostic opens with question two already answered. */
  .work-cta {{
    border-top: 1px solid var(--border-color);
    background: var(--text-color); color: var(--bg-color);
    padding: clamp(2.5rem, 6vw, 4.5rem) 2rem;
  }}
  .work-cta .label {{ color: rgba(229, 229, 230, 0.62); }}
  .work-cta h2 {{
    font-size: clamp(1.75rem, 3.6vw, 3rem); font-weight: 500;
    letter-spacing: -0.03em; line-height: 1.1; max-width: 20ch;
    margin: 1.25rem 0 1rem;
  }}
  .work-cta p {{ max-width: 56ch; color: rgba(229, 229, 230, 0.78); font-size: 1.0625rem; }}
  .work-cta form {{ margin-top: 2rem; max-width: 640px; }}
  .work-cta .row {{ display: flex; flex-wrap: wrap; border: 1px solid var(--bg-color); }}
  .work-cta input {{
    flex: 1 1 240px; min-width: 0; font-family: var(--font-mono); font-size: 1rem;
    padding: 1.0625rem 1.125rem; border: none; background: transparent; color: var(--bg-color);
  }}
  .work-cta input::placeholder {{ color: rgba(229, 229, 230, 0.45); }}
  .work-cta input:focus {{ outline: none; background: rgba(229, 229, 230, 0.08); }}
  .work-cta button {{
    flex: 0 0 auto; font-family: var(--font-mono); font-size: 0.875rem;
    text-transform: uppercase; letter-spacing: 0.05em; padding: 1.0625rem 1.5rem;
    border: none; border-left: 1px solid var(--bg-color);
    background: var(--bg-color); color: var(--text-color); cursor: pointer;
  }}
  .work-cta button:hover {{ opacity: 0.85; }}
  .work-cta .alt {{
    font-family: var(--font-mono); font-size: 0.75rem; letter-spacing: 0.03em;
    margin-top: 0.875rem; color: rgba(229, 229, 230, 0.6);
  }}
  .work-cta .alt a {{ color: var(--bg-color); text-decoration: underline; }}
  @media (max-width: 560px) {{
    .work-cta button {{ flex: 1 1 100%; border-left: none; border-top: 1px solid var(--bg-color); }}
  }}

  @media (max-width: 860px) {{
    .bar {{ flex-direction: column; align-items: flex-start; gap: 0.85rem; }}
    .bar-actions {{ width: 100%; }}
    .frame-well {{ padding: 0; height: 640px; min-height: 0; }}
    .builds {{ padding: 1.5rem 1.25rem; gap: 1.25rem; }}
  }}
  @media (max-width: 640px) {{
    /* one column on a phone, and the frame is the phone: no scaling */
    .builds {{ grid-template-columns: minmax(0, 1fr); }}
    .frame-well iframe {{ width: 100%; height: 100%; transform: none; }}
    .portfolio-of {{ display: none; }}
    header, .section-header, footer {{
      padding-left: 1.25rem; padding-right: 1.25rem;
    }}
    .bar {{ padding-left: 1.25rem; padding-right: 1.25rem; }}
  }}
  @media (prefers-reduced-motion: reduce) {{ .open {{ transition: none; }} }}
</style>
</head>
<body>

<header>
  <div class="logo-mark">
    <span class="status-dot" aria-hidden="true"></span>
    <a href="../../" class="label" style="font-weight: 600;">Grand Street Works</a>
    <span class="label portfolio-of">[{titled(industry)} site portfolio]</span>
  </div>
  <a href="../" class="label" style="text-decoration: underline;">← All work</a>
</header>

<main>
  <div class="section-header">
    <span class="label">{titled(industry)} Clients</span>
    <span class="label dim">Six builds, six directions. Open any one in full.</span>
  </div>

  <div class="builds">
{builds}
  </div>

  <section class="work-cta">
    <span class="label">Next // Your turn</span>
    <h2>Yours next.</h2>
    <p>Send your website address and we'll build you a new homepage first. No call, no obligation, nothing to cancel.</p>
    <form action="../../start/" method="get">
      <input type="hidden" name="trade" value="{trade_slug}">
      <div class="row">
        <label for="cta-url" style="position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0,0,0,0);">Your website address</label>
        <input type="text" id="cta-url" name="url" placeholder="yourfirm.com"
               autocomplete="url" inputmode="url" spellcheck="false" required>
        <button type="submit" data-umami-event="start" data-umami-event-place="work-{trade_slug}">Rebuild it →</button>
      </div>
      <p class="alt">Or <a data-umami-event="mailto" data-umami-event-place="work-{trade_slug}" href="mailto:joe@grandstreetworks.com?subject={mail_subject}">email Joe directly</a>.</p>
    </form>
  </section>
</main>

<footer>
  <div class="label"><a href="../" style="text-decoration: underline;">← All work</a></div>
  <div class="label"><a data-umami-event="start" data-umami-event-place="work-footer" href="../../start/?trade={trade_slug}" style="text-decoration: underline;">Get yours rebuilt →</a></div>
</footer>

</body>
</html>
'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, default=DEFAULT_SOURCE,
                    help="demos directory holding the harness index.html files")
    ap.add_argument("--only", nargs="*", metavar="TRADE",
                    help="regenerate just these published trade directories")
    args = ap.parse_args()

    written = 0
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    for slug, industry in INDUSTRIES.items():
        if args.only and trade_dir(slug) not in args.only:
            continue
        src = args.source / slug / "index.html"
        dest = WORK / trade_dir(slug) / "index.html"
        if not src.exists() and slug not in PHOTO_SETS:
            print(f"skip {slug}: no source at {src}", file=sys.stderr)
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        if slug in PHOTO_SETS:
            module, blurb = PHOTO_SETS[slug]
            try:
                directions = photo_directions(module)
            except ModuleNotFoundError:
                print(f"skip {slug}: no copy deck {module}.py", file=sys.stderr)
                continue
            company, sub, disclaimer = blurb, "", ""
        else:
            company, sub, disclaimer = parse(src)[:3]
            directions = parse(src)[3]
            try:
                deck = importlib.import_module(f"demo_copy.{slug}")
            except ModuleNotFoundError:
                deck = None
            if deck:
                for d in directions:
                    spec = deck.PAGES.get(d["href"])
                    if spec:
                        d["href"] = slugify(spec["firm"]) + ".html"
        dest.write_text(render(slug, industry, company, sub, disclaimer, directions))
        written += 1
        print(f"{slug}: {company} — {len(directions)} directions")

    print(f"\nwrote {written} index pages")
    expected = len(args.only) if args.only else len(INDUSTRIES)
    if written != expected:
        sys.exit(1)


if __name__ == "__main__":
    main()
