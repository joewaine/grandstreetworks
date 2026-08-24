#!/usr/bin/env python3
"""Give every build a mark, a favicon, a social card and structured data.

Before this pass, all six builds in a trade set signed themselves the same way:
the company name set in the display face. No mark, no favicon (0/120 builds had
one), no og:image (0/120), no JSON-LD (0/120). Six businesses that shared a
signature read as one design recoloured six times, which is exactly the failure
the set exists to disprove.

Per build this writes, into work/_assets/identity/<trade>/:

    <slug>-mark.svg      the mark on its own, transparent
    <slug>-icon.svg      favicon — the mark on its card ground, padded
    <slug>-icon-180.png  apple-touch-icon
    <slug>-og.png        1200x630 social card

and patches the build itself: icon + Open Graph + Twitter tags in the head,
the mark inlined into the nav and footer lockups, and a LocalBusiness JSON-LD
block. Idempotent — a build already carrying the marker comment is skipped.

    python3 tools/build-identity-kits.py roofing
    python3 tools/build-identity-kits.py roofing --force

Rasterising needs headless Chrome, same as measure-hero-colors.py.
"""

import argparse
import html
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from identity_specs import BUILDS, mark_svg  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
WORK = REPO / "work"
IDENTITY = WORK / "_assets" / "identity"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
SITE = "https://grandstreetworks.com"
MARKER = "<!-- gsw:identity -->"


def shot(html_text: str, out: Path, width: int, height: int, scale: int = 1) -> None:
    """Rasterise a fragment of HTML at an exact size."""
    with tempfile.TemporaryDirectory() as tmp:
        page = Path(tmp) / "card.html"
        page.write_text(html_text)
        subprocess.run(
            [CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
             f"--force-device-scale-factor={scale}",
             # Webfonts arrive over the network; without a virtual time budget
             # the screenshot can fire on the fallback face.
             "--virtual-time-budget=5000",
             f"--window-size={width},{height}",
             f"--screenshot={out}", str(page)],
            check=True, capture_output=True)


def og_card(spec: dict, trade_label: str) -> str:
    name = html.escape(spec["name"])
    headline = html.escape(spec["headline"])
    fam = spec["display_font"]
    # Long headlines at the display size ran into the footer rule.
    h1_size = 82 if len(spec["headline"]) <= 42 else 64
    return f"""<!doctype html><meta charset="utf-8">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family={spec['display_css']}&family=Inter:wght@400;500&display=swap" rel="stylesheet">
<style>
  *{{margin:0;box-sizing:border-box}}
  body{{width:1200px;height:630px;background:{spec['card_bg']};color:{spec['card_fg']};
       font:400 26px/1.5 Inter,system-ui,sans-serif;padding:76px 84px;
       display:flex;flex-direction:column;justify-content:space-between;overflow:hidden}}
  .top{{display:flex;align-items:center;gap:26px}}
  .name{{font-family:"{fam}",Impact,sans-serif;font-weight:{spec['display_weight']};
        font-size:62px;line-height:1;{'text-transform:uppercase;' if spec['uppercase'] else ''}
        letter-spacing:.01em}}
  h1{{font-family:"{fam}",Impact,sans-serif;font-weight:{spec['display_weight']};
     font-size:{h1_size}px;line-height:1.04;max-width:19ch;
     {'text-transform:uppercase;' if spec['uppercase'] else ''}}}
  .rule{{height:8px;background:{spec['card_accent']};width:132px;margin:34px 0 30px}}
  .foot{{display:flex;justify-content:space-between;align-items:baseline;
        font-size:27px;color:{spec['card_accent']};letter-spacing:.04em}}
  .foot .trade{{color:{spec['card_fg']};opacity:.62;text-transform:uppercase;
               letter-spacing:.18em;font-size:22px;font-weight:500}}
</style>
<div class="top">{mark_svg(spec, 84, spec["card_bg"])}<div class="name">{name}</div></div>
<div><div class="rule"></div><h1>{headline}</h1></div>
<div class="foot"><span>{spec['phone']}</span><span class="trade">{trade_label}</span></div>
"""


def favicon_svg(spec: dict) -> str:
    """The mark on its own ground, with breathing room so it survives 16px."""
    inner = spec["mark"].format(
        **{**spec["palette"],
           **({"accent": spec["card_mark"]} if spec.get("card_mark") else {})})
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 80" '
        f'role="img" aria-label="{html.escape(spec["name"])}">'
        f'<rect width="80" height="80" rx="10" fill="{spec["card_bg"]}"/>'
        f'<g transform="translate(8 8)">{inner}</g></svg>')


