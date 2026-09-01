#!/usr/bin/env python3
"""Build the Palm Construction site: sites/palm-construction/.

A real client site (Palm Construction WA, Inc., Federal Way) rather than a
reference build: no noindex, no "fictional" footer, self-contained under
sites/palm-construction/ so the folder can be dropped onto their own domain
unchanged. Brief: a higher-end design-build remodeler for the Puget Sound,
positioned to win larger jobs than the site it replaces, and it keeps the
drone reel their current site opens on.

Facts (name, phones, address, L&I number, service area, services, numbers,
reviews, FAQ, partners) come from palmconstructionwa.com and the WA L&I
open-data register. Anything the client will want changed lives in CONFIG
or the copy tables below. Change it there and rerun.

    python3 tools/build-palm-site.py            # images, identity, page
    python3 tools/build-palm-site.py --page     # just rewrite index.html

Images: frames from the client's own two drone reels, four of their own
photographs, and three Gemini atmosphere plates from tools/gen-palm-images.py.
The hero loop is cut from their reel by tools/encode-hero-video.py (see the
README). Originals live in ~/fractal/clients/palm-construction/originals and
only the encoded ladder is written into the repo. Needs avifenc, sips, and
headless Chrome for the rasterised identity assets.
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
SLUG = "palm-construction"
SITE_DIR = REPO / "sites" / SLUG
IMG = SITE_DIR / "assets" / "img"
IDENTITY = SITE_DIR / "assets" / "identity"
ORIGINALS = Path.home() / "fractal" / "clients" / SLUG / "originals"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# --- the client -----------------------------------------------------------
CONFIG = {
    "name": "Palm Construction",
    "legal": "Palm Construction WA, Inc.",
    "phone": "(206) 688-6711",
    "phone2": "(206) 445-5359",
    # Their site has no address on it; the contact form posts to WordPress.
    # Empty here means the consultation form falls back to SMS/phone rather
    # than to a mailbox nobody has confirmed. Fill in before launch.
    "email": "",
    "street": "33530 1st Way S, Ste 102",
    "town": "Federal Way, WA",
    "zip": "98003",
    "lat": 47.3018, "lng": -122.3350,
    "area_long": "the Seattle–Tacoma area",
    # Their homepage list, in their order.
    "towns": ["Auburn", "Des Moines", "Edgewood", "Federal Way", "Fife", "Kent",
              "Milton", "Pacific", "SeaTac", "Tacoma"],
    # WA L&I: PALM CONSTRUCTION WA INC, construction contractor, general,
    # active, effective 2023-10-10, expires 2027-10-10, UBI 605321309.
    "lni": "PALMCCW776PS",
    "ubi": "605321309",
    "facebook": "https://www.facebook.com/people/Palm-Construction-WA/61556824024394/",
    "instagram": "https://www.instagram.com/palmconstruction.wa/",
    "yelp": "https://www.yelp.com/biz/palm-construction-washington-federal-way",
    # Their reviews are Google reviews (Trustindex widget); no place link on
    # the site, so this is a search that resolves to the listing.
    "google": "https://www.google.com/search?q=Palm+Construction+WA+Federal+Way+reviews",
    # The pages on their current site the new one still points at.
    "careers": "https://palmconstructionwa.com/careers/",
    "blog": "https://palmconstructionwa.com/blog/",
    # Public URL the site will live at; only used for og:image and JSON-LD.
    "url": "https://grandstreetworks.com/sites/palm-construction/",
    # Optional POST endpoint for the consultation form. Empty means the form
    # falls back to email (if set) or to a text message.
    "quote_endpoint": "",
}

TAGLINE = "Design-build remodeling"
HEADLINE = "Built to the standard of the home."
# Their claims, from the About page. "3,000+ projects" is company-wide across
# WA, CA and TX; confirm they are happy to use it on the Washington site.
NUMBERS = [
    ("3,000+", "projects completed in 2025"),
    ("#1", "TrexPRO Platinum partner in Washington"),
    ("50+", "years of combined leadership experience"),
    ("< 1 wk", "from signed contract to first day on site, for most projects"),
]

# --- images ---------------------------------------------------------------
HERO_AVIF = (1280, 2560)
HERO_JPEG = 1280
TILE_AVIF = (640, 1280)
TILE_JPEG = 720
AVIF_Q, AVIF_SPEED = "50", "6"
JPEG_Q = "62"

# name -> kind. "wide" images are full-bleed backdrops, "tile" images sit in
# the gallery and the bands. Nothing is upscaled: each gets only the rungs of
# the ladder its original can fill, plus the original width when that is
# meaningfully wider than the last rung (a 1920px reel frame gets 1280 + 1920).
IMAGES = {
    "hero": "wide", "dusk": "wide", "kitchen": "wide",
    "plans": "tile", "sound-deck": "tile", "pavilion": "tile", "lake-wide": "tile",
    "covered-deck": "tile", "bath-vanity": "tile", "bath-tub": "tile",
    "white-stairs": "tile", "pergola-deck": "tile", "metal-roof": "tile",
    "exterior-paint": "tile", "driveway": "tile",
    "concrete-stairs": "tile", "deck-structure": "tile", "joists": "tile",
    "retaining-wall": "tile", "deck-frame": "tile",
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


def ladder(name: str) -> tuple[list[int], int]:
    """AVIF widths and the JPEG width this image actually gets."""
    kind = IMAGES[name]
    widths, jpeg_w = (HERO_AVIF, HERO_JPEG) if kind == "wide" else (TILE_AVIF, TILE_JPEG)
    src = ORIGINALS / f"{name}.jpg"
    if src.exists():
        w, _ = dimensions(src)
        kept = [x for x in widths if x <= w]
        if not kept or w >= kept[-1] * 1.25:
            kept.append(w)
        widths = kept
        jpeg_w = min(jpeg_w, w)
    return list(widths), jpeg_w


def encode_images(force: bool) -> None:
    for tool in ("avifenc", "sips"):
        if not shutil.which(tool):
            sys.exit(f"{tool} not found")
    IMG.mkdir(parents=True, exist_ok=True)
    for name in IMAGES:
        src = ORIGINALS / f"{name}.jpg"
        if not src.exists():
            print(f"  {name}: original missing, skipped")
            continue
        widths, jpeg_w = ladder(name)
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
    widths, jpeg_w = ladder(name)
    src = ORIGINALS / f"{name}.jpg"
    w, h = dimensions(src) if src.exists() else (1600, 1200)
    srcset = ", ".join(f"assets/img/{name}-{x}.avif {x}w" for x in widths)
    load = 'loading="eager" fetchpriority="high"' if eager else 'loading="lazy"'
    return (f'<picture><source type="image/avif" srcset="{srcset}" sizes="{sizes}">'
            f'<img src="assets/img/{name}-{jpeg_w}.jpg" width="{w}" height="{h}" '
            f'alt="{html.escape(alt)}" {load} decoding="async"></picture>')


def jpeg_path(name: str) -> str:
    _, jpeg_w = ladder(name)
    return f"assets/img/{name}-{jpeg_w}.jpg"


# --- identity -------------------------------------------------------------
# Their mark is a teal-and-gold palm-and-house lockup. The site's palette is
# quieter - charcoal, ivory, brass, with the teal kept as a deep secondary -
# and the mark is redrawn as a monoline roofline with a palm rising behind it,
# in one colour, so it survives a favicon and a social card.
PALETTE = {"ink": "#171A19", "surface": "#F4F1EA", "accent": "#A3843F",
           "flare": "#D3B978", "teal": "#1E4744", "dark": "#121514", "white": "#FFFFFF"}

MARK_INNER = """\
<g fill="none" stroke="{c}" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round">
<path d="M8 47 L30 25 L52 47"/>
<path d="M14 41 V58 H46 V41"/>
<path d="M26 58 V47 H34 V58"/>
<path d="M38 27 C39 19 42 13 47 9"/>
<path d="M47 9 C41 7 36 9 33 13"/>
<path d="M47 9 C44 4 39 3 35 4"/>
<path d="M47 9 C50 3 55 2 59 4"/>
<path d="M47 9 C53 8 58 11 60 16"/>
<path d="M47 9 C52 11 55 15 55 20"/>
</g>"""


def mark_svg(color: str, size: int | None = None, label: str | None = None) -> str:
    attrs = f' width="{size}" height="{size}"' if size else ""
    a11y = (f' role="img" aria-label="{html.escape(label)}"' if label
            else ' aria-hidden="true" focusable="false"')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"{attrs}{a11y}>'
            + MARK_INNER.format(c=color) + "</svg>")


def favicon_svg() -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" '
            f'aria-label="{html.escape(CONFIG["name"])}">'
            f'<rect width="64" height="64" rx="8" fill="{PALETTE["dark"]}"/>'
            + MARK_INNER.format(c=PALETTE["flare"]) + "</svg>")


def shot(page_html: str, out: Path, width: int, height: int) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        page = Path(tmp) / "card.html"
        page.write_text(page_html)
        subprocess.run(
            [CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
             "--force-device-scale-factor=1", "--virtual-time-budget=5000",
             f"--window-size={width},{height}", f"--screenshot={out}", str(page)],
            check=True, capture_output=True)


FONT_LINK = ('<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
             '<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500'
             '&family=Manrope:wght@400;500;600;700&display=swap" rel="stylesheet">')


def og_card() -> str:
    c = CONFIG
    return f"""<!doctype html><meta charset="utf-8">
{FONT_LINK}
<style>
  *{{margin:0;box-sizing:border-box}}
  body{{width:1200px;height:630px;background:{PALETTE['dark']};color:{PALETTE['surface']};
       font:400 24px/1.5 Manrope,system-ui,sans-serif;padding:64px 84px 64px;
       display:flex;flex-direction:column;justify-content:space-between;overflow:hidden;position:relative}}
  .top{{display:flex;align-items:center;gap:22px}}
  .name{{font-family:Manrope,sans-serif;font-weight:600;font-size:26px;letter-spacing:.22em;text-transform:uppercase}}
  h1{{font-family:"Cormorant Garamond",Georgia,serif;font-weight:500;font-size:104px;line-height:1;
     max-width:19ch;letter-spacing:-.01em}}
  h1 i{{font-style:italic;color:{PALETTE['flare']}}}
  .rule{{height:1px;background:{PALETTE['accent']};width:120px;margin:0 0 30px}}
  .foot{{display:flex;justify-content:space-between;align-items:baseline;font-size:24px;color:{PALETTE['flare']};letter-spacing:.02em}}
  .foot .trade{{color:{PALETTE['surface']};opacity:.6;text-transform:uppercase;letter-spacing:.22em;font-size:17px;font-weight:500;white-space:nowrap}}
