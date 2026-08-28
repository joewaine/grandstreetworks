#!/usr/bin/env python3
"""Build the fencing client site: sites/northline-fence/.

A real client site rather than a reference build, so it does not live under
work/ (which is noindex and says "fictional" in every footer). It is fully
self-contained, with its own encoded images and identity under
sites/northline-fence/assets/, so the folder can be dropped onto its own
domain unchanged.

Everything the client will want changed lives in CONFIG: name, phone, email,
town, service area, L&I registration number. Change it there and rerun.

    python3 tools/build-fencing-site.py            # images, identity, page
    python3 tools/build-fencing-site.py --page     # just rewrite index.html

Images: run tools/gen-fencing-images.py first; the originals live in
~/fractal/clients/northline-fence/originals and only the encoded ladder is
written into the repo. Needs avifenc, sips, and headless Chrome for the
rasterised identity assets.
"""

import argparse
import html
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from string import Template

REPO = Path(__file__).resolve().parent.parent
SLUG = "northline-fence"
SITE_DIR = REPO / "sites" / SLUG
IMG = SITE_DIR / "assets" / "img"
IDENTITY = SITE_DIR / "assets" / "identity"
ORIGINALS = Path.home() / "fractal" / "clients" / SLUG / "originals"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# --- the client -----------------------------------------------------------
# Placeholders until the owner's real details arrive. The phone is in the
# 555-01xx range reserved for fiction so the tel: links can never dial a
# stranger; swap it and every link updates.
CONFIG = {
    "name": "Northline Fence",
    "legal": "Northline Fence Co.",
    "phone": "(360) 555-0142",
    "email": "quotes@northlinefence.com",
    "town": "Everett, WA",
    "area_short": "Snohomish & King counties",
    "area_long": "Snohomish and King counties",
    "towns": ["Everett", "Marysville", "Lake Stevens", "Snohomish", "Monroe",
              "Mill Creek", "Bothell", "Lynnwood", "Edmonds", "Arlington",
              "Mukilteo", "Woodinville"],
    "lni": "NORTHLFC000AA",
    "hours": "Monday to Saturday, 7am to 6pm",
    "since": "2016",
    # Public URL the site will live at; only used for og:image and JSON-LD.
    "url": "https://grandstreetworks.com/sites/northline-fence/",
    # Optional POST endpoint for the quote form. Empty means the form falls
    # back to composing an email with the fields filled in.
    "quote_endpoint": "",
}

TAGLINE = "Cedar fence and gate contractor"
HEADLINE = "Built for Washington weather."

# --- images ---------------------------------------------------------------
HERO_AVIF = (1280, 2560)
HERO_JPEG = 1280
TILE_AVIF = (640, 1280)
TILE_JPEG = 720
AVIF_Q, AVIF_SPEED = "50", "6"
JPEG_Q = "62"

# name -> kind. "wide" images are full-bleed backdrops, "tile" images sit in
# the gallery grid or beside copy.
IMAGES = {
    "hero": "wide", "farmhouse": "wide", "finished-street": "wide",
    "storm-before": "tile", "storm-after": "tile", "post-setting": "tile",
    "cedar-detail": "tile", "gate": "tile", "chain-link": "tile",
    "ranch": "tile", "ornamental": "tile", "horizontal": "tile",
}


def sips(src: Path, out: Path, width: int, fmt: str, quality: str | None = None) -> None:
    cmd = ["sips", "-Z", str(width), "-s", "format", fmt]
    if quality:
        cmd += ["-s", "formatOptions", quality]
    subprocess.run(cmd + [str(src), "--out", str(out)], check=True, capture_output=True)


def dimensions(path: Path) -> tuple[int, int]:
    out = subprocess.run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", str(path)],
                         check=True, capture_output=True, text=True).stdout
    w = int(re.search(r"pixelWidth: (\d+)", out).group(1))
    h = int(re.search(r"pixelHeight: (\d+)", out).group(1))
    return w, h


def encode_images(force: bool) -> None:
    for tool in ("avifenc", "sips"):
        if not shutil.which(tool):
            sys.exit(f"{tool} not found")
    IMG.mkdir(parents=True, exist_ok=True)
    for name, kind in IMAGES.items():
        src = ORIGINALS / f"{name}.jpg"
        if not src.exists():
            print(f"  {name}: original missing, skipped")
            continue
        widths, jpeg_w = (HERO_AVIF, HERO_JPEG) if kind == "wide" else (TILE_AVIF, TILE_JPEG)
        with tempfile.TemporaryDirectory() as tmp:
            for w in widths:
                out = IMG / f"{name}-{w}.avif"
                if out.exists() and not force:
                    continue
                staged = Path(tmp) / f"{name}-{w}.png"
                sips(src, staged, w, "png")
                subprocess.run(["avifenc", "-q", AVIF_Q, "-s", AVIF_SPEED, "-j", "8",
                                str(staged), str(out)], check=True, capture_output=True)
            jpg = IMG / f"{name}-{jpeg_w}.jpg"
            if force or not jpg.exists():
                sips(src, jpg, jpeg_w, "jpeg", JPEG_Q)
        print(f"  {name}: {', '.join(p.name for p in sorted(IMG.glob(name + '-*')))}")


def picture(name: str, alt: str, sizes: str, eager: bool = False) -> str:
    """A <picture> pointing at the ladder, with the real aspect ratio as the
    width/height hint so nothing reflows when the image arrives."""
    kind = IMAGES[name]
    widths, jpeg_w = (HERO_AVIF, HERO_JPEG) if kind == "wide" else (TILE_AVIF, TILE_JPEG)
    src = ORIGINALS / f"{name}.jpg"
    w, h = dimensions(src) if src.exists() else ((2560, 1440) if kind == "wide" else (1600, 1200))
    srcset = ", ".join(f"assets/img/{name}-{x}.avif {x}w" for x in widths)
    load = 'loading="eager" fetchpriority="high"' if eager else 'loading="lazy"'
    return (f'<picture><source type="image/avif" srcset="{srcset}" sizes="{sizes}">'
            f'<img src="assets/img/{name}-{jpeg_w}.jpg" width="{w}" height="{h}" '
            f'alt="{html.escape(alt)}" {load} decoding="async"></picture>')


