#!/usr/bin/env python3
"""Build the Essential Fence Center site: sites/essential-fence-center/.

A real client site rather than a reference build, so it does not live under
work/ (which is noindex and says "fictional" in every footer). It is fully
self-contained, with its own encoded images and identity under
sites/essential-fence-center/assets/, so the folder can be dropped onto the
client's own domain unchanged.

Facts (name, phone, address, hours, L&I number, service area, services, FAQ,
reviews) come from the client's existing site, essentialfencecenter.com, and
from the WA L&I register. Anything the client will want changed lives in
CONFIG or the copy tables below. Change it there and rerun.

    python3 tools/build-fencing-site.py            # images, identity, page
    python3 tools/build-fencing-site.py --page     # just rewrite index.html

Images: the client's own job photographs (from their gallery page) plus two
Gemini backdrops from tools/gen-fencing-images.py. Originals live in
~/fractal/clients/essential-fence-center/originals and only the encoded ladder
is written into the repo. Needs avifenc, sips, and headless Chrome for the
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
SLUG = "essential-fence-center"
SITE_DIR = REPO / "sites" / SLUG
IMG = SITE_DIR / "assets" / "img"
IDENTITY = SITE_DIR / "assets" / "identity"
ORIGINALS = Path.home() / "fractal" / "clients" / SLUG / "originals"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# --- the client -----------------------------------------------------------
CONFIG = {
    "name": "Essential Fence Center",
    "legal": "Essential Fence Center, LLC",
    "phone": "(425) 387-6308",
    "email": "rlcole2257@gmail.com",
    "street": "6713 87th Avenue SE",
    "town": "Snohomish, WA",
    "zip": "98290",
    "lat": 47.9339282, "lng": -122.1138068,
    "area_long": "Snohomish County and Washington State",
    # The service-area list from their contact page, in their order.
    "towns": ["Snohomish", "Monroe", "Marysville", "Everett", "Granite Falls",
              "Stanwood", "Sultan", "Woodinville", "Bothell", "Lynnwood", "Edmonds",
              "Shoreline", "Bellevue", "Redmond", "Arlington", "Carnation",
              "Lake Stevens", "Mill Creek", "Mukilteo", "Gold Bar"],
    # WA L&I construction contractor registration, active, expires 2027-02-19.
    "lni": "ESSENFC796CE",
    "hours": "Monday to Friday, 9am to 5pm",
    "hours_schema": "Mo-Fr 09:00-17:00",
    "years": "45",
    "facebook": "https://www.facebook.com/essentialfencecenter/",
    "google": ("https://www.google.com/maps/place/Essential+Fence+Center/"
               "@47.9334861,-122.1108886,16z/data=!4m13!1m7!3m6!1s0x549aa99034d4b59f:0x411e487eb55b76b2"
               "!2s6713+87th+Ave+SE,+Snohomish,+WA+98290,+USA!3b1!8m2!3d47.9339282!4d-122.1138068"
               "!3m4!1s0x549aa969678dc423:0x2785cc8c5b29b058!8m2!3d47.9339282!4d-122.1138068"),
    # Public URL the site will live at; only used for og:image and JSON-LD.
    "url": "https://grandstreetworks.com/sites/essential-fence-center/",
    # Optional POST endpoint for the estimate form. Empty means the form falls
    # back to composing an email with the fields filled in.
    "quote_endpoint": "",
}

TAGLINE = "Cedar, chain link and ornamental iron"
HEADLINE = "Fencing done right."   # the client's own tagline

# --- images ---------------------------------------------------------------
HERO_AVIF = (1280, 2560)
HERO_JPEG = 1280
TILE_AVIF = (640, 1280)
TILE_JPEG = 720
AVIF_Q, AVIF_SPEED = "50", "6"
JPEG_Q = "62"

# name -> kind. "wide" images are full-bleed backdrops (Gemini), "tile" images
# are the client's own photographs, which come in every size and are never
# upscaled: each gets only the rungs of the ladder its original can fill.
IMAGES = {
    "hero": "wide", "farmhouse": "wide",
    "staining": "tile", "estate-cedar": "tile", "high-five-stair-step": "tile",
    "galvanized-high-five-gate": "tile", "modified-panel": "tile",
    "modified-panel-2": "tile", "radius": "tile", "cedar-double-drive-gate": "tile",
    "black-chain-link-slats": "tile", "ornamental-iron": "tile",
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
        widths = [x for x in widths if x <= w] or [w]
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


# --- identity -------------------------------------------------------------
# The client's own mark is a red roundel with "EFC" in it (logo.png on their
# site, 200px). Redrawn as SVG so it survives a favicon and a social card.
PALETTE = {"ink": "#1C1C1E", "surface": "#F5F1E9", "accent": "#8F2429",
           "flare": "#E7787C", "dark": "#1C1C1E", "white": "#FFFFFF"}

MARK_INNER = """\
<circle cx="32" cy="32" r="30" fill="{ring}"/>
<circle cx="32" cy="32" r="20.5" fill="{face}"/>
<text x="32" y="39.5" text-anchor="middle" font-family="Barlow Condensed,Arial Narrow,Arial,Helvetica,sans-serif" font-weight="700" font-size="22" letter-spacing="-.5" fill="{letters}">EFC</text>"""


def mark_svg(ring: str, face: str, letters: str, size: int | None = None,
             label: str | None = None) -> str:
    attrs = f' width="{size}" height="{size}"' if size else ""
    a11y = (f' role="img" aria-label="{html.escape(label)}"' if label
            else ' aria-hidden="true" focusable="false"')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"{attrs}{a11y}>'
            + MARK_INNER.format(ring=ring, face=face, letters=letters) + "</svg>")


def favicon_svg() -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" '
            f'aria-label="{html.escape(CONFIG["name"])}">'
            + MARK_INNER.format(ring=PALETTE["accent"], face=PALETTE["white"],
                                letters=PALETTE["ink"])
            + "</svg>")


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
             '<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700'
             '&family=Barlow:wght@400;500&display=swap" rel="stylesheet">')


def og_card() -> str:
    c = CONFIG
    return f"""<!doctype html><meta charset="utf-8">
{FONT_LINK}
<style>
  *{{margin:0;box-sizing:border-box}}
  body{{width:1200px;height:630px;background:{PALETTE['dark']};color:{PALETTE['surface']};
       font:400 26px/1.5 Barlow,system-ui,sans-serif;padding:64px 84px 70px;
       display:flex;flex-direction:column;justify-content:space-between;overflow:hidden;position:relative}}
  .top{{display:flex;align-items:center;gap:26px}}
  .name{{font-family:"Barlow Condensed",Impact,sans-serif;font-weight:700;font-size:60px;
        line-height:1;text-transform:uppercase;letter-spacing:.02em}}
  h1{{font-family:"Barlow Condensed",Impact,sans-serif;font-weight:700;font-size:128px;
     line-height:.96;max-width:20ch;text-transform:uppercase;letter-spacing:.005em}}
  .rule{{height:8px;background:{PALETTE['accent']};width:132px;margin:30px 0 26px}}
  .foot{{display:flex;justify-content:space-between;align-items:baseline;
        font-size:28px;color:{PALETTE['flare']};letter-spacing:.04em}}
  .foot .trade{{color:{PALETTE['surface']};opacity:.62;text-transform:uppercase;
               letter-spacing:.18em;font-size:19px;font-weight:500;white-space:nowrap}}
  .boards{{position:absolute;left:0;right:0;bottom:0;height:22px;
          background:repeating-linear-gradient(90deg,#3B3F3A 0 44px,#22282A 44px 48px)}}
</style>
<div class="top">{mark_svg(PALETTE['accent'], PALETTE['white'], PALETTE['ink'], 84)}<div class="name">{html.escape(c['name'])}</div></div>
<div><div class="rule"></div><h1>{html.escape(HEADLINE)}</h1></div>
<div class="foot"><span>{html.escape(c['phone'])}</span><span class="trade">{html.escape(TAGLINE)} · Snohomish, WA</span></div>
<div class="boards"></div>
"""


def build_identity(force: bool) -> None:
    IDENTITY.mkdir(parents=True, exist_ok=True)
    (IDENTITY / "mark.svg").write_text(
        mark_svg(PALETTE["accent"], PALETTE["white"], PALETTE["ink"], label=CONFIG["name"]))
    (IDENTITY / "icon.svg").write_text(favicon_svg())
    png180 = IDENTITY / "icon-180.png"
    if force or not png180.exists():
        shot(FONT_LINK + "<style>*{margin:0}body{width:180px;height:180px;background:#fff}"
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
        "@type": "HomeAndConstructionBusiness",
        "name": c["name"],
        "legalName": c["legal"],
        "description": f"Fence installation in {c['area_long']}: cedar and wood, chain link, "
                       f"ornamental iron, gates and operators, repairs and DIY material packages.",
        "telephone": c["phone"],
        "email": c["email"],
        "url": c["url"],
        "image": c["url"] + "assets/identity/og.png",
        "logo": c["url"] + "assets/identity/mark.svg",
        "sameAs": [c["facebook"]],
        "address": {"@type": "PostalAddress", "streetAddress": c["street"],
                    "addressLocality": c["town"].split(",")[0].strip(),
                    "addressRegion": "WA", "postalCode": c["zip"], "addressCountry": "US"},
        "geo": {"@type": "GeoCoordinates", "latitude": c["lat"], "longitude": c["lng"]},
        "areaServed": [{"@type": "City", "name": t} for t in c["towns"]],
        "openingHours": c["hours_schema"],
        "paymentAccepted": "Cash, Visa, MasterCard",
        "priceRange": "$$",
    }
    return ('<script type="application/ld+json">'
            + json.dumps(data, separators=(",", ":")) + "</script>")


# Copy below is drawn from the client's site: their service pages, gallery
# captions, FAQ and reviews. Claims are theirs; the phrasing is tightened.
SERVICES = [
    ("Cedar &amp; wood fences",
     "Ten-plus styles: estate cedar, modified panel, High Five, horizontal, split "
     "rail and three-rail horse fence. Every board hand-picked from select "
     "distributors."),
    ("Galvanized chain link",
     "The workhorse for yards, dog runs, kennels and commercial lots. Galvanized "
     "mesh and posts, with matching walk and drive gates."),
    ("Black &amp; colored chain link",
     "Black or colored vinyl-coated mesh that reads as a line rather than a fence, "
     "with black slats when you want privacy too."),
    ("Ornamental iron",
     "Three-rail ornamental iron for front yards, driveways and pool surrounds, "
     "with matching walk gates and drive gates."),
    ("Gates &amp; operators",
     "Steel-frame gates on wood, double drive or single slider. Electric and solar "
     "gate operators: we are a Ghost Controls distributor and we install them."),
    ("Repairs, kennels &amp; DIY packages",
     "Repairs that do not mean redoing the whole fence. Chain link dog kennels. "
     "And if you would rather build it yourself, we measure your footage, put a "
     "material package together and deliver it."),
]

ABOUT = [
    ("Hand-picked material",
     "We hand pick each piece from a few select distributors, so the fence lasts "
     "up to your expectations at a competitive price, without sacrificing the "
     "workmanship."),
    ("Posts that stay straight",
     "Fifty-plus years of experience. We can plate a post to a sound concrete pad, "
     "and attach to the house by nailing to the siding or bolting to concrete."),
    ("Repair before rebuild",
     "Depending on the shape of the fence, a repair can still get you a perfect "
     "fence. We will tell you which it is, and we look for ways to save you money."),
]

STEPS = [
    ("Free onsite estimate",
     "Call or message us. We come out, measure the run, talk through the styles "
     "and price it. No charge, no obligation."),
    ("Utilities marked",
     "We schedule a locator to come out and mark underground utilities before "
     "anyone digs."),
    ("Tear-out and build",
     "We tear out and haul the old fence for a charge, cut old posts at ground "
     "level unless we are pulling them, and set the new ones. Each job is "
     "different; we tell you how many days at the estimate."),
    ("Gates, hardware, walkthrough",
     "A bigger gate just needs bigger posts and more concrete. Openers are wired "
     "and tested, then we walk the line with you."),
]

# Verbatim from the client's site. Hana's is an excerpt.
REVIEWS = [
    ("Randy does amazing work. He always knows exactly what needs to be done and "
     "does it with extreme excellence. I also really appreciate that he finds ways "
     "to repair things and save me money. All the fencing is always very durable "
     "and holds up to a lot of wear and tear. Both Sue and Randy are always very "
     "responsive, professional, and easy to communicate with.",
     "Hana S.", "Cool Caninez dog boarding &amp; daycare"),
    ("It looks great. Your guys were so kind as well. Thank you so much for all of "
     "your help!", "Melissa H.", "Homeowner"),
    ("Thank you! All my neighbors are envious of the fence and I LOVE it. I finally "
     "feel like I have some semblance of privacy.", "Amy M.", "Homeowner"),
]

# From the client's FAQ page, lightly edited.
FAQ = [
    ("Do you take the old fence with you?",
     "Yes. We tear out and haul the old fence for a charge."),
    ("Can you mark underground utilities?",
     "We schedule a locator to come out and mark utilities before we dig."),
    ("Can you repair my fence without redoing everything?",
     "Yes. Depending on the shape of the fence, you can do a repair and still get "
     "a perfect fence."),
    ("Can I have a different style of fence?",
     "Of course. There are ten-plus styles to choose from, and you can see most of "
     "them in the work above."),
    ("Can you attach to the house, or plate a post to the patio?",
     "Yes. We can nail to the siding or bolt to the concrete, and as long as the "
     "concrete pad is in good shape we can plate a post to it."),
    ("Can I have a bigger gate, or make my gate automatic?",
     "Usually, yes. A bigger gate just needs bigger posts with more concrete. We "
     "are a Ghost Controls distributor and we install the operators."),
    ("Do you take the old concrete?",
     "Only if we are pulling the posts. Otherwise we cut the post at ground level "
     "and leave the concrete."),
    ("Do you offer any specials or discounts?",
     "Yes. A senior discount, a veterans discount, and a discount for saying you "
     "saw us on the website."),
    ("How long will the job take?",
     "Each job is different and depends on the size and the days scheduled. We "
     "tell you at the estimate."),
    ("Do you love dogs?",
     "Yes! We all love dogs."),
]

# The client's own photographs, with their gallery captions.
TILES = [
    ("estate-cedar", "Estate cedar"),
    ("high-five-stair-step", "Galvanized High Five, stair-stepped"),
    ("galvanized-high-five-gate", "Galvanized High Five with double drive gate"),
    ("modified-panel", "Modified panel"),
    ("cedar-double-drive-gate", "Steel-frame cedar double drive gate"),
    ("black-chain-link-slats", "Black chain link with black slats"),
    ("ornamental-iron", "Three-rail ornamental iron"),
    ("radius", "A radius corner"),
    ("modified-panel-2", "Modified panel, on a slope"),
]


PAGE = Template(r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<script>/* Relative asset paths need the directory URL: send /sites/x to /sites/x/. */
if(!/\/$$|\.[a-z0-9]+$$/i.test(location.pathname))location.replace(location.pathname+'/'+location.search+location.hash)</script>
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>$name · Fence installation in Snohomish, WA</title>
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
/* THE FENCE LINE ONE, for Essential Fence Center. hero:backdrop nav:bar
   services:grid-numbered proof:about + the client's own photographs
   ink #1C1C1E · surface #F5F1E9 · accent #8F2429 (the EFC roundel red) · muted #5C6360
   Barlow Condensed display / Barlow body
   Device: the board band, a run of vertical cedar boards with two rails, closing the
   hero and signing the footer. The phone is the hero's largest object; the estimate
   form is the second CTA everywhere. Built from the Grand Street Works trade set. */
:root{--ink:#1C1C1E;--surface:#F5F1E9;--accent:#8F2429;--accent-2:#7A1D22;--muted:#5C6360;--dark:#1C1C1E;
--ondark:#EFEAE0;--dim:#B9BDB6;--flare:#E7787C;--rule:rgba(28,28,30,.16);--hair:rgba(28,28,30,.09);
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
.btn-primary:hover{background:var(--accent-2)}
.btn-ghost{background:transparent;color:var(--ondark);border-color:rgba(239,234,224,.4)}
.btn-ghost:hover{border-color:var(--flare);color:var(--flare)}
.topbar{background:var(--gap);color:#C6CABF;font-size:14px}
.topbar .wrap{padding:8px 20px;letter-spacing:.06em;text-transform:uppercase;font-weight:500;
display:flex;justify-content:space-between;gap:16px}
.topbar a{text-decoration:none}
.topbar a:hover{color:#fff}
.topbar .wrap span+span{display:none}
.nav{position:sticky;top:0;z-index:30;background:var(--dark);border-bottom:2px solid var(--accent)}
.nav .wrap{display:flex;align-items:center;gap:10px;height:62px}
.brand{font-family:"Barlow Condensed",Impact,sans-serif;font-weight:700;font-size:24px;color:#fff;
text-decoration:none;text-transform:uppercase;letter-spacing:.03em;flex:none;line-height:1}
.lockup{display:inline-flex;align-items:center;gap:.42em}
.lockup svg{height:1.45em;width:auto;flex:none;display:block}
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
background:linear-gradient(100deg,rgb(28 28 30/.92) 0%,rgb(28 28 30/.84) 40%,rgb(28 28 30/.5) 72%,rgb(28 28 30/.3) 100%)}
@media(max-width:60rem){.backdrop::after{background:rgb(28 28 30/.84)}}
@media(forced-colors:active),print{.backdrop{display:none}}
.eyebrow{font-size:13px;letter-spacing:.2em;text-transform:uppercase;font-weight:600;
color:var(--flare);margin:0 0 12px}
.hero h1{font-size:clamp(44px,10vw,96px);color:#fff;max-width:11ch}
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
.sec h2,.about h2,.close h2,.gal h2{font-size:clamp(30px,7.2vw,56px);margin-bottom:12px}
.lede{color:var(--muted);max-width:58ch;margin:0 0 26px;font-size:16px}
.gridnum{display:grid;gap:0;border-top:3px solid var(--ink)}
.gn{padding:20px 0;border-bottom:1px solid var(--rule);display:grid;
grid-template-columns:46px minmax(0,1fr);gap:12px;align-items:start}
.gn .num{font-size:34px;color:var(--accent);line-height:.85}
.gn h3{font-size:23px;margin-bottom:6px}
.gn p{color:var(--muted);font-size:16px}
/* About: dark, the client's own photograph beside the three points. */
.about{background:var(--dark);color:var(--ondark);padding:44px 0 48px}
.about h2{color:#fff;max-width:18ch}
.about .kicker{color:var(--flare)}
.about .lede{color:var(--dim)}
.aboutgrid{display:grid;gap:26px}
.aboutrow{display:grid;gap:16px}
.aboutrow div{border-left:3px solid var(--flare);padding:2px 0 2px 14px}
.aboutrow strong{font-family:"Barlow Condensed",Impact,sans-serif;text-transform:uppercase;
font-size:21px;font-weight:700;display:block;color:#fff;line-height:1.1;margin-bottom:5px}
.aboutrow p{color:var(--dim);font-size:16px}
.aboutpic{margin:0;overflow:hidden;background:var(--board)}
.aboutpic picture,.aboutpic img{display:block;width:100%;height:auto}
.aboutpic img{aspect-ratio:4/3;object-fit:cover}
.aboutpic figcaption{font-size:12px;letter-spacing:.14em;text-transform:uppercase;font-weight:600;
color:var(--dim);padding:10px 0 0}
/* Gallery: the client's photographs, three across. */
.gal{background:var(--surface);padding:46px 0}
.gal .note{color:var(--muted);margin:12px 0 28px;max-width:58ch;font-size:16px}
.galgrid{display:grid;grid-template-columns:1fr;gap:3px}
.gal figure{margin:0;position:relative;overflow:hidden;background:var(--rule)}
.gal picture{display:block}
.gal img{display:block;width:100%;height:auto;aspect-ratio:4/3;object-fit:cover;transition:transform .5s ease}
.gal figure:hover img{transform:scale(1.035)}
.gal figcaption{position:absolute;left:0;bottom:0;background:var(--dark);color:var(--surface);
font-size:12px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;padding:7px 12px}
.gal .more{margin-top:18px;font-size:15px;color:var(--muted)}
.gal .more a{color:var(--accent);font-weight:600;text-decoration:none}
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
.revlink{margin-top:22px;font-size:15px;color:var(--muted)}
.revlink a{color:var(--accent);font-weight:600;text-decoration:none}
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
/* Estimate form. */
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
.close .backdrop::after{background:linear-gradient(100deg,rgb(28 28 30/.92) 0%,rgb(28 28 30/.8) 45%,rgb(28 28 30/.45) 100%)}
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
.sec,.gal,.quote{padding:76px 0}.hero{padding:60px 0 0}.about{padding:70px 0 74px}
.hero .sub{font-size:19px}.btn{min-height:70px}.btn b{font-size:32px}}
@media(min-width:900px){.aboutgrid{grid-template-columns:minmax(0,1.15fr) minmax(0,1fr);align-items:center;gap:44px}
.aboutrow{gap:20px}.quotegrid{grid-template-columns:minmax(0,1.3fr) minmax(0,1fr);gap:56px}}
@media(min-width:1000px){body{padding-bottom:0}.callbar{display:none}.navlinks{display:flex}
.navact{margin-left:24px}.hero{padding:88px 0 0}.hero .boards{margin-top:64px}}
/* Motion: gated on .m, which only the script adds, so nothing hides without JS. */
.m [data-reveal]{opacity:0;transform:translateY(14px);transition:opacity .7s cubic-bezier(.2,.6,.2,1),transform .7s cubic-bezier(.2,.6,.2,1)}
.m [data-reveal].in{opacity:1;transform:none}
.m .gal figure[data-reveal]:nth-child(3n+2){transition-delay:.08s}
.m .gal figure[data-reveal]:nth-child(3n){transition-delay:.16s}
@keyframes hero-in{from{opacity:0;transform:scale(1.025)}to{opacity:1;transform:none}}
.m .hero .backdrop img{animation:hero-in 1s ease-out both}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}
.m [data-reveal]{opacity:1;transform:none;transition:none}.m .hero .backdrop img{animation:none}
.gal img{transition:none}.gal figure:hover img{transform:none}}
</style>
</head>
<body>
<div class="topbar"><div class="wrap"><span>Licensed, bonded &amp; insured · L&amp;I #$lni</span><span><a href="$google" rel="noopener">Review us on Google</a> · <a href="$facebook" rel="noopener">Facebook</a></span></div></div>
<header class="nav"><div class="wrap">
  <a class="brand" href="#top"><span class="lockup">$mark<span>$name</span></span></a>
  <nav class="navlinks"><a href="#services">Fences</a><a href="#about">About</a><a href="#work">Our work</a><a href="#process">Process</a><a href="#faq">Questions</a><a href="#quote">Estimate</a></nav>
  <a class="navact" href="tel:$tel">$phone</a>
</div></header>
<section class="hero" id="top">
  <div class="backdrop" aria-hidden="true">$hero_pic</div>
  <div class="wrap">
    <p class="eyebrow">$tagline · Snohomish, WA</p>
    <h1>$headline</h1>
    <p class="sub">$name has built fences across $area_long for over $years years. Cedar and wood, chain link and ornamental iron, the gates and operators to match, repairs, and material packages if you would rather build it yourself. Free onsite estimates.</p>
    <div class="ctas">
      <a class="btn btn-primary" href="tel:$tel">Call or text <b>$phone</b></a>
      <a class="btn btn-ghost" href="#quote">Get a free estimate</a>
    </div>
    <ul class="badges">
      <li>Free onsite estimates</li><li>$years+ years in fence construction</li>
      <li>Licensed, bonded and insured</li><li>Senior and veteran discounts</li>
    </ul>
  </div>
  <div class="boards" aria-hidden="true"></div>
</section>
<section class="strip"><div class="wrap">
  <p class="big">Free onsite estimate.</p>
  <p class="small">Senior discount, veterans discount, and a discount for saying you saw us on the website.</p>
</div></section>
<section class="sec" id="services"><div class="wrap">
  <p class="kicker">Fences &amp; gates</p>
  <h2>What we build</h2>
  <p class="lede">Residential and commercial, in cedar, chain link and ornamental iron. If you do not see yours, call anyway. There are ten-plus styles and we have probably built it.</p>
  <div class="gridnum">
$services
  </div>
</div></section>
<section class="about" id="about"><div class="wrap">
  <p class="kicker">About us</p>
  <h2>Forty-five years of fences</h2>
  <p class="lede">$name has over $years years of expertise in fence construction, with crews who have spent thirty of them building fences the right way. We value each customer's home and privacy, and attention to detail is what we strive for.</p>
  <div class="aboutgrid">
    <div class="aboutrow">
$about
    </div>
    <figure class="aboutpic">$about_pic<figcaption>Every board hand-picked, and finished by hand</figcaption></figure>
  </div>
</div></section>
<section class="gal" id="work"><div class="wrap">
  <p class="kicker">Our work</p>
  <h2>Take a closer look</h2>
  <p class="note">Cedar, High Five, chain link and ornamental iron, on flat lots, slopes and acreage across $area_long. All of it ours.</p>
  <div class="galgrid">
$tiles
  </div>
  <p class="more">More on <a href="$facebook" rel="noopener">Facebook</a>.</p>
</div></section>
<section class="sec alt" id="process"><div class="wrap">
  <p class="kicker">Process</p>
  <h2>How a job actually runs</h2>
  <p class="lede">The part most fence companies leave vague, which is the part you are wondering about while the old fence is still leaning.</p>
  <ol class="steps">
$steps
  </ol>
</div></section>
<section class="sec" id="reviews"><div class="wrap">
  <p class="kicker">Reviews</p>
  <h2>What customers say</h2>
  <div class="reviews">
$reviews
  </div>
  <p class="revlink">Read more, or leave one: <a href="$google" rel="noopener">$name on Google</a>.</p>
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
  <h2>Snohomish County and beyond</h2>
  <p class="lede">Based in $town. If you are a little outside the towns below, call anyway.</p>
  <ul class="towns">
$towns
  </ul>
</div></section>
<section class="quote" id="quote"><div class="wrap">
  <p class="kicker">Free estimate</p>
  <h2>Tell us about the fence</h2>
  <p class="lede">Rough numbers are fine. We will get back to you to set up the onsite estimate.</p>
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
          <option>Cedar or wood</option><option>Galvanized chain link</option><option>Black or colored chain link</option>
          <option>Ornamental iron</option><option>Gate or gate operator</option><option>Repair</option>
          <option>DIY material package</option><option>Not sure yet</option>
        </select></label>
        <label>Approx. length (feet)<input name="length" inputmode="numeric" placeholder="e.g. 180"></label>
      </div>
      <label>Anything else<textarea name="notes" placeholder="Gates, height, a slope, a fence that is already down, dogs..."></textarea></label>
      <button class="btn btn-primary" type="submit">Send the details</button>
      <p class="status" role="status" aria-live="polite"></p>
      <p class="fine">Or just call or text <a href="tel:$tel">$phone</a>. No pressure either way.</p>
    </form>
    <div class="contactcard">
      <div><strong>Call or text</strong><a href="tel:$tel">$phone</a></div>
      <div><strong>Email</strong><a href="mailto:$email">$email</a></div>
      <div><strong>Hours</strong>$hours</div>
      <div><strong>Address</strong>$street<br>$town $zip</div>
      <div><strong>Registered contractor</strong>WA L&amp;I #$lni · Bonded &amp; insured</div>
      <div><strong>Payment</strong>Cash, Visa, MasterCard</div>
    </div>
  </div>
</div></section>
<section class="close" id="contact">
  <div class="backdrop" aria-hidden="true">$close_pic</div>
  <div class="wrap">
    <h2>Bring the family back to the back yard.</h2>
    <p>Beautiful construction and a safe environment for your home or business. Let us help you secure your property and bring value to it. Call or message for a free onsite estimate.</p>
    <div class="ctas">
      <a class="btn btn-primary" href="tel:$tel">Call or text <b>$phone</b></a>
      <a class="btn btn-ghost" href="#quote">Get a free estimate</a>
    </div>
  </div>
</section>
<footer class="foot">
  <div class="boards" aria-hidden="true" style="margin:0"></div>
  <div class="wrap">
  <a class="brand" href="#top"><span class="lockup">$mark<span>$name</span></span></a>
  <p><a href="tel:$tel">$phone</a> · <a href="mailto:$email">$email</a></p>
  <p>$legal · $street, $town $zip · $hours</p>
  <p>WA L&amp;I registered contractor #$lni · Licensed, bonded and insured · <a href="$facebook" rel="noopener">Facebook</a> · <a href="$google" rel="noopener">Google</a></p>
  <p class="fine">Site by <a href="https://grandstreetworks.com">Grand Street Works</a>.</p>
</div></footer>
<div class="callbar"><a class="tel" href="tel:$tel">Call $phone</a><a class="alt2" href="#quote">Free estimate</a></div>
<script>
(function () {
  /* Estimate form. With an endpoint configured it posts JSON; without one it
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
        + '?subject=' + encodeURIComponent('Fence estimate request from ' + (data.name || 'the website'))
        + '&body=' + encodeURIComponent(body);
      status.textContent = 'Opening your mail app. If nothing happens, call or text us instead.';
      return;
    }
    ev.preventDefault();
    status.textContent = 'Sending...';
    fetch(ENDPOINT, { method: 'POST', headers: { 'Content-Type': 'application/json' },
                      body: JSON.stringify(data) })
      .then(function (r) { if (!r.ok) throw new Error(r.status); form.reset();
                           status.textContent = 'Got it. We will be in touch to set up the estimate.'; })
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


def build_page() -> None:
    c = CONFIG
    tel = re.sub(r"\D", "", c["phone"])
    tel = ("+1" + tel) if len(tel) == 10 else "+" + tel
    description = (f"Fence installation in {c['area_long']}. Cedar and wood, chain link, "
                   f"ornamental iron, gates and operators, repairs and DIY material packages. "
                   f"Over {c['years']} years of experience. Free onsite estimates. "
                   f"WA L&I #{c['lni']}, bonded and insured.")
    mark = mark_svg(PALETTE["accent"], PALETTE["white"], PALETTE["ink"])

    services = "\n".join(
        f'    <article class="gn"><div class="num">{i:02d}</div><div><h3>{t}</h3><p>{p}</p></div></article>'
        for i, (t, p) in enumerate(SERVICES, 1))
    about = "\n".join(
        f'      <div><strong>{html.escape(t)}</strong><p>{html.escape(p)}</p></div>' for t, p in ABOUT)
    steps = "\n".join(
        f'    <li><div><h3>{html.escape(t)}</h3><p>{html.escape(p)}</p></div></li>' for t, p in STEPS)
    reviews = "\n".join(
        f'    <article class="rev"><div class="stars" aria-label="Five stars">★★★★★</div>'
        f'<blockquote>{html.escape(q)}</blockquote><footer>{html.escape(n)} · {w}</footer></article>'
        for q, n, w in REVIEWS)
    faq = "\n".join(
        f'    <details><summary>{html.escape(q)}</summary><p>{html.escape(a)}</p></details>'
        for q, a in FAQ)
    towns = "\n".join(f'    <li>{html.escape(t)}</li>' for t in c["towns"])
    tiles = "\n".join(
        f'    <figure>{picture(n, cap, "(max-width: 700px) 100vw, 33vw")}'
        f'<figcaption>{html.escape(cap)}</figcaption></figure>' for n, cap in TILES)

    page = PAGE.substitute(
        name=html.escape(c["name"]), legal=html.escape(c["legal"]),
        tagline=TAGLINE, headline=HEADLINE, description=html.escape(description),
        phone=html.escape(c["phone"]), tel=tel, email=html.escape(c["email"]),
        street=html.escape(c["street"]), town=html.escape(c["town"]), zip=c["zip"],
        town_placeholder=html.escape(c["town"].split(",")[0]),
        area_long=html.escape(c["area_long"]), years=c["years"],
        lni=html.escape(c["lni"]), hours=html.escape(c["hours"]),
        facebook=html.escape(c["facebook"]), google=html.escape(c["google"]),
        url=c["url"], dark=PALETTE["dark"], jsonld=jsonld(), mark=mark,
        hero_pic=picture("hero", "", "100vw", eager=True),
        close_pic=picture("farmhouse", "", "100vw"),
        about_pic=picture("staining", "Brushing finish onto new cedar fence boards by hand", "(max-width: 900px) 100vw, 45vw"),
        services=services, about=about, steps=steps, reviews=reviews, faq=faq,
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