def jsonld(spec: dict, trade: dict, slug: str) -> str:
    """Structured data. The address is deliberately locality-only: these are
    invented businesses and a fabricated street address on a page that is
    otherwise honest about being a demonstration is a step too far."""
    data = {
        "@context": "https://schema.org",
        "@type": trade["schema_type"],
        "name": spec["name"],
        "description": spec["tagline"],
        "telephone": spec["phone"],
        "areaServed": "Metro area",
        "image": f"{SITE}/work/_assets/identity/roofing/{slug}-og.png",
        "logo": f"{SITE}/work/_assets/identity/roofing/{slug}-mark.svg",
    }
    return ('<script type="application/ld+json">'
            + json.dumps(data, separators=(",", ":")) + "</script>")


HEAD_CSS = """
<style>
  /* Identity pass. The lockup is the mark plus the wordmark the build already
     had; the mark is sized in em so it tracks whatever display face this build
     sets its brand in. */
  .gsw-lockup { display: inline-flex; align-items: center; gap: .46em; }
  .gsw-lockup svg { height: 1.16em; width: auto; flex: none; display: block; }
</style>"""


def patch(page: Path, spec: dict, trade: dict, slug: str, trade_slug: str) -> str:
    src = page.read_text()
    if MARKER in src:
        return "already has identity"

    rel = f"../_assets/identity/{trade_slug}"
    name_esc = html.escape(spec["name"])
    # The builds carry a plain company name in .brand; wrap it in a lockup.
    mark_inline = mark_svg(spec, None).replace(
        '<svg ', '<svg aria-hidden="true" focusable="false" ', 1)
    mark_inline = re.sub(r' role="img" aria-label="[^"]*"', "", mark_inline)

    def brand_repl(m: re.Match) -> str:
        return (f'{m.group("open")}<span class="gsw-lockup">{mark_inline}'
                f'<span>{m.group("text")}</span></span></a>')

    src, n = re.subn(
        r'(?P<open><a class="brand"[^>]*>)(?P<text>[^<]+)</a>', brand_repl, src)
    if not n:
        return "no .brand lockup found"

    head = (
        f'{MARKER}\n'
        f'<link rel="icon" href="{rel}/{slug}-icon.svg" type="image/svg+xml">\n'
        f'<link rel="apple-touch-icon" href="{rel}/{slug}-icon-180.png">\n'
        f'<meta name="theme-color" content="{spec["card_bg"]}">\n'
        f'<meta property="og:type" content="website">\n'
        f'<meta property="og:site_name" content="{name_esc}">\n'
        f'<meta property="og:title" content="{name_esc} — {html.escape(spec["tagline"])}">\n'
        f'<meta property="og:description" content="{html.escape(spec["headline"])}">\n'
        f'<meta property="og:image" content="{SITE}/work/_assets/identity/{trade_slug}/{slug}-og.png">\n'
        f'<meta property="og:image:width" content="1200">\n'
        f'<meta property="og:image:height" content="630">\n'
        f'<meta name="twitter:card" content="summary_large_image">\n'
        f'{jsonld(spec, trade, slug)}\n'
        f'{HEAD_CSS}\n')
    src = src.replace("</head>", head + "</head>", 1)
    page.write_text(src)
    return f"identity added ({n} lockups)"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("trades", nargs="+")
    ap.add_argument("--force", action="store_true", help="re-render assets")
    args = ap.parse_args()

    for trade_slug in args.trades:
        trade = BUILDS.get(trade_slug)
        if not trade:
            print(f"  {trade_slug}: no specs, skipped")
            continue
        out_dir = IDENTITY / trade_slug
        out_dir.mkdir(parents=True, exist_ok=True)

        for slug, spec in trade["builds"].items():
            (out_dir / f"{slug}-mark.svg").write_text(mark_svg(spec))
            (out_dir / f"{slug}-icon.svg").write_text(favicon_svg(spec))

            png180 = out_dir / f"{slug}-icon-180.png"
            if args.force or not png180.exists():
                shot(f'<style>*{{margin:0}}body{{width:180px;height:180px}}'
                     f'svg{{width:180px;height:180px;display:block}}</style>'
                     + favicon_svg(spec), png180, 180, 180)

            og = out_dir / f"{slug}-og.png"
            if args.force or not og.exists():
                shot(og_card(spec, trade["trade_label"]), og, 1200, 630)

            page = WORK / trade_slug / f"{slug}.html"
            status = patch(page, spec, trade, slug, trade_slug) if page.exists() \
                else "page missing"
            print(f"  {slug:<34} {status}")


if __name__ == "__main__":
    main()