# --- identity -------------------------------------------------------------
PALETTE = {"ink": "#1B221E", "surface": "#F5F1E9", "accent": "#B85C2B",
           "flare": "#E9A56E", "dark": "#1B221E"}

# Three pickets and two rails: the device the page's own fence-board band is
# drawn from. Authored at 64x64 so it survives a 16px favicon.
MARK_INNER = """\
<g fill="{picket}">
<path d="M9 22 L17 12 L25 22 V58 H9 Z"/>
<path d="M24 16 L32 6 L40 16 V58 H24 Z"/>
<path d="M39 22 L47 12 L55 22 V58 H39 Z"/>
</g>
<g fill="{rail}">
<rect x="4" y="28" width="56" height="5"/>
<rect x="4" y="44" width="56" height="5"/>
</g>"""


def mark_svg(picket: str, rail: str, size: int | None = None, label: str | None = None) -> str:
    attrs = f' width="{size}" height="{size}"' if size else ""
    a11y = (f' role="img" aria-label="{html.escape(label)}"' if label
            else ' aria-hidden="true" focusable="false"')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"{attrs}{a11y}>'
            + MARK_INNER.format(picket=picket, rail=rail) + "</svg>")


def favicon_svg() -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 80" role="img" '
            f'aria-label="{html.escape(CONFIG["name"])}">'
            f'<rect width="80" height="80" rx="12" fill="{PALETTE["dark"]}"/>'
            f'<g transform="translate(8 8)">'
            + MARK_INNER.format(picket=PALETTE["accent"], rail=PALETTE["surface"])
            + "</g></svg>")


def shot(page_html: str, out: Path, width: int, height: int) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        page = Path(tmp) / "card.html"
        page.write_text(page_html)
        subprocess.run(
            [CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
             "--force-device-scale-factor=1", "--virtual-time-budget=5000",
             f"--window-size={width},{height}", f"--screenshot={out}", str(page)],
            check=True, capture_output=True)


def og_card() -> str:
    c = CONFIG
    return f"""<!doctype html><meta charset="utf-8">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700&family=Barlow:wght@400;500&display=swap" rel="stylesheet">
<style>
  *{{margin:0;box-sizing:border-box}}
  body{{width:1200px;height:630px;background:{PALETTE['dark']};color:{PALETTE['surface']};
       font:400 26px/1.5 Barlow,system-ui,sans-serif;padding:64px 84px 70px;
       display:flex;flex-direction:column;justify-content:space-between;overflow:hidden;position:relative}}
  .top{{display:flex;align-items:center;gap:26px}}
  .name{{font-family:"Barlow Condensed",Impact,sans-serif;font-weight:700;font-size:60px;
        line-height:1;text-transform:uppercase;letter-spacing:.02em}}
  h1{{font-family:"Barlow Condensed",Impact,sans-serif;font-weight:700;font-size:96px;
     line-height:.96;max-width:20ch;text-transform:uppercase;letter-spacing:.005em}}
  .rule{{height:8px;background:{PALETTE['accent']};width:132px;margin:30px 0 26px}}
  .foot{{display:flex;justify-content:space-between;align-items:baseline;
        font-size:28px;color:{PALETTE['flare']};letter-spacing:.04em}}
  .foot .trade{{color:{PALETTE['surface']};opacity:.62;text-transform:uppercase;
               letter-spacing:.18em;font-size:19px;font-weight:500;white-space:nowrap}}
  .boards{{position:absolute;left:0;right:0;bottom:0;height:22px;
          background:repeating-linear-gradient(90deg,#3B3F3A 0 44px,#22282A 44px 48px)}}
</style>
<div class="top">{mark_svg(PALETTE['accent'], PALETTE['surface'], 84)}<div class="name">{html.escape(c['name'])}</div></div>
<div><div class="rule"></div><h1>{html.escape(HEADLINE)}</h1></div>
<div class="foot"><span>{html.escape(c['phone'])}</span><span class="trade">{html.escape(TAGLINE)} · {html.escape(c['area_short'])}</span></div>
<div class="boards"></div>
"""


def build_identity(force: bool) -> None:
    IDENTITY.mkdir(parents=True, exist_ok=True)
    (IDENTITY / "mark.svg").write_text(
        mark_svg(PALETTE["accent"], PALETTE["ink"], label=CONFIG["name"]))
    (IDENTITY / "icon.svg").write_text(favicon_svg())
    png180 = IDENTITY / "icon-180.png"
    if force or not png180.exists():
        shot("<style>*{margin:0}body{width:180px;height:180px}svg{width:180px;height:180px;display:block}</style>"
             + favicon_svg(), png180, 180, 180)
    og = IDENTITY / "og.png"
    if force or not og.exists():
        shot(og_card(), og, 1200, 630)
    print("  identity: mark.svg icon.svg icon-180.png og.png")


# --- the page -------------------------------------------------------------
def jsonld() -> str:
    c = CONFIG
    data = {
        "@context": "https://schema.org",
        "@type": "HomeAndConstructionBusiness",
        "name": c["name"],
        "description": f"{TAGLINE} serving {c['area_long']}.",
        "telephone": c["phone"],
        "email": c["email"],
        "url": c["url"],
        "image": c["url"] + "assets/identity/og.png",
        "logo": c["url"] + "assets/identity/mark.svg",
        "areaServed": [{"@type": "City", "name": t} for t in c["towns"]],
        "address": {"@type": "PostalAddress", "addressLocality": c["town"].split(",")[0].strip(),
                    "addressRegion": "WA", "addressCountry": "US"},
        "openingHours": "Mo-Sa 07:00-18:00",
        "priceRange": "$$",
    }
    return ('<script type="application/ld+json">'
            + json.dumps(data, separators=(",", ":")) + "</script>")


SERVICES = [
    ("Cedar privacy fence",
     "Six-foot western red cedar on 4x4 posts with three rails, a cap rail and a "
     "rot board as standard. Dog-ear picket, board-on-board, or horizontal."),
    ("Chain link",
     "Galvanized or black vinyl-coated, four to eight feet, privacy slats if you "
     "want them. The right call for dog runs, side yards and commercial lots."),
    ("Ranch &amp; farm fence",
     "Split rail, three-rail with woven wire, hog panel, and horse-safe no-climb. "
     "Acreage is priced by the run, with corner bracing done properly."),
    ("Ornamental aluminum &amp; vinyl",
     "Powder-coated aluminum for front yards and pools, vinyl for a fence that never "
     "needs staining. Both carry a manufacturer warranty on top of ours."),
    ("Gates &amp; operators",
     "Walk gates and driveway gates in matching cedar, steel-framed so they never "
     "sag. Automatic openers with keypads, installed and wired."),
    ("Repairs &amp; post replacement",
     "A leaning section, a rotted post, a panel down after a windstorm. We tell you "
     "straight whether it is a repair or a rebuild, and price both."),
]