</style>
<div class="top">{mark_svg(PALETTE['flare'], 76)}<div class="name">{html.escape(c['name'])}</div></div>
<div><div class="rule"></div><h1>Built to the standard <i>of the home.</i></h1></div>
<div class="foot"><span>{html.escape(c['phone'])}</span><span class="trade">{html.escape(TAGLINE)} · Puget Sound, WA</span></div>
"""


def build_identity(force: bool) -> None:
    IDENTITY.mkdir(parents=True, exist_ok=True)
    (IDENTITY / "mark.svg").write_text(mark_svg(PALETTE["accent"], label=CONFIG["name"]))
    (IDENTITY / "icon.svg").write_text(favicon_svg())
    png180 = IDENTITY / "icon-180.png"
    if force or not png180.exists():
        shot("<style>*{margin:0}body{width:180px;height:180px;background:#121514}"
             "svg{width:180px;height:180px;display:block}</style>" + favicon_svg(),
             png180, 180, 180)
    og = IDENTITY / "og.png"
    if force or not og.exists():
        shot(og_card(), og, 1200, 630)
    print("  identity: mark.svg icon.svg icon-180.png og.png")


# --- the page -------------------------------------------------------------
def jsonld() -> str:
    c = CONFIG
    data = {
        "@context": "https://schema.org",
        "@type": "GeneralContractor",
        "name": c["name"],
        "legalName": c["legal"],
        "description": f"Design-build remodeling in {c['area_long']}: outdoor living, kitchens "
                       f"and bathrooms, roofing, windows and doors, exteriors and whole-home renovations.",
        "telephone": c["phone"],
        "url": c["url"],
        "image": c["url"] + "assets/identity/og.png",
        "logo": c["url"] + "assets/identity/mark.svg",
        "sameAs": [c["facebook"], c["instagram"], c["yelp"]],
        "address": {"@type": "PostalAddress", "streetAddress": c["street"],
                    "addressLocality": c["town"].split(",")[0].strip(),
                    "addressRegion": "WA", "postalCode": c["zip"], "addressCountry": "US"},
        "geo": {"@type": "GeoCoordinates", "latitude": c["lat"], "longitude": c["lng"]},
        "areaServed": [{"@type": "City", "name": t} for t in c["towns"]],
        "priceRange": "$$$",
    }
    if c["email"]:
        data["email"] = c["email"]
    return ('<script type="application/ld+json">'
            + json.dumps(data, separators=(",", ":")) + "</script>")


# Copy below is drawn from the client's site - service pages, About, FAQ,
# careers page (for how a project is run) and reviews. Claims are theirs;
# the phrasing is the site's.
SERVICES = [
    ("Outdoor living",
     "Decks, covered patios, pergolas and pavilions, hardscape and turf. Washington's "
     "#1 TrexPRO Platinum partner, in composite, wood or pavers."),
    ("Kitchens",
     "Custom design, cabinetry, stone and appliances, built around the way you cook "
     "and gather. One team from drawings to the last cabinet pull."),
    ("Bathrooms",
     "Bespoke bathroom design: tile and slab, fixtures and glass, lighting, the "
     "details that make a primary bath feel like somewhere you would pay to stay."),
    ("Whole-home &amp; additions",
     "General construction for full-scale renovations and large projects, "
     "managed end to end with permits, inspections and every trade coordinated."),
    ("Roofing &amp; gutters",
     "Replacement and repair in composition and metal, with gutter systems and "
     "gutter guards, so the roof is one thing you never think about."),
    ("Windows, doors &amp; siding",
     "Energy-efficient double-pane low-e windows, custom entry doors in wood, "
     "fiberglass and iron, and siding that suits the house."),
    ("Exterior painting &amp; stucco",
     "Durable, weather-resistant finishes for a Pacific Northwest exterior, and "
     "stucco repair and application in traditional and modern textures."),
    ("Flooring &amp; interior finishes",
     "Hardwood, tile, laminate and vinyl, with interior painting and colour "
     "consultation, so the inside is finished to the same standard as the outside."),
]

STEPS = [
    ("Consultation &amp; design",
     "We walk the property, listen to how you live and what you want the house to "
     "do, then design it: drawings, material selections and a written scope and "
     "price. Nothing is vague."),
    ("Permits &amp; preparation",
     "We acquire the permits, prepare the paperwork, expedite the approvals and "
     "schedule the inspections. You do not deal with the building department; we do."),
    ("The build",
     "One project manager is your single point of contact from the first day, "
     "coordinating vetted crews and every trade, with daily communication. Most "
     "projects start within a week of signing."),
    ("Inspection &amp; handover",
     "Final inspection, a walkthrough with you, and then we stay in touch. Most of "
     "our work comes by word of mouth, and it stays that way by finishing properly."),
]

ABOUT = [
    ("Family-owned, veteran-operated",
     "A local company with the backing and buying power of a nationwide network: "
     "trusted partnerships with Trex, The Home Depot and Upgrade for materials and "
     "financing."),
    ("Speed without shortcuts",
     "Most projects start within a week, and dedicated, vetted crews stand behind "
     "their work and their timelines."),
    ("Leadership on every job",
     "Fifty-plus years of combined industry experience at the top, with quality "
     "control in the field and from headquarters."),
]

# Verbatim from the client's site (Google reviews via Trustindex).
REVIEWS = [
    ("They were very meticulous in all the finishes and final details, as if it were "
     "for their own home. In addition to being careful with the agreed deadlines, "
     "they met them without any delay, coordinating the different trades in a way "
     "that the time was optimized to the maximum.",
     "Aaron Alvarez"),
    ("Our house had some particularities, given the design we had made, which is why "
     "the issue of delivery and project specifications were more complex and "
     "detailed than for a common client. And we believe that Palm Construction was "
     "perfectly up to the task.",
     "Yeinyreth Mitchell Ramos"),
    ("The after-sales service has been very good, and even though we haven't had any "
     "problems, they have been constantly concerned about contacting us and knowing "
     "if everything is working well.",
     "Alfonso Peña"),
]

# From the client's FAQ, About and process copy, chosen for the questions a
# larger project raises.
FAQ = [
    ("Do you handle permits and inspections?",
     "Yes. Permit acquisition and preparation, expediting, inspection scheduling and "
     "the final inspection are part of every project. You will not be the one on "
     "the phone with the building department."),
    ("How soon can a project start?",
     "Most projects start within a week of a signed contract. Larger projects with "
     "design and permitting have a schedule set at the consultation."),
    ("Who manages the project day to day?",
     "A dedicated project manager is your single point of contact between you, the "
     "crews, the subcontractors and the office, communicating daily and on site."),
    ("Can you design the project as well as build it?",
     "Yes. Design is where a project starts with us: custom kitchen and bathroom "
     "design, deck and patio design to suit the house, landscape design, and colour "
     "consultation for interior and exterior finishes."),
    ("What materials do you build decks and patios with?",
     "Composite, wood and pavers, depending on the project. We are Washington's #1 "
     "TrexPRO Platinum partner, so for composite the whole range is available."),
    ("Do you offer financing?",
     "Yes. We partner with financing firms that cover up to 100% of a project, with "
     "options tailored to different budgets."),
    ("Do you warranty your work?",
     "Yes. Installations are warranted, and we follow up after completion to make "
     "sure everything is performing as it should."),
    ("Can you work within a budget?",
     "Yes. We build the scope around the budget at the design stage rather than "
     "discovering it halfway through. Tell us the number and we will tell you what "
     "it buys."),
    ("How long does a kitchen or bathroom remodel take?",
     "It depends on the scope, and we give you a schedule before we start. We plan "
     "the work to keep disruption to the rest of the house to a minimum."),
    ("Do you take on large-scale and commercial projects?",
     "Yes. From a single room to full-scale renovations, residential and commercial, "
     "with the management to match."),
]

# (name, caption, kind). Captions describe only what the picture shows.
TILES = [
    ("sound-deck", "Composite deck above Puget Sound", "feature"),
    ("pavilion", "Lakefront pavilion and putting green", ""),
    ("covered-deck", "Timber-framed covered deck", ""),
    ("bath-vanity", "Primary bath in marble-look slab", ""),
    ("white-stairs", "Deck, stair and pergola", ""),
    ("lake-wide", "Lakefront outdoor living, from above", ""),
    ("metal-roof", "Standing-seam metal roof", ""),
    ("exterior-paint", "Exterior repaint", ""),
    ("pergola-deck", "Covered entry deck", ""),
]
# Eight regular tiles plus the double feature fill four rows of three exactly;
# "bath-tub" and "driveway" are encoded and ready if the client wants a swap.

CRAFT = [
    ("concrete-stairs", "Poured concrete stair"),
    ("retaining-wall", "New retaining wall"),
    ("deck-frame", "The new frame going up"),
]


PAGE = Template(r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<script>/* Relative asset paths need the directory URL: send /sites/x to /sites/x/. */
if(!/\/$$|\.[a-z0-9]+$$/i.test(location.pathname))location.replace(location.pathname+'/'+location.search+location.hash)</script>
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>$name · Design-build remodeling, Puget Sound WA</title>
<meta name="description" content="$description">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&family=Manrope:wght@400;500;600;700&display=swap" rel="stylesheet">
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
/* THE ESTATE ONE, for Palm Construction. hero:video nav:bar
   work:editorial-grid services:numbered-grid proof:numbers + reviews
   ink #171A19 · surface #F4F1EA · accent #A3843F (brass) · teal #1E4744 · muted #5F625E
   Cormorant Garamond display / Manrope body
   Device: the hairline. One-pixel brass rules mark every section, the numbers
   are set in the serif, and nothing shouts: the video does the talking.
   Built from the Grand Street Works trade set. */
:root{--ink:#171A19;--surface:#F4F1EA;--paper:#FFFFFF;--alt:#EAE5DA;--accent:#A3843F;--accent-2:#8A6E33;
--teal:#1E4744;--muted:#5F625E;--dark:#121514;--ondark:#EDE8DD;--dim:#A9ADA7;--flare:#D3B978;
--rule:rgba(23,26,25,.14);--hair:rgba(23,26,25,.08);--wrap:1180px;
--serif:"Cormorant Garamond",Georgia,"Times New Roman",serif;--sans:Manrope,system-ui,-apple-system,sans-serif}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;scroll-behavior:smooth}
body{margin:0;background:var(--surface);color:var(--ink);overflow-x:hidden;padding-bottom:84px;
font:400 17px/1.65 var(--sans)}
.wrap{max-width:var(--wrap);margin:0 auto;padding:0 22px}
h1,h2,h3{font-family:var(--serif);font-weight:500;margin:0;line-height:1.04;letter-spacing:-.005em}
h1 i,h2 i{font-style:italic;font-weight:500}
a{color:inherit}
p{margin:0}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:10px;min-height:56px;padding:10px 28px;
text-decoration:none;text-align:center;border:1px solid transparent;line-height:1.1;font-weight:600;font-size:13px;
letter-spacing:.2em;text-transform:uppercase;cursor:pointer;font-family:var(--sans);transition:background .2s,color .2s,border-color .2s}
.btn-primary{background:var(--accent);color:#fff}
.btn-primary:hover{background:var(--accent-2)}
.btn-ghost{background:transparent;color:var(--ondark);border-color:rgba(237,232,221,.42)}
.btn-ghost:hover{border-color:var(--flare);color:var(--flare)}
.btn-ink{background:var(--ink);color:var(--surface)}
.btn-ink:hover{background:var(--teal)}
.topbar{background:var(--dark);color:#9DA29B;font-size:12px;border-bottom:1px solid rgba(237,232,221,.08)}
.topbar .wrap{padding:9px 22px;letter-spacing:.14em;text-transform:uppercase;font-weight:500;
display:flex;justify-content:space-between;gap:16px}
.topbar a{text-decoration:none}
.topbar a:hover{color:var(--flare)}
.topbar .wrap span+span{display:none}
.nav{position:sticky;top:0;z-index:30;background:rgba(18,21,20,.92);backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);
border-bottom:1px solid var(--accent)}
.nav .wrap{display:flex;align-items:center;gap:12px;height:68px}
.brand{font-family:var(--sans);font-weight:600;font-size:14px;color:#fff;text-decoration:none;
text-transform:uppercase;letter-spacing:.24em;flex:none;line-height:1}
.lockup{display:inline-flex;align-items:center;gap:.7em}
.lockup svg{height:2.1em;width:auto;flex:none;display:block}
.navlinks{display:none;gap:26px;margin-left:auto;font-size:12px;letter-spacing:.18em;
text-transform:uppercase;font-weight:500;color:var(--dim)}
.navlinks a{text-decoration:none;padding:6px 0;border-bottom:1px solid transparent}
.navlinks a:hover{color:#fff;border-color:var(--flare)}
.navact{margin-left:auto;flex:none;min-height:42px;padding:0 18px;white-space:nowrap;display:flex;align-items:center;
border:1px solid var(--accent);color:var(--flare);text-decoration:none;font-weight:600;letter-spacing:.16em;
text-transform:uppercase;font-size:12px}
.navact:hover{background:var(--accent);color:#fff}
.navtel{display:none;color:#fff;text-decoration:none;font-weight:600;letter-spacing:.04em;font-size:15px;margin-left:22px;white-space:nowrap}
/* Hero: the client's own drone reel, looping under a scrim in the page's ground
   colour. The still frame is the poster and carries first paint; the loop fades
   in over it once it is playing. */
.hero{position:relative;isolation:isolate;overflow:hidden;background:var(--dark);color:var(--ondark);
min-height:clamp(560px,calc(100svh - 68px),840px);display:flex;flex-direction:column;justify-content:flex-end}
.hero>*:not(.backdrop){position:relative;z-index:1}
.backdrop{position:absolute;inset:0;z-index:0}
.backdrop picture{display:block;width:100%;height:100%}
.backdrop img,.backdrop video{width:100%;height:100%;object-fit:cover;object-position:center 55%}
.backdrop video{position:absolute;inset:0;opacity:0;transition:opacity 1.4s ease}
.backdrop video.playing{opacity:1}
.backdrop::after{content:"";position:absolute;inset:0;
background:linear-gradient(180deg,rgb(18 21 20/.35) 0%,rgb(18 21 20/.2) 35%,rgb(18 21 20/.78) 78%,rgb(18 21 20/.94) 100%)}
@media(max-width:60rem){.hero .backdrop::after{background:linear-gradient(180deg,rgb(18 21 20/.5) 0%,rgb(18 21 20/.55) 30%,rgb(18 21 20/.86) 70%,rgb(18 21 20/.95) 100%)}}
@media(forced-colors:active),print{.backdrop{display:none}}
.hero .wrap{padding-top:64px;padding-bottom:36px;width:100%}
.eyebrow{font-size:12px;letter-spacing:.26em;text-transform:uppercase;font-weight:600;color:var(--flare);margin:0 0 18px}
.eyebrow::before{content:"";display:inline-block;width:28px;height:1px;background:var(--flare);vertical-align:middle;margin-right:12px}
.hero h1{font-size:clamp(44px,8.6vw,104px);color:#fff;max-width:13ch;line-height:.98}
.hero h1 i{color:var(--flare)}
.hero .sub{font-size:17px;color:var(--ondark);max-width:56ch;margin:22px 0 28px;line-height:1.6;opacity:.92}
.ctas{display:flex;flex-wrap:wrap;gap:10px}
.numbers{list-style:none;margin:40px 0 0;padding:26px 0 0;display:grid;gap:18px 20px;grid-template-columns:1fr 1fr;border-top:1px solid rgba(237,232,221,.22)}
.numbers b{display:block;font-family:var(--serif);font-weight:500;font-size:40px;line-height:1;color:#fff;letter-spacing:-.01em}
.numbers span{display:block;font-size:13px;color:var(--dim);margin-top:6px;letter-spacing:.02em;max-width:22ch}
/* Partners strip. */
.strip{background:var(--teal);color:var(--ondark)}
.strip .wrap{padding:18px 22px;display:flex;flex-wrap:wrap;align-items:center;gap:10px 28px;font-size:12px;
letter-spacing:.2em;text-transform:uppercase;font-weight:600}
.strip .lead{color:var(--flare)}
.strip span+span::before{content:"·";margin-right:28px;color:var(--flare);opacity:.7}
/* Sections. */
.sec{padding:64px 0}
.sec.alt{background:var(--alt)}
.sec.paper{background:var(--paper)}
.head{display:grid;gap:14px;margin-bottom:34px}
.kicker{font-size:12px;letter-spacing:.26em;text-transform:uppercase;font-weight:600;color:var(--accent);margin:0}
.kicker::before{content:"";display:inline-block;width:28px;height:1px;background:var(--accent);vertical-align:middle;margin-right:12px}
.sec h2,.about h2,.close h2,.gal h2,.fin h2{font-size:clamp(36px,6.4vw,66px);max-width:16ch}
.lede{color:var(--muted);max-width:58ch;font-size:17px;line-height:1.65}
/* Work: editorial grid, the first tile double. */
.gal{padding:64px 0;background:var(--surface)}
.galgrid{display:grid;grid-template-columns:1fr 1fr;gap:6px}
.gal figure{margin:0;position:relative;overflow:hidden;background:var(--alt)}
.gal figure.feature{grid-column:1/-1}
.gal picture{display:block}
.gal img{display:block;width:100%;height:100%;aspect-ratio:4/3;object-fit:cover;transition:transform .8s cubic-bezier(.2,.6,.2,1)}
.gal figure:hover img{transform:scale(1.03)}
.gal figcaption{position:absolute;left:0;right:0;bottom:0;padding:34px 14px 12px;color:#fff;font-size:12px;font-weight:600;
letter-spacing:.16em;text-transform:uppercase;background:linear-gradient(180deg,transparent,rgb(18 21 20/.72))}
.gal .more{margin-top:22px;font-size:15px;color:var(--muted)}
.gal .more a{color:var(--ink);font-weight:600;text-decoration:none;border-bottom:1px solid var(--accent)}
/* Services. */
.svc{display:grid;gap:0;border-top:1px solid var(--ink)}
.sv{padding:24px 0;border-bottom:1px solid var(--rule);display:grid;grid-template-columns:52px minmax(0,1fr);gap:12px;align-items:start}
.sv .num{font-family:var(--serif);font-size:30px;color:var(--accent);line-height:.9;font-weight:500;padding-top:3px}
.sv h3{font-size:27px;margin-bottom:8px}
.sv p{color:var(--muted);font-size:15.5px;line-height:1.6}
/* Process: numbered, with the craft photographs beside it. */
.procgrid{display:grid;gap:34px}
.steps{list-style:none;margin:0;padding:0;counter-reset:s;display:grid;gap:0;border-top:1px solid var(--ink)}
.steps li{counter-increment:s;padding:22px 0;border-bottom:1px solid var(--rule);display:grid;grid-template-columns:52px minmax(0,1fr);gap:12px}
.steps li::before{content:"0" counter(s);font-family:var(--serif);font-size:30px;font-weight:500;color:var(--accent);line-height:.9;padding-top:3px}
.steps h3{font-size:26px;margin-bottom:7px}
.steps p{color:var(--muted);font-size:15.5px;line-height:1.6}
.craft{display:grid;gap:6px;align-content:start}
.craft figure{margin:0;position:relative;overflow:hidden;background:var(--alt)}
.craft img{display:block;width:100%;height:auto;aspect-ratio:4/3;object-fit:cover}
.craft figcaption{font-size:12px;letter-spacing:.16em;text-transform:uppercase;font-weight:600;color:var(--muted);padding:9px 0 2px}
.craft .note{font-size:14px;color:var(--muted);margin-top:8px;max-width:38ch;line-height:1.55}
/* About: dark, the plate beside three points. */
.about{background:var(--dark);color:var(--ondark);padding:64px 0}
.about h2{color:#fff}
.about h2 i{color:var(--flare)}
.about .kicker{color:var(--flare)}.about .kicker::before{background:var(--flare)}
.about .lede{color:var(--dim);margin-top:18px}
.aboutgrid{display:grid;gap:30px;margin-top:30px}
.aboutrow{display:grid;gap:20px;align-content:start}
.aboutrow div{border-left:1px solid var(--accent);padding:2px 0 2px 18px}
.aboutrow strong{font-family:var(--serif);font-size:25px;font-weight:500;display:block;color:#fff;line-height:1.1;margin-bottom:6px}
.aboutrow p{color:var(--dim);font-size:15.5px;line-height:1.6}
.aboutpic{margin:0;overflow:hidden;background:#1C201F}
.aboutpic picture,.aboutpic img{display:block;width:100%;height:auto}
.aboutpic img{aspect-ratio:4/3;object-fit:cover}
.aboutpic figcaption{font-size:12px;letter-spacing:.16em;text-transform:uppercase;font-weight:600;color:var(--dim);padding:10px 0 0}
.about .partners{margin:34px 0 0;padding:22px 0 0;border-top:1px solid rgba(237,232,221,.18);display:flex;flex-wrap:wrap;gap:8px 30px;
font-size:12px;letter-spacing:.2em;text-transform:uppercase;font-weight:600;color:var(--dim)}
.about .partners b{color:var(--flare);font-weight:600}
/* Financing band on the kitchen plate. */
.fin{position:relative;isolation:isolate;overflow:hidden;background:var(--dark);color:#fff;padding:72px 0}
.fin>*:not(.backdrop){position:relative;z-index:1}
.fin .backdrop::after{background:linear-gradient(90deg,rgb(18 21 20/.86) 0%,rgb(18 21 20/.7) 50%,rgb(18 21 20/.3) 100%)}
.fin .backdrop img{object-position:center}
.fin .kicker{color:var(--flare)}.fin .kicker::before{background:var(--flare)}
.fin h2{color:#fff;max-width:14ch}
.fin p{max-width:50ch;font-size:17px;margin:16px 0 26px;color:var(--ondark);opacity:.9;line-height:1.6}
/* Reviews. */
.reviews{display:grid;gap:8px}
.rev{background:var(--paper);padding:30px 26px 24px;border-top:1px solid var(--accent)}
.rev blockquote{margin:0;font-family:var(--serif);font-size:23px;line-height:1.32;font-weight:500}
.rev blockquote::before{content:"“";color:var(--accent);font-size:40px;line-height:0;margin-right:2px;vertical-align:-10px}
.rev footer{margin-top:16px;font-size:12px;letter-spacing:.18em;text-transform:uppercase;font-weight:600;color:var(--muted)}
.stars{color:var(--accent);letter-spacing:.14em;font-size:13px;margin-bottom:12px}
.revlink{margin-top:24px;font-size:15px;color:var(--muted)}
.revlink a{color:var(--ink);font-weight:600;text-decoration:none;border-bottom:1px solid var(--accent)}
/* FAQ. */
.faq{border-top:1px solid var(--ink)}
.faq details{border-bottom:1px solid var(--rule)}
.faq summary{cursor:pointer;list-style:none;padding:18px 40px 18px 0;position:relative;font-family:var(--serif);font-weight:500;font-size:25px;line-height:1.15}
.faq summary::-webkit-details-marker{display:none}
.faq summary::after{content:"+";position:absolute;right:2px;top:14px;color:var(--accent);font-size:30px;line-height:1;font-family:var(--sans);font-weight:300}
.faq details[open] summary::after{content:"–"}
.faq p{color:var(--muted);padding:0 0 20px;max-width:64ch;font-size:15.5px;line-height:1.6}
.towns{list-style:none;margin:22px 0 0;padding:0;display:flex;flex-wrap:wrap;gap:8px}
.towns li{border:1px solid var(--rule);padding:8px 14px;font-size:12px;letter-spacing:.14em;text-transform:uppercase;font-weight:600;color:var(--muted)}
/* Consultation form. */
.quote{background:var(--alt);padding:64px 0}
.quotegrid{display:grid;gap:30px}
.form{display:grid;gap:14px}
.form label{display:grid;gap:6px;font-size:11.5px;letter-spacing:.18em;text-transform:uppercase;font-weight:600;color:var(--muted)}
.form input,.form select,.form textarea{font:inherit;font-size:16px;padding:13px 14px;border:1px solid var(--rule);
background:var(--paper);color:var(--ink);border-radius:0;width:100%;letter-spacing:0;text-transform:none;font-weight:400}
.form input:focus,.form select:focus,.form textarea:focus{outline:1px solid var(--accent);outline-offset:0;border-color:var(--accent)}
.form textarea{min-height:120px;resize:vertical}
.form .row{display:grid;gap:14px}
.form .btn{margin-top:6px;min-height:58px}
.form .fine{font-size:13.5px;color:var(--muted);line-height:1.5}
.form .fine a{color:var(--ink);font-weight:600;text-decoration:none;border-bottom:1px solid var(--accent)}
.form .status{font-size:15px;font-weight:600;color:var(--teal);min-height:1.2em}
.contactcard{border-top:1px solid var(--ink);padding-top:22px;display:grid;gap:14px;align-content:start;font-size:15.5px}
.contactcard strong{font-family:var(--sans);font-size:11.5px;letter-spacing:.18em;text-transform:uppercase;display:block;margin-bottom:3px;color:var(--muted);font-weight:600}
.contactcard a{text-decoration:none;color:var(--ink);font-weight:600}
.contactcard .big{font-family:var(--serif);font-size:30px;font-weight:500;line-height:1.1}
/* Close and footer. */
.close{position:relative;isolation:isolate;overflow:hidden;background:var(--dark);color:#fff;padding:96px 0 104px}
.close>*:not(.backdrop){position:relative;z-index:1}
.close .backdrop::after{background:linear-gradient(180deg,rgb(18 21 20/.55) 0%,rgb(18 21 20/.35) 45%,rgb(18 21 20/.86) 100%)}
.close .backdrop img{object-position:center 60%}
.close .kicker{color:var(--flare)}.close .kicker::before{background:var(--flare)}
.close h2{max-width:15ch;color:#fff;font-size:clamp(40px,7.4vw,84px)}
.close h2 i{color:var(--flare)}
.close p{max-width:50ch;font-size:17px;margin:18px 0 28px;color:var(--ondark);opacity:.9;line-height:1.6}
.foot{background:var(--dark);color:var(--dim);padding:0 0 34px;font-size:14.5px;border-top:1px solid var(--accent)}
.foot .wrap{padding-top:38px}
.foot .brand{display:inline-block;margin-bottom:16px}
.foot p{margin:0 0 9px;max-width:66ch;line-height:1.6}
.foot a{color:var(--ondark);text-decoration:none}
.foot a:hover{color:var(--flare)}
.foot .fine{font-size:12.5px;color:#7F847E;margin-top:18px}
.callbar{position:fixed;left:0;right:0;bottom:0;z-index:40;background:var(--dark);border-top:1px solid var(--accent);
display:grid;grid-template-columns:1fr auto;gap:6px;padding:6px}
.callbar a{display:flex;align-items:center;justify-content:center;min-height:58px;text-decoration:none;text-align:center;
font-weight:600;line-height:1.1;padding:0 12px;letter-spacing:.14em;text-transform:uppercase;font-size:12.5px}
.callbar .tel{background:var(--accent);color:#fff}
.callbar .alt2{color:var(--ondark);border:1px solid rgba(237,232,221,.42);max-width:150px}
@media(max-width:559px){.navact{display:none}}
@media(min-width:700px){.topbar .wrap span+span{display:inline}
.numbers{grid-template-columns:repeat(4,1fr);column-gap:26px}.svc{grid-template-columns:1fr 1fr;column-gap:52px}
.galgrid{grid-template-columns:repeat(3,1fr)}.gal figure.feature{grid-column:1/3;grid-row:1/3}
.reviews{grid-template-columns:1fr 1fr 1fr}.form .row{grid-template-columns:1fr 1fr}
.sec,.gal,.quote,.about{padding:96px 0}.hero .wrap{padding-top:120px;padding-bottom:52px}
.hero .sub{font-size:19px}.btn{min-height:60px}.head{grid-template-columns:minmax(0,1.1fr) minmax(0,1fr);align-items:end;gap:40px;margin-bottom:44px}
.head .lede{padding-bottom:6px}.craft{grid-template-columns:1fr 1fr 1fr}}
@media(min-width:900px){.aboutgrid{grid-template-columns:minmax(0,1fr) minmax(0,1.05fr);align-items:center;gap:56px}
.aboutrow{gap:24px}.quotegrid{grid-template-columns:minmax(0,1.35fr) minmax(0,1fr);gap:64px}
.procgrid{grid-template-columns:minmax(0,1.15fr) minmax(0,1fr);gap:56px;align-items:start}.craft{grid-template-columns:1fr 1fr}
.craft figure:first-child{grid-column:1/-1}}
@media(min-width:1000px){body{padding-bottom:0}.callbar{display:none}.navlinks{display:flex}
.navact{margin-left:18px}.hero .wrap{padding-top:150px;padding-bottom:64px}}
/* Between 1000 and 1200px the links, the number and the button do not all fit: the
   number waits for 1200px, and so does the last link. */
@media(min-width:1000px) and (max-width:1239px){.navlinks{gap:20px}.navlinks a:last-child{display:none}}
@media(min-width:1240px){.navtel{display:inline}}
/* Motion: gated on .m, which only the script adds, so nothing hides without JS. */
.m [data-reveal]{opacity:0;transform:translateY(16px);transition:opacity .8s cubic-bezier(.2,.6,.2,1),transform .8s cubic-bezier(.2,.6,.2,1)}
.m [data-reveal].in{opacity:1;transform:none}
.m .gal figure[data-reveal]:nth-child(3n+2){transition-delay:.08s}
.m .gal figure[data-reveal]:nth-child(3n){transition-delay:.16s}
@keyframes hero-in{from{opacity:0}to{opacity:1}}
.m .hero .wrap{animation:hero-in 1.2s ease-out both}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}
.m [data-reveal]{opacity:1;transform:none;transition:none}.m .hero .wrap{animation:none}
.backdrop video{display:none}.gal img{transition:none}.gal figure:hover img{transform:none}}
</style>
</head>
<body>
<div class="topbar"><div class="wrap"><span>Licensed, bonded &amp; insured · WA L&amp;I #$lni</span><span>#1 TrexPRO Platinum partner in Washington · <a href="$instagram" rel="noopener">Instagram</a> · <a href="$google" rel="noopener">Google</a></span></div></div>
<header class="nav"><div class="wrap">
  <a class="brand" href="#top"><span class="lockup">$mark<span>$name</span></span></a>
  <nav class="navlinks"><a href="#work">Work</a><a href="#services">Services</a><a href="#process">Process</a><a href="#about">About</a><a href="#reviews">Reviews</a><a href="#faq">Questions</a></nav>
  <a class="navtel" href="tel:$tel">$phone</a>
  <a class="navact" href="#consult">Request a consultation</a>
</div></header>
<section class="hero" id="top">
  <div class="backdrop" aria-hidden="true">$hero_pic<video muted loop playsinline autoplay preload="metadata" poster="$hero_poster" data-phone="assets/hero/lakefront-1280.mp4"><source src="assets/hero/lakefront.mp4" type="video/mp4"></video></div>
  <div class="wrap">
    <p class="eyebrow">$tagline · Puget Sound</p>
    <h1>Built to the standard <i>of the home.</i></h1>
    <p class="sub">$name is a design-build remodeler for the Puget Sound's finer homes: outdoor living, kitchens and baths, exteriors and whole-home renovations, managed by one team from the first drawing to the final inspection.</p>
    <div class="ctas">
      <a class="btn btn-primary" href="#consult">Request a consultation</a>
      <a class="btn btn-ghost" href="#work">See the work</a>
    </div>
    <ul class="numbers">
$numbers
    </ul>
  </div>
</section>
<section class="strip"><div class="wrap">
  <span class="lead">Partners</span><span>Trex · TrexPRO Platinum</span><span>The Home Depot</span><span>Upgrade financing</span><span>Family-owned, veteran-operated</span>
</div></section>
<section class="gal" id="work"><div class="wrap">
  <div class="head">
    <div><p class="kicker">The work</p><h2>Outdoor rooms, kitchens, baths and the houses <i>around them.</i></h2></div>
    <p class="lede">Decks over the Sound, a lakefront pavilion, a primary bath in slab, a standing-seam roof. All of it ours, across $area_long.</p>
  </div>
  <div class="galgrid">
$tiles
  </div>
  <p class="more">More on <a href="$instagram" rel="noopener">Instagram</a>.</p>
</div></section>
<section class="sec paper" id="services"><div class="wrap">
  <div class="head">
    <div><p class="kicker">Services</p><h2>One team, inside <i>and out.</i></h2></div>
    <p class="lede">A true one-stop shop: from a single room to a full-scale renovation, every trade under one project manager, so you are never the one coordinating the schedule.</p>
  </div>
  <div class="svc">
$services
  </div>
</div></section>
<section class="sec alt" id="process"><div class="wrap">
  <div class="head">
    <div><p class="kicker">Process</p><h2>How a project <i>actually runs.</i></h2></div>
    <p class="lede">The part most remodelers leave vague, which is the part you are wondering about while the kitchen is still in boxes.</p>
  </div>
  <div class="procgrid">
    <ol class="steps">
$steps
    </ol>
    <div class="craft">
$craft
      <p class="note">A deck rebuild in Sammamish, from the reel: new footings and a poured stair before a board goes down. The finish is only as good as this.</p>
    </div>
  </div>
</div></section>
<section class="about" id="about"><div class="wrap">
  <p class="kicker">About</p>
  <h2>Local company, national <i>backing.</i></h2>
  <p class="lede">$name is a family-owned, veteran-operated general contractor based in $town, with more than a decade shaping Washington's residential construction and the strength of a nationwide network behind it. Over 3,000 projects in 2025 and more than $$250M in the last five years, and still mostly hired by word of mouth.</p>
  <div class="aboutgrid">
    <div class="aboutrow">
$about
    </div>
    <figure class="aboutpic">$about_pic<figcaption>Every project starts on paper</figcaption></figure>
  </div>
  <p class="partners"><b>Registered</b><span>WA L&amp;I #$lni</span><span>UBI $ubi</span><span>Licensed, bonded &amp; insured</span></p>
</div></section>
<section class="fin" id="financing">
  <div class="backdrop" aria-hidden="true">$fin_pic</div>
  <div class="wrap">
    <p class="kicker">Financing</p>
    <h2>Up to 100% of the project, financed.</h2>
    <p>We partner with financing firms that can cover the whole project, with options tailored to different budgets, so the right scope does not have to wait for the right year.</p>
    <a class="btn btn-primary" href="#consult">Ask about financing</a>
  </div>
</section>
<section class="sec" id="reviews"><div class="wrap">
  <div class="head">
    <div><p class="kicker">Reviews</p><h2>What clients say <i>afterwards.</i></h2></div>
    <p class="lede">Google reviews, in the clients' own words.</p>
  </div>
  <div class="reviews">
$reviews
  </div>
  <p class="revlink">Read more, or leave one: <a href="$google" rel="noopener">$name on Google</a>.</p>
</div></section>
<section class="sec paper" id="faq"><div class="wrap">
  <div class="head">
    <div><p class="kicker">Fair questions</p><h2>Before you <i>call.</i></h2></div>
  </div>
  <div class="faq">
$faq
  </div>
</div></section>
<section class="sec alt" id="area"><div class="wrap">
  <div class="head">
    <div><p class="kicker">Service area</p><h2>South Sound to the <i>Eastside.</i></h2></div>
    <p class="lede">Based in $town, serving $area_long. If you are a little outside the towns below, ask anyway.</p>
  </div>
  <ul class="towns">
$towns
  </ul>
</div></section>
<section class="quote" id="consult"><div class="wrap">
  <div class="head">
    <div><p class="kicker">Consultation</p><h2>Tell us about <i>the house.</i></h2></div>
    <p class="lede">Rough numbers are fine. We will come back to you to set up a visit, walk the property and talk it through. No charge, no obligation.</p>
  </div>
  <div class="quotegrid">
    <form class="form" id="quoteform" action="$form_action" method="post" enctype="text/plain">
      <div class="row">
        <label>Name<input name="name" autocomplete="name" required></label>
        <label>Phone<input name="phone" type="tel" autocomplete="tel" required></label>
      </div>
      <div class="row">
        <label>Email<input name="email" type="email" autocomplete="email"></label>
        <label>Town<input name="town" autocomplete="address-level2" placeholder="$town_placeholder"></label>
      </div>
      <div class="row">
        <label>Project<select name="project">
          <option>Outdoor living: deck, patio, pergola</option><option>Kitchen</option><option>Bathroom</option>
          <option>Whole-home remodel or addition</option><option>Roofing or gutters</option><option>Windows, doors or siding</option>
          <option>Exterior paint or stucco</option><option>Flooring or interior finishes</option><option>Something else</option>
        </select></label>
        <label>Budget<select name="budget">
          <option>Not sure yet</option><option>Under $$25,000</option><option>$$25,000 to $$50,000</option>
          <option>$$50,000 to $$100,000</option><option>$$100,000 to $$250,000</option><option>Over $$250,000</option>
        </select></label>
      </div>
      <label>Timing<select name="timing"><option>As soon as possible</option><option>In the next three months</option><option>Later this year</option><option>Just planning</option></select></label>
      <label>About the project<textarea name="notes" placeholder="The house, the room or the yard, what you want it to do, anything you already know you want..."></textarea></label>
      <button class="btn btn-primary" type="submit">Request a consultation</button>
      <p class="status" role="status" aria-live="polite"></p>
      <p class="fine">Or call <a href="tel:$tel">$phone</a>. Either way, a person answers.</p>
    </form>
    <div class="contactcard">
      <div><strong>Call</strong><a class="big" href="tel:$tel">$phone</a></div>
      <div><strong>Also</strong><a href="tel:$tel2">$phone2</a></div>
$email_row
      <div><strong>Office</strong>$street<br>$town $zip</div>
      <div><strong>Registered contractor</strong>WA L&amp;I #$lni · UBI $ubi · Bonded &amp; insured</div>
      <div><strong>Elsewhere</strong><a href="$instagram" rel="noopener">Instagram</a> · <a href="$facebook" rel="noopener">Facebook</a> · <a href="$yelp" rel="noopener">Yelp</a></div>
    </div>
  </div>
</div></section>
<section class="close" id="contact">
  <div class="backdrop" aria-hidden="true">$close_pic</div>
  <div class="wrap">
    <p class="kicker">Start here</p>
    <h2>The house you already have, <i>finished properly.</i></h2>
    <p>One consultation, one design, one team through to the final inspection. Call, or tell us about the project and we will come to you.</p>
    <div class="ctas">
      <a class="btn btn-primary" href="#consult">Request a consultation</a>
      <a class="btn btn-ghost" href="tel:$tel">Call $phone</a>
    </div>
  </div>
</section>
<footer class="foot">
  <div class="wrap">
  <a class="brand" href="#top"><span class="lockup">$mark<span>$name</span></span></a>
  <p><a href="tel:$tel">$phone</a> · <a href="tel:$tel2">$phone2</a>$email_foot</p>
  <p>$legal · $street, $town $zip</p>
  <p>WA L&amp;I registered contractor #$lni · UBI $ubi · Licensed, bonded and insured · <a href="$instagram" rel="noopener">Instagram</a> · <a href="$facebook" rel="noopener">Facebook</a> · <a href="$yelp" rel="noopener">Yelp</a> · <a href="$google" rel="noopener">Google</a></p>
  <p><a href="$careers" rel="noopener">Careers</a> · <a href="$blog" rel="noopener">Journal</a></p>
  <p class="fine">Site by <a href="https://grandstreetworks.com">Grand Street Works</a>.</p>
</div></footer>
<div class="callbar"><a class="tel" href="tel:$tel">Call $phone</a><a class="alt2" href="#consult">Consultation</a></div>
<script>
(function () {
  /* Consultation form. With an endpoint configured it posts JSON; with an
     email it hands the fields to the mail client (which is also what the
     form does on its own when this script never runs); with neither it
     opens a text message to the office on phones and says to call on
     desktops. */
  var ENDPOINT = $endpoint_json, EMAIL = $email_json, SMS = $sms_json;
  var form = document.getElementById('quoteform');
  var status = form.querySelector('.status');
  form.addEventListener('submit', function (ev) {
    ev.preventDefault();
    var data = {};
    new FormData(form).forEach(function (v, k) { data[k] = v; });
    var body = Object.keys(data).map(function (k) { return k + ': ' + data[k]; }).join('\n');
    if (ENDPOINT) {
      status.textContent = 'Sending...';
      fetch(ENDPOINT, { method: 'POST', headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(data) })
        .then(function (r) { if (!r.ok) throw new Error(r.status); form.reset();
                             status.textContent = 'Got it. We will be in touch to set up the visit.'; })
        .catch(function () { status.textContent = 'That did not go through. Call us and we will sort it out.'; });
      return;
    }
    if (EMAIL) {
      window.location.href = 'mailto:' + EMAIL
        + '?subject=' + encodeURIComponent('Consultation request from ' + (data.name || 'the website'))
        + '&body=' + encodeURIComponent(body);
      status.textContent = 'Opening your mail app. If nothing happens, call us instead.';
      return;
    }
    if (/Android|iPhone|iPad/i.test(navigator.userAgent)) {
      window.location.href = 'sms:' + SMS + '?&body=' + encodeURIComponent(body);
      status.textContent = 'Opening a text message with the details. If nothing happens, call us instead.';
    } else {
      status.textContent = 'Call us on ' + $phone_json + ' and mention the details above, or send this from your phone.';
    }
  });

  /* The hero loop fades in over its poster once it is actually playing.
     Phones get the 1280px cut (the hero is cropped to its middle there
     anyway); a connection that asks for less data gets the still. */
  var v = document.querySelector('.hero video');
  if (v) {
    var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var net = navigator.connection || {};
    var lean = net.saveData || /(^|-)2g$$/.test(net.effectiveType || '');
    if (reduce || lean) { v.pause(); v.removeAttribute('autoplay'); v.remove(); }
    else {
      if (window.matchMedia('(max-width: 899px)').matches && v.dataset.phone) {
        v.querySelector('source').src = v.dataset.phone; v.load();
      }
      var on = function () { v.classList.add('playing'); };
      v.addEventListener('playing', on);
      if (!v.paused && v.readyState >= 3) on();
      v.play().catch(function () {});
    }
  }

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


def tel_link(phone: str) -> str:
    digits = re.sub(r"\D", "", phone)
    return ("+1" + digits) if len(digits) == 10 else "+" + digits


def build_page() -> None:
    c = CONFIG
    tel, tel2 = tel_link(c["phone"]), tel_link(c["phone2"])
    description = (f"Design-build remodeling in {c['area_long']}: outdoor living and decks, "
                   f"kitchens and bathrooms, roofing, windows and doors, exterior paint and "
                   f"whole-home renovations, with permits and inspections handled. Washington's "
                   f"#1 TrexPRO Platinum partner. WA L&I #{c['lni']}, bonded and insured.")
    mark = mark_svg(PALETTE["flare"])

    numbers = "\n".join(
        f'      <li><b>{html.escape(n)}</b><span>{html.escape(t)}</span></li>' for n, t in NUMBERS)
    services = "\n".join(
        f'    <article class="sv"><div class="num">{i:02d}</div><div><h3>{t}</h3><p>{p}</p></div></article>'
        for i, (t, p) in enumerate(SERVICES, 1))
    about = "\n".join(
        f'      <div><strong>{html.escape(t)}</strong><p>{html.escape(p)}</p></div>' for t, p in ABOUT)
    steps = "\n".join(
        f'      <li><div><h3>{t}</h3><p>{html.escape(p)}</p></div></li>' for t, p in STEPS)
    reviews = "\n".join(
        f'    <article class="rev"><div class="stars" aria-label="Five stars">★★★★★</div>'
        f'<blockquote>{html.escape(q)}</blockquote><footer>{html.escape(n)} · Google review</footer></article>'
        for q, n in REVIEWS)
    faq = "\n".join(
        f'    <details><summary>{html.escape(q)}</summary><p>{html.escape(a)}</p></details>'
        for q, a in FAQ)
    towns = "\n".join(f'    <li>{html.escape(t)}</li>' for t in c["towns"])
    tiles = "\n".join(
        f'    <figure class="{kind}">'
        + picture(n, cap, "(max-width: 700px) 100vw, 66vw" if kind == "feature" else "(max-width: 700px) 50vw, 33vw")
        + f'<figcaption>{html.escape(cap)}</figcaption></figure>' for n, cap, kind in TILES)
    craft = "\n".join(
        f'      <figure>{picture(n, cap, "(max-width: 700px) 100vw, 40vw")}'
        f'<figcaption>{html.escape(cap)}</figcaption></figure>' for n, cap in CRAFT)

    email_row = (f'      <div><strong>Email</strong><a href="mailto:{html.escape(c["email"])}">{html.escape(c["email"])}</a></div>'
                 if c["email"] else "")
    email_foot = f' · <a href="mailto:{html.escape(c["email"])}">{html.escape(c["email"])}</a>' if c["email"] else ""
    # Without JavaScript the form still goes somewhere: the mailbox if there
    # is one, otherwise the office number as an SMS link (phones honour it).
    form_action = f"mailto:{c['email']}" if c["email"] else f"sms:{tel}"

    page = PAGE.substitute(
        name=html.escape(c["name"]), legal=html.escape(c["legal"]),
        tagline=TAGLINE, headline=HEADLINE, description=html.escape(description),
        phone=html.escape(c["phone"]), tel=tel, phone2=html.escape(c["phone2"]), tel2=tel2,
        street=html.escape(c["street"]), town=html.escape(c["town"]), zip=c["zip"],
        town_placeholder=html.escape(c["town"].split(",")[0]),
        area_long=html.escape(c["area_long"]),
        lni=html.escape(c["lni"]), ubi=html.escape(c["ubi"]),
        facebook=html.escape(c["facebook"]), instagram=html.escape(c["instagram"]),
        yelp=html.escape(c["yelp"]), google=html.escape(c["google"]),
        careers=html.escape(c["careers"]), blog=html.escape(c["blog"]),
        url=c["url"], dark=PALETTE["dark"], jsonld=jsonld(), mark=mark,
        hero_pic=picture("hero", "", "100vw", eager=True), hero_poster=jpeg_path("hero"),
        close_pic=picture("dusk", "", "100vw"),
        fin_pic=picture("kitchen", "", "100vw"),
        about_pic=picture("plans", "Deck and patio drawings on a table with a composite decking sample and a white oak flooring sample", "(max-width: 900px) 100vw, 50vw"),
        numbers=numbers, services=services, about=about, steps=steps, reviews=reviews,
        faq=faq, towns=towns, tiles=tiles, craft=craft,
        email_row=email_row, email_foot=email_foot, form_action=form_action,
        endpoint_json=json.dumps(c["quote_endpoint"]), email_json=json.dumps(c["email"]),
        sms_json=json.dumps(tel), phone_json=json.dumps(c["phone"]),
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