BUILD = [
    ("Posts that don't rot",
     "Ground-contact rated 4x4 posts, 24 to 30 inches deep, on a gravel base so "
     "water drains instead of sitting in the bottom of the hole. Concrete crowned "
     "above grade to shed the rain."),
    ("A rot board, every time",
     "A pressure-treated board runs along the bottom and keeps the cedar off the "
     "soil. It is the first thing to go on any fence and the cheapest to replace, "
     "so it takes the hit instead of your pickets."),
    ("Fasteners that don't bleed",
     "Stainless or hot-dipped galvanized ring-shank nails, screws at the gates. "
     "Plain steel streaks cedar black inside a year."),
]

STEPS = [
    ("Walk the line",
     "We come out, walk the fence line with you, find the property pins and mark "
     "the run. Free, and usually within a couple of days."),
    ("A written quote",
     "A per-foot price with the material, height, post spacing and gate count "
     "written down, good for 30 days. Shared line? We quote your neighbor's half "
     "separately so you can split it."),
    ("Build day",
     "Utilities located through 811 first. Most residential fences are one to two "
     "days. We haul off the old fence and leave the yard raked."),
    ("The walkthrough",
     "We walk the whole run with you, check every gate swings and latches, and you "
     "have a direct number if anything ever moves."),
]

# Placeholders. Replace with the owner's real Google reviews before launch;
# see sites/northline-fence/README.md.
REVIEWS = [
    ("Fence down across the whole back after the January windstorm. They had posts "
     "in the ground Thursday and the run finished Saturday. Looks better than the "
     "original.", "M. Ellison", "Marysville"),
    ("Three quotes, and theirs was the only one that said what size posts and how "
     "deep. That is why we picked them.", "D. Nakamura", "Lake Stevens"),
    ("Talked our neighbor into splitting the shared line and handled both sides. "
     "Two invoices, one crew, zero drama.", "R. Alvarez", "Bothell"),
]

FAQ = [
    ("Do I need a permit?",
     "Most cities in $area_long do not require one for a fence up to six feet in "
     "the back yard and four feet in the front, but a few do, and corner lots have "
     "sight-line rules. We check your city before we quote and pull the permit if "
     "one is needed."),
    ("How long does a cedar fence last here?",
     "Twenty to twenty-five years for the boards with the build we use, and the "
     "posts outlast that. Staining every three to four years keeps the colour. Left "
     "alone it silvers, which is fine, just a look."),
    ("What about the property line?",
     "We locate your pins where they exist. If they cannot be found, a survey is "
     "the only honest answer, and we will say so rather than build on a guess."),
    ("Can you match my neighbor's fence?",
     "Usually, yes. Bring a photo to the walk-through, or point at it."),
    ("How soon can you start?",
     "A written quote within 48 hours of the walk-through, and most jobs start "
     "inside two to three weeks. Storm repairs get moved up the list."),
    ("How does payment work?",
     "Half at signing to order material, the balance at the walkthrough. Nothing "
     "for work you have not seen."),
]


def list_html(items, wrap, inner) -> str:
    return "\n".join(inner(*it) for it in items)


PAGE = Template(r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<script>/* Relative asset paths need the directory URL: send /sites/x to /sites/x/. */
if(!/\/$$|\.[a-z0-9]+$$/i.test(location.pathname))location.replace(location.pathname+'/'+location.search+location.hash)</script>
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>$name · $tagline in $area_short</title>
<meta name="description" content="$description">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Barlow:wght@400;500;600&family=Barlow+Condensed:wght@600;700&display=swap" rel="stylesheet">
<link rel="icon" href="assets/identity/icon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="assets/identity/icon-180.png">
<meta name="theme-color" content="$dark">
<meta property="og:type" content="website">
<meta property="og:site_name" content="$name">
<meta property="og:title" content="$name · $headline">
<meta property="og:description" content="$description">
<meta property="og:image" content="${url}assets/identity/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
$jsonld
<style>
/* THE FENCE LINE ONE. hero:backdrop nav:bar services:grid-numbered proof:build-spec
   ink #1B221E · surface #F5F1E9 · accent #B85C2B (cedar) · muted #5C6360 · on-dark #EFEAE0
   Barlow Condensed display / Barlow body
   Device: the board band, a run of vertical cedar boards with two rails, closing the
   hero and signing the footer. The phone is the hero's largest object; the quote form
   is the second CTA everywhere. Built from the Grand Street Works trade set. */
:root{--ink:#1B221E;--surface:#F5F1E9;--accent:#B85C2B;--muted:#5C6360;--dark:#1B221E;
--ondark:#EFEAE0;--dim:#B9BDB6;--flare:#E9A56E;--rule:rgba(27,34,30,.16);--hair:rgba(27,34,30,.09);
--board:#3B3F3A;--gap:#22282A;--alt:#ECE7DD;--wrap:1140px}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;scroll-behavior:smooth}
body{margin:0;background:var(--surface);color:var(--ink);overflow-x:hidden;padding-bottom:84px;
font:400 17px/1.6 Barlow,system-ui,-apple-system,sans-serif}
.wrap{max-width:var(--wrap);margin:0 auto;padding:0 20px}
h1,h2,h3,.num{font-family:"Barlow Condensed",Impact,sans-serif;font-weight:700;margin:0;
line-height:1.02;letter-spacing:.005em;text-transform:uppercase}
a{color:inherit}
p{margin:0}
.btn{display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:62px;
padding:8px 20px;text-decoration:none;text-align:center;border:2px solid transparent;line-height:1.1;
font-weight:600;font-size:15px;letter-spacing:.13em;text-transform:uppercase;cursor:pointer}
.btn b{font-family:"Barlow Condensed",Impact,sans-serif;font-size:27px;letter-spacing:.01em;
font-weight:700;margin-top:2px}
.btn-primary{background:var(--accent);color:#fff}
.btn-primary:hover{background:#A34F22}
.btn-ghost{background:transparent;color:var(--ondark);border-color:rgba(239,234,224,.4)}
.btn-ghost:hover{border-color:var(--flare);color:var(--flare)}
.topbar{background:var(--gap);color:#C6CABF;font-size:14px}
.topbar .wrap{padding:8px 20px;letter-spacing:.06em;text-transform:uppercase;font-weight:500;
display:flex;justify-content:space-between;gap:16px}
.topbar .wrap span+span{display:none}
.nav{position:sticky;top:0;z-index:30;background:var(--dark);border-bottom:2px solid var(--accent)}
.nav .wrap{display:flex;align-items:center;gap:10px;height:62px}
.brand{font-family:"Barlow Condensed",Impact,sans-serif;font-weight:700;font-size:24px;color:#fff;
text-decoration:none;text-transform:uppercase;letter-spacing:.03em;flex:none;line-height:1}
.lockup{display:inline-flex;align-items:center;gap:.42em}
.lockup svg{height:1.2em;width:auto;flex:none;display:block}
.navlinks{display:none;gap:22px;margin-left:auto;font-size:13px;letter-spacing:.16em;
text-transform:uppercase;font-weight:500;color:var(--dim)}
.navlinks a{text-decoration:none;padding:6px 0}
.navlinks a:hover{color:var(--flare)}
.navact{margin-left:auto;flex:none;min-height:42px;padding:0 14px;white-space:nowrap;
display:flex;align-items:center;background:var(--accent);color:#fff;text-decoration:none;
font-weight:700;letter-spacing:.05em;font-family:"Barlow Condensed",Impact,sans-serif;font-size:20px}
/* Hero: the photograph sits behind the composition under a scrim in the
   page's own ground colour, so the contrast the layout was set with holds. */
.hero{position:relative;isolation:isolate;overflow:hidden;background:var(--dark);color:var(--ondark);padding:30px 0 0}
.hero>*:not(.backdrop){position:relative;z-index:1}
.backdrop{position:absolute;inset:0;z-index:0}
.backdrop picture{display:block;width:100%;height:100%}
.backdrop img{width:100%;height:100%;object-fit:cover;object-position:center 70%}
.backdrop::after{content:"";position:absolute;inset:0;
background:linear-gradient(100deg,rgb(27 34 30/.92) 0%,rgb(27 34 30/.84) 40%,rgb(27 34 30/.5) 72%,rgb(27 34 30/.3) 100%)}
@media(max-width:60rem){.backdrop::after{background:rgb(27 34 30/.84)}}
@media(forced-colors:active),print{.backdrop{display:none}}
.eyebrow{font-size:13px;letter-spacing:.2em;text-transform:uppercase;font-weight:600;
color:var(--flare);margin:0 0 12px}
.hero h1{font-size:clamp(40px,9.4vw,84px);color:#fff;max-width:11ch}
.hero .sub{font-size:16px;color:var(--dim);max-width:52ch;margin:16px 0 22px;line-height:1.55}
.ctas{display:grid;gap:10px}
.badges{list-style:none;margin:24px 0 0;padding:0;display:grid;gap:0;border-top:1px solid rgba(239,234,224,.2)}
.badges li{font-size:15px;color:var(--ondark);padding:11px 0 11px 22px;position:relative;
border-bottom:1px solid rgba(239,234,224,.14);letter-spacing:.01em}
.badges li::before{content:"";position:absolute;left:0;top:19px;width:11px;height:3px;background:var(--flare)}
/* The board band: vertical boards, two rails. */
.boards{height:44px;background:repeating-linear-gradient(90deg,var(--board) 0 46px,var(--gap) 46px 50px);
position:relative;margin-top:30px}
.boards::before,.boards::after{content:"";position:absolute;left:0;right:0;height:5px;background:var(--gap);opacity:.9}
.boards::before{top:10px}.boards::after{bottom:10px}
.hero .boards{z-index:1}
.strip{background:var(--accent);color:#fff}
.strip .wrap{padding:16px 20px;display:flex;flex-wrap:wrap;align-items:baseline;gap:6px 18px}
.strip .big{font-family:"Barlow Condensed",Impact,sans-serif;font-size:30px;font-weight:700;
text-transform:uppercase;line-height:1}
.strip .small{font-size:15px;font-weight:500;letter-spacing:.01em;max-width:60ch}
.sec{padding:46px 0}
.sec.alt{background:var(--alt)}
.kicker{font-size:13px;letter-spacing:.2em;text-transform:uppercase;font-weight:600;
color:var(--accent);margin:0 0 10px}
.sec h2,.build h2,.close h2,.gal h2{font-size:clamp(30px,7.2vw,56px);margin-bottom:12px}
.lede{color:var(--muted);max-width:58ch;margin:0 0 26px;font-size:16px}
.gridnum{display:grid;gap:0;border-top:3px solid var(--ink)}
.gn{padding:20px 0;border-bottom:1px solid var(--rule);display:grid;
grid-template-columns:46px minmax(0,1fr);gap:12px;align-items:start}
.gn .num{font-size:34px;color:var(--accent);line-height:.85}
.gn h3{font-size:23px;margin-bottom:6px}
.gn p{color:var(--muted);font-size:16px}
/* How we build: dark, the post-setting photograph beside the three specs. */
.build{background:var(--dark);color:var(--ondark);padding:44px 0 48px}
.build h2{color:#fff;max-width:18ch}
.build .kicker{color:var(--flare)}
.build .lede{color:var(--dim)}
.buildgrid{display:grid;gap:26px}
.buildrow{display:grid;gap:16px}
.buildrow div{border-left:3px solid var(--flare);padding:2px 0 2px 14px}
.buildrow strong{font-family:"Barlow Condensed",Impact,sans-serif;text-transform:uppercase;
font-size:21px;font-weight:700;display:block;color:#fff;line-height:1.1;margin-bottom:5px}
.buildrow p{color:var(--dim);font-size:16px}
.buildpic{margin:0;overflow:hidden;background:var(--board)}
.buildpic picture,.buildpic img{display:block;width:100%;height:auto}
.buildpic img{aspect-ratio:4/3;object-fit:cover}
.buildpic figcaption{font-size:12px;letter-spacing:.14em;text-transform:uppercase;font-weight:600;
color:var(--dim);padding:10px 0 0}
/* Gallery. */
.gal{background:var(--surface);padding:46px 0}
.gal .note{color:var(--muted);margin:12px 0 28px;max-width:58ch;font-size:16px}
.galgrid{display:grid;grid-template-columns:1fr;gap:3px;margin-top:3px}
.gal figure{margin:0;position:relative;overflow:hidden;background:var(--rule)}
.gal picture{display:block}
.gal img{display:block;width:100%;height:auto;aspect-ratio:4/3;object-fit:cover;transition:transform .5s ease}
.gal figure:hover img{transform:scale(1.035)}
.gal figcaption{position:absolute;left:0;bottom:0;background:var(--dark);color:var(--surface);
font-size:12px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;padding:7px 12px}
/* Before/after: one range input does the clip, the rule and the grip. */
.gal .cmp{--pos:50%;margin:0;position:relative;background:none}
.cmpframe{position:relative;overflow:hidden;touch-action:pan-y;background:var(--rule)}
.cmp picture,.cmp img{display:block;width:100%;height:auto}
.cmp img{aspect-ratio:4/3;object-fit:cover}
.cmpbefore{position:absolute;inset:0;clip-path:inset(0 calc(100% - var(--pos)) 0 0)}
.cmpline{position:absolute;top:0;bottom:0;left:var(--pos);width:3px;margin-left:-1.5px;background:#fff;pointer-events:none}
.cmpgrip{position:absolute;top:50%;left:50%;width:44px;height:44px;margin:-22px 0 0 -22px;border-radius:50%;
background:var(--accent);color:#fff;display:grid;place-items:center;box-shadow:0 2px 10px rgba(0,0,0,.35)}
.cmpgrip::before{content:"‹ ›";font:700 17px/1 system-ui,sans-serif;letter-spacing:.05em}
.cmptag{position:absolute;bottom:12px;font-size:12px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;
background:var(--dark);color:var(--surface);padding:6px 10px;pointer-events:none}
.cmptag-b{left:12px}.cmptag-a{right:12px}
.cmprange{position:absolute;inset:0;width:100%;height:100%;margin:0;opacity:0;cursor:ew-resize;-webkit-appearance:none;appearance:none;background:transparent}
.cmprange::-webkit-slider-thumb{-webkit-appearance:none;width:44px;height:100%}
.cmprange::-moz-range-thumb{width:44px;height:100%;border:0}
.cmprange:focus-visible~.cmpline{outline:3px solid var(--flare)}
.gal .cmpcap{position:static;background:none;color:var(--muted);font:400 14px/1.5 Barlow,system-ui,sans-serif;letter-spacing:0;text-transform:none;padding:10px 0 0}
/* Process, reviews, FAQ. */
.steps{list-style:none;margin:24px 0 0;padding:0;counter-reset:s;display:grid;gap:0}
.steps li{counter-increment:s;padding:20px 0;border-top:1px solid var(--rule);display:grid;
grid-template-columns:44px minmax(0,1fr);gap:12px}
.steps li::before{content:"0" counter(s);font-family:"Barlow Condensed",Impact,sans-serif;
font-size:26px;font-weight:700;color:var(--accent);line-height:1}
.steps h3{font-size:21px;margin-bottom:5px}
.steps p{color:var(--muted);font-size:16px}
.reviews{display:grid;gap:18px;margin-top:8px}
.rev{background:var(--surface);border-top:3px solid var(--accent);padding:20px 20px 18px}
.rev blockquote{margin:0;font-size:17px;line-height:1.5}
.rev blockquote::before{content:"“";color:var(--accent);font-family:"Barlow Condensed",Impact,sans-serif;font-size:34px;line-height:0;margin-right:4px;vertical-align:-8px}
.rev footer{margin-top:12px;font-size:13px;letter-spacing:.14em;text-transform:uppercase;font-weight:600;color:var(--muted)}
.stars{color:var(--accent);letter-spacing:.1em;font-size:14px;margin-bottom:8px}
.faq{border-top:3px solid var(--ink);margin-top:8px}
.faq details{border-bottom:1px solid var(--rule)}
.faq summary{cursor:pointer;list-style:none;padding:16px 36px 16px 0;position:relative;
font-family:"Barlow Condensed",Impact,sans-serif;font-weight:700;font-size:22px;text-transform:uppercase;line-height:1.1}
.faq summary::-webkit-details-marker{display:none}
.faq summary::after{content:"+";position:absolute;right:2px;top:12px;color:var(--accent);font-size:28px;line-height:1}
.faq details[open] summary::after{content:"–"}
.faq p{color:var(--muted);padding:0 0 18px;max-width:62ch;font-size:16px}
.towns{list-style:none;margin:18px 0 0;padding:0;display:flex;flex-wrap:wrap;gap:8px}
.towns li{border:1px solid var(--rule);padding:7px 12px;font-size:14px;letter-spacing:.06em;text-transform:uppercase;font-weight:500}
/* Quote form. */
.quote{background:var(--alt);padding:46px 0}
.quotegrid{display:grid;gap:26px}
.form{display:grid;gap:12px}
.form label{display:grid;gap:5px;font-size:13px;letter-spacing:.12em;text-transform:uppercase;font-weight:600;color:var(--muted)}
.form input,.form select,.form textarea{font:inherit;font-size:16px;padding:12px 12px;border:1px solid var(--rule);
background:#fff;color:var(--ink);border-radius:0;width:100%}
.form input:focus,.form select:focus,.form textarea:focus{outline:2px solid var(--accent);outline-offset:0;border-color:var(--accent)}
.form textarea{min-height:110px;resize:vertical}
.form .row{display:grid;gap:12px}
.form .btn{margin-top:4px;min-height:58px}
.form .fine{font-size:13px;color:var(--muted)}
.form .status{font-size:15px;font-weight:600;color:var(--accent);min-height:1.2em}
.contactcard{border-top:3px solid var(--ink);padding-top:18px;display:grid;gap:10px;align-content:start;font-size:16px}
.contactcard strong{font-family:"Barlow Condensed",Impact,sans-serif;font-size:22px;text-transform:uppercase;display:block;margin-bottom:2px}
.contactcard a{text-decoration:none;color:var(--accent);font-weight:600}
/* Close and footer. */
.close{position:relative;isolation:isolate;overflow:hidden;background:var(--dark);color:#fff;padding:52px 0 56px}
.close>*:not(.backdrop){position:relative;z-index:1}
.close .backdrop::after{background:linear-gradient(100deg,rgb(27 34 30/.92) 0%,rgb(27 34 30/.8) 45%,rgb(27 34 30/.45) 100%)}
.close h2{max-width:14ch;color:#fff}
.close p{max-width:52ch;font-size:17px;margin:12px 0 22px;color:var(--dim)}
.close .btn-primary{background:#fff;color:var(--accent)}
.close .btn-primary:hover{background:var(--surface)}
.foot{background:var(--dark);color:var(--dim);padding:0 0 30px;font-size:15px}
.foot .wrap{padding-top:34px}
.foot .brand{display:inline-block;margin-bottom:12px;font-size:22px}
.foot p{margin:0 0 9px;max-width:62ch}
.foot a{color:var(--flare);text-decoration:none}
.foot .fine{font-size:13px;color:#8C918B;margin-top:16px}
.callbar{position:fixed;left:0;right:0;bottom:0;z-index:40;background:var(--dark);
border-top:2px solid var(--accent);display:grid;grid-template-columns:1fr auto;gap:6px;padding:6px}
.callbar a{display:flex;align-items:center;justify-content:center;min-height:60px;
text-decoration:none;text-align:center;font-weight:700;line-height:1.1;padding:0 12px}
.callbar .tel{background:var(--accent);color:#fff;font-family:"Barlow Condensed",Impact,sans-serif;
font-size:26px;letter-spacing:.02em;text-transform:uppercase}
.callbar .alt2{color:var(--ondark);border:1px solid rgba(239,234,224,.4);font-size:13px;
letter-spacing:.08em;text-transform:uppercase;max-width:132px}
@media(max-width:559px){.navact{display:none}}
@media(min-width:700px){.topbar .wrap span+span{display:inline}.ctas{grid-template-columns:auto auto;justify-content:start}
.badges{grid-template-columns:1fr 1fr;column-gap:26px}.gridnum{grid-template-columns:1fr 1fr;column-gap:44px}
.steps{grid-template-columns:1fr 1fr;column-gap:44px}.galgrid{grid-template-columns:1fr 1fr 1fr}
.reviews{grid-template-columns:1fr 1fr 1fr}.form .row{grid-template-columns:1fr 1fr}
.sec,.gal,.quote{padding:76px 0}.hero{padding:60px 0 0}.build{padding:70px 0 74px}
.hero .sub{font-size:19px}.btn{min-height:70px}.btn b{font-size:32px}}
@media(min-width:900px){.buildgrid{grid-template-columns:minmax(0,1.15fr) minmax(0,1fr);align-items:center;gap:44px}
.buildrow{gap:20px}.quotegrid{grid-template-columns:minmax(0,1.3fr) minmax(0,1fr);gap:56px}}
@media(min-width:1000px){body{padding-bottom:0}.callbar{display:none}.navlinks{display:flex}
.navact{margin-left:24px}.hero{padding:88px 0 0}.hero .boards{margin-top:64px}}
/* Motion: gated on .m, which only the script adds, so nothing hides without JS. */
.m [data-reveal]{opacity:0;transform:translateY(14px);transition:opacity .7s cubic-bezier(.2,.6,.2,1),transform .7s cubic-bezier(.2,.6,.2,1)}
.m [data-reveal].in{opacity:1;transform:none}
.m .gal figure[data-reveal]:nth-child(2){transition-delay:.08s}
.m .gal figure[data-reveal]:nth-child(3){transition-delay:.16s}
.m .gal figure[data-reveal]:nth-child(4){transition-delay:.24s}
.m .gal figure[data-reveal]:nth-child(5){transition-delay:.32s}
.m .gal figure[data-reveal]:nth-child(6){transition-delay:.4s}
@keyframes hero-in{from{opacity:0;transform:scale(1.025)}to{opacity:1;transform:none}}
.m .hero .backdrop img{animation:hero-in 1s ease-out both}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}
.m [data-reveal]{opacity:1;transform:none;transition:none}.m .hero .backdrop img{animation:none}
.gal img{transition:none}.gal figure:hover img{transform:none}}
</style>
</head>
<body>
<div class="topbar"><div class="wrap"><span>L&amp;I registered, bonded &amp; insured</span><span>Free written quotes · $area_short</span></div></div>
<header class="nav"><div class="wrap">
  <a class="brand" href="#top"><span class="lockup">$mark<span>$name</span></span></a>
  <nav class="navlinks"><a href="#services">Fences</a><a href="#build">How we build</a><a href="#work">Recent work</a><a href="#process">Process</a><a href="#faq">Questions</a><a href="#quote">Quote</a></nav>
  <a class="navact" href="tel:$tel">$phone</a>
</div></header>
<section class="hero" id="top">
  <div class="backdrop" aria-hidden="true">$hero_pic</div>
  <div class="wrap">
    <p class="eyebrow">$tagline · $area_short</p>
    <h1>$headline</h1>
    <p class="sub">Cedar privacy, chain link, ranch and ornamental fencing, and the gates to match. Posts set in gravel and concrete, cedar that will still be standing in twenty years, and a written per-foot quote before anyone picks up a shovel.</p>
    <div class="ctas">
      <a class="btn btn-primary" href="tel:$tel">Call or text <b>$phone</b></a>
      <a class="btn btn-ghost" href="#quote">Get a free quote</a>
    </div>
    <ul class="badges">
      <li>Written quote within 48 hours</li><li>Posts set in gravel and concrete</li>
      <li>Western red cedar, tight-knot or better</li><li>Shared lines quoted for both neighbors</li>
    </ul>
  </div>
  <div class="boards" aria-hidden="true"></div>
</section>
<section class="strip"><div class="wrap">
  <p class="big">Quoted by the foot, in writing.</p>
  <p class="small">Every quote lists the material, the post size and spacing, the gate count and the price per linear foot, so two quotes can actually be compared.</p>
</div></section>
<section class="sec" id="services"><div class="wrap">
  <p class="kicker">Fences &amp; gates</p>
  <h2>What we build</h2>
  <p class="lede">Most calls fall into one of these. If yours does not, call anyway. We will tell you straight whether it is a repair, a rebuild, or something another trade should do.</p>
  <div class="gridnum">
$services
  </div>
</div></section>
<section class="build" id="build"><div class="wrap">
  <p class="kicker">How we build</p>
  <h2>Why ours outlast the others on the street</h2>
  <p class="lede">Forty inches of rain a year and a windstorm most winters. A fence here fails at the post and the bottom board, so that is where the money goes.</p>
  <div class="buildgrid">
    <div class="buildrow">
$build
    </div>
    <figure class="buildpic">$post_pic<figcaption>Post set on gravel, checked plumb on two faces</figcaption></figure>
  </div>
</div></section>
<section class="gal" id="work"><div class="wrap">
  <p class="kicker">Recent work</p>
  <h2>After the windstorm</h2>
  <p class="note">The same back yard, one week apart. Two panels down and a snapped post on the Monday; the whole run rebuilt in cedar by the weekend. Drag to compare.</p>
  <figure class="cmp"><div class="cmpframe">
    $after_pic
    <div class="cmpbefore">$before_pic</div>
    <span class="cmpline" aria-hidden="true"><span class="cmpgrip"></span></span>
    <span class="cmptag cmptag-b">Before</span><span class="cmptag cmptag-a">After</span>
    <input class="cmprange" type="range" min="0" max="100" value="50" step="0.5" aria-label="Drag to compare the before and after photographs">
  </div><figcaption class="cmpcap">Six-foot cedar, cap rail and rot board, 4x4 posts at eight feet.</figcaption></figure>
  <div class="galgrid">
$tiles
  </div>
</div></section>
<section class="sec alt" id="process"><div class="wrap">
  <p class="kicker">Process</p>
  <h2>How a job actually runs</h2>
  <p class="lede">The part most fence companies leave vague, which is the part you are wondering about while the old fence is lying on the lawn.</p>
  <ol class="steps">
$steps
  </ol>
</div></section>
<section class="sec" id="reviews"><div class="wrap">
  <p class="kicker">Reviews</p>
  <h2>What the neighbors say</h2>
  <div class="reviews">
$reviews
  </div>
</div></section>
<section class="sec alt" id="faq"><div class="wrap">
  <p class="kicker">Fair questions</p>
  <h2>Before you call</h2>
  <div class="faq">
$faq
  </div>
</div></section>
<section class="sec" id="area"><div class="wrap">
  <p class="kicker">Service area</p>
  <h2>$area_long</h2>
  <p class="lede">Based in $town. If you are a little outside the towns below, call anyway. Acreage jobs travel further.</p>
  <ul class="towns">
$towns
  </ul>
</div></section>
<section class="quote" id="quote"><div class="wrap">
  <p class="kicker">Free quote</p>
  <h2>Tell us about the fence</h2>
  <p class="lede">Rough numbers are fine. We will call to set up the walk-through, and the written quote follows within 48 hours of it.</p>
  <div class="quotegrid">
    <form class="form" id="quoteform" action="mailto:$email" method="post" enctype="text/plain">
      <div class="row">
        <label>Name<input name="name" autocomplete="name" required></label>
        <label>Phone<input name="phone" type="tel" autocomplete="tel" required></label>
      </div>
      <div class="row">
        <label>Email<input name="email" type="email" autocomplete="email"></label>
        <label>Town<input name="town" autocomplete="address-level2" placeholder="$town_placeholder"></label>
      </div>
      <div class="row">
        <label>Fence type<select name="type">
          <option>Cedar privacy</option><option>Chain link</option><option>Ranch or farm</option>
          <option>Ornamental aluminum</option><option>Vinyl</option><option>Gate only</option>
          <option>Repair</option><option>Not sure yet</option>
        </select></label>
        <label>Approx. length (feet)<input name="length" inputmode="numeric" placeholder="e.g. 180"></label>
      </div>
      <label>Anything else<textarea name="notes" placeholder="Gates, height, a shared line with a neighbor, a fence that is already down..."></textarea></label>
      <button class="btn btn-primary" type="submit">Send the details</button>
      <p class="status" role="status" aria-live="polite"></p>
      <p class="fine">Or just call or text <a href="tel:$tel">$phone</a>. No pressure either way, and no salesman turns up at the door.</p>
    </form>
    <div class="contactcard">
      <div><strong>Call or text</strong><a href="tel:$tel">$phone</a></div>
      <div><strong>Email</strong><a href="mailto:$email">$email</a></div>
      <div><strong>Hours</strong>$hours</div>
      <div><strong>Based in</strong>$town</div>
      <div><strong>Registered contractor</strong>WA L&amp;I #$lni · Bonded &amp; insured</div>
    </div>
  </div>
</div></section>
<section class="close" id="contact">
  <div class="backdrop" aria-hidden="true">$close_pic</div>
  <div class="wrap">
    <h2>Ready to walk the line?</h2>
    <p>Call, text, or send the form. We come out, measure, and put a real number in writing. If the fence just needs a couple of posts, we will say so.</p>
    <div class="ctas">
      <a class="btn btn-primary" href="tel:$tel">Call or text <b>$phone</b></a>
      <a class="btn btn-ghost" href="#quote">Get a free quote</a>
    </div>
  </div>
</section>
<footer class="foot">
  <div class="boards" aria-hidden="true" style="margin:0"></div>
  <div class="wrap">
  <a class="brand" href="#top"><span class="lockup">$mark<span>$name</span></span></a>
  <p><a href="tel:$tel">$phone</a> · <a href="mailto:$email">$email</a></p>
  <p>$legal · $town · Serving $area_long since $since</p>
  <p>WA L&amp;I registered contractor #$lni · Bonded and insured · $hours</p>
  <p class="fine">Site by <a href="https://grandstreetworks.com">Grand Street Works</a>.</p>
</div></footer>
<div class="callbar"><a class="tel" href="tel:$tel">Call $phone</a><a class="alt2" href="#quote">Free quote</a></div>
<script>
(function () {
  /* Before/after: the range writes its value to a custom property the clip,
     the rule and the grip all read. */
  document.querySelectorAll('.cmp').forEach(function (frame) {
    var range = frame.querySelector('.cmprange');
    if (!range) return;
    var apply = function () { frame.style.setProperty('--pos', range.value + '%'); };
    range.addEventListener('input', apply);
    apply();
  });

  /* Quote form. With an endpoint configured it posts JSON; without one it
     hands the fields to the mail client, which is also what the form does
     on its own when this script never runs. */
  var ENDPOINT = $endpoint_json;
  var form = document.getElementById('quoteform');
  var status = form.querySelector('.status');
  form.addEventListener('submit', function (ev) {
    var data = {};
    new FormData(form).forEach(function (v, k) { data[k] = v; });
    if (!ENDPOINT) {
      ev.preventDefault();
      var body = Object.keys(data).map(function (k) { return k + ': ' + data[k]; }).join('\n');
      window.location.href = 'mailto:' + $email_json
        + '?subject=' + encodeURIComponent('Fence quote request from ' + (data.name || 'the website'))
        + '&body=' + encodeURIComponent(body);
      status.textContent = 'Opening your mail app. If nothing happens, call or text us instead.';
      return;
    }
    ev.preventDefault();
    status.textContent = 'Sending...';
    fetch(ENDPOINT, { method: 'POST', headers: { 'Content-Type': 'application/json' },
                      body: JSON.stringify(data) })
      .then(function (r) { if (!r.ok) throw new Error(r.status); form.reset();
                           status.textContent = 'Got it. We will call to set up the walk-through.'; })
      .catch(function () { status.textContent = 'That did not go through. Call or text us and we will sort it out.'; });
  });

  /* Once-only reveal on sections and gallery tiles. */
  if (!('IntersectionObserver' in window)) return;
  var targets = [].slice.call(document.querySelectorAll('body > section, .gal figure'));
  var first = document.querySelector('body > section');
  targets = targets.filter(function (el) { return el !== first; });
  document.documentElement.classList.add('m');
  targets.forEach(function (el) { el.setAttribute('data-reveal', ''); });
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
    });
  }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
  targets.forEach(function (el) { io.observe(el); });
})();
</script>
</body>
</html>
""")

TILES = [
    ("gate", "Cedar walk gate, steel frame, black hardware"),
    ("horizontal", "Horizontal cedar on steel posts"),
    ("chain-link", "Black vinyl-coated chain link"),
    ("ranch", "Three-rail with woven wire, on acreage"),
    ("ornamental", "Ornamental aluminum, front yard"),
    ("cedar-detail", "Tight-knot cedar, stainless ring-shank"),
]


def build_page() -> None:
    c = CONFIG
    tel = re.sub(r"\D", "", c["phone"])
    tel = ("+1" + tel) if len(tel) == 10 else "+" + tel
    description = (f"{TAGLINE} in {c['area_long']}. Cedar privacy, chain link, ranch, "
                   f"ornamental and gates. Posts set in gravel and concrete, written "
                   f"per-foot quotes within 48 hours. WA L&I registered, bonded and insured.")
    mark = mark_svg(PALETTE["accent"], PALETTE["surface"])

    services = "\n".join(
        f'    <article class="gn"><div class="num">{i:02d}</div><div><h3>{t}</h3><p>{p}</p></div></article>'
        for i, (t, p) in enumerate(SERVICES, 1))
    build = "\n".join(
        f'      <div><strong>{html.escape(t)}</strong><p>{html.escape(p)}</p></div>' for t, p in BUILD)
    steps = "\n".join(
        f'    <li><div><h3>{html.escape(t)}</h3><p>{html.escape(p)}</p></div></li>' for t, p in STEPS)
    reviews = "\n".join(
        f'    <article class="rev"><div class="stars" aria-label="Five stars">★★★★★</div>'
        f'<blockquote>{html.escape(q)}</blockquote><footer>{html.escape(n)} · {html.escape(w)}</footer></article>'
        for q, n, w in REVIEWS)
    faq = "\n".join(
        f'    <details><summary>{html.escape(q)}</summary><p>{html.escape(Template(a).substitute(area_long=c["area_long"]))}</p></details>'
        for q, a in FAQ)
    towns = "\n".join(f'    <li>{html.escape(t)}</li>' for t in c["towns"])
    tiles = "\n".join(
        f'    <figure>{picture(n, cap, "(max-width: 700px) 100vw, 33vw")}'
        f'<figcaption>{html.escape(cap)}</figcaption></figure>' for n, cap in TILES)

    page = PAGE.substitute(
        name=html.escape(c["name"]), legal=html.escape(c["legal"]),
        tagline=TAGLINE, headline=HEADLINE, description=html.escape(description),
        phone=html.escape(c["phone"]), tel=tel, email=html.escape(c["email"]),
        town=html.escape(c["town"]), town_placeholder=html.escape(c["town"].split(",")[0]),
        area_short=html.escape(c["area_short"]), area_long=html.escape(c["area_long"]),
        lni=html.escape(c["lni"]), hours=html.escape(c["hours"]), since=c["since"],
        url=c["url"], dark=PALETTE["dark"], jsonld=jsonld(), mark=mark,
        hero_pic=picture("hero", "", "100vw", eager=True),
        close_pic=picture("farmhouse", "", "100vw"),
        post_pic=picture("post-setting", "A fence post standing in a fresh hole with a level clamped to it", "(max-width: 900px) 100vw, 45vw"),
        before_pic=picture("storm-before", "Before: a grey fence blown down across a wet lawn", "(max-width: 700px) 100vw, 1140px"),
        after_pic=picture("storm-after", "After: a new cedar privacy fence in the same yard", "(max-width: 700px) 100vw, 1140px"),
        services=services, build=build, steps=steps, reviews=reviews, faq=faq,
        towns=towns, tiles=tiles,
        endpoint_json=json.dumps(c["quote_endpoint"]), email_json=json.dumps(c["email"]),
    )
    SITE_DIR.mkdir(parents=True, exist_ok=True)
    (SITE_DIR / "index.html").write_text(page)
    print(f"  page: {SITE_DIR / 'index.html'} ({len(page) // 1024}KB)")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--page", action="store_true", help="only rewrite index.html")
    ap.add_argument("--force", action="store_true", help="re-encode images and identity")
    a = ap.parse_args()
    if not a.page:
        encode_images(a.force)
        build_identity(a.force)
    build_page()


if __name__ == "__main__":
    main()
