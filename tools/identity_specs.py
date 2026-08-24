#!/usr/bin/env python3
"""Per-build identity specs for the finish pass.

Every build in a trade set is a different invented business, and the whole point
of shipping six is that they read as six firms rather than one design recoloured.
Until now the only thing carrying that was the typeface: the "logo" was the
company name set in the display face, and there was no favicon, no social card
and no mark anywhere in the set.

Each mark below is drawn from the device that build's own stylesheet header
already names — the shingle course band, the chevron rule, the sawtooth ridge,
the hazard chevron, the docket shield, the dispatch band. Nothing here invents
a new visual language; it gives the one already on the page something to sign.

Marks are authored at 64x64 so they survive being rasterised to a 16px favicon.
"""

# --- the marks -------------------------------------------------------------
# Each is the *inner* markup of a 0 0 64 64 SVG. Colours are literal rather than
# currentColor: these get rasterised into favicons and social cards where no
# stylesheet is in scope.

MARK_HALLORAN = """\
<defs><clipPath id="c"><path d="M6 55 L19 11 L45 11 L58 55 Z"/></clipPath></defs>
<g clip-path="url(#c)" fill="{accent}">
<rect x="-10" y="11" width="12.5" height="13"/><rect x="5" y="11" width="12.5" height="13"/>
<rect x="20" y="11" width="12.5" height="13"/><rect x="35" y="11" width="12.5" height="13"/>
<rect x="50" y="11" width="12.5" height="13"/>
<rect x="-2.5" y="26.5" width="12.5" height="13" opacity=".86"/><rect x="12.5" y="26.5" width="12.5" height="13" opacity=".86"/>
<rect x="27.5" y="26.5" width="12.5" height="13" opacity=".86"/><rect x="42.5" y="26.5" width="12.5" height="13" opacity=".86"/>
<rect x="57.5" y="26.5" width="12.5" height="13" opacity=".86"/>
<rect x="-10" y="42" width="12.5" height="14" opacity=".72"/><rect x="5" y="42" width="12.5" height="14" opacity=".72"/>
<rect x="20" y="42" width="12.5" height="14" opacity=".72"/><rect x="35" y="42" width="12.5" height="14" opacity=".72"/>
<rect x="50" y="42" width="12.5" height="14" opacity=".72"/>
</g>"""

MARK_FAIR_OAKS = """\
<g fill="none" stroke="{accent}" stroke-width="9" stroke-linecap="butt" stroke-linejoin="miter">
<path d="M2 44 L18 20 L34 44 L50 20 L62 38"/>
</g>"""

MARK_MERIDIAN = """\
<rect x="6" y="26" width="52" height="32" fill="{slate}"/>
<path d="M6 26 L19 8 L32 26 L45 8 L58 26 Z" fill="{accent}"/>"""

MARK_ANCHOR_PEAK = """\
<rect x="4" y="4" width="56" height="56" rx="2" fill="{ink}"/>
<g fill="none" stroke="{accent}" stroke-width="9" stroke-linecap="square" stroke-linejoin="miter">
<path d="M13 33 L32 16 L51 33"/><path d="M13 50 L32 33 L51 50"/>
</g>"""

MARK_SENTRY = """\
<path d="M32 5 L57 14 V33 C57 46 46 55 32 59 C18 55 7 46 7 33 V14 Z" fill="{accent}"/>
<g fill="{surface}">
<rect x="14" y="28" width="11" height="10"/><rect x="26.5" y="28" width="11" height="10"/>
<rect x="39" y="28" width="11" height="10"/>
</g>"""

MARK_NORTHGATE = """\
<rect x="4" y="4" width="56" height="56" fill="{band}"/>
<rect x="11" y="15" width="30" height="6" fill="{accent}" opacity=".55"/>
<rect x="11" y="26" width="42" height="14" fill="{accent}"/>
<rect x="11" y="45" width="36" height="6" fill="{accent}" opacity=".55"/>"""


# --- the builds ------------------------------------------------------------
# `mark_fill` names which palette entry the mark's own colours come from, so the
# social card and the favicon can pick a ground that the mark reads against.

BUILDS = {
    "roofing": {
        "trade_label": "Roofing contractor",
        "schema_type": "RoofingContractor",
        "builds": {
            "halloran-roofing": {
                "name": "Halloran Roofing",
                "device": "shingle course band",
                "mark": MARK_HALLORAN,
                "palette": {"ink": "#141517", "surface": "#F7F5F2", "accent": "#A8380A",
                            "slate": "#3A3F45", "band": "#141517"},
                "card_bg": "#141517", "card_fg": "#EDEAE6", "card_accent": "#FF9E6B",
                "display_font": "Saira Condensed", "display_css": "Saira+Condensed:wght@600;700",
                "display_weight": 700, "uppercase": True,
                "headline": "Tarped tonight. Replaced this week.",
                "phone": "(970) 208-4417",
                "tagline": "Storm damage, replacements and repairs across the metro",
            },
            "fair-oaks-roofing": {
                "name": "Fair Oaks Roofing",
                "device": "chevron rule",
                "mark": MARK_FAIR_OAKS,
                "palette": {"ink": "#1B1D20", "surface": "#FAF9F7", "accent": "#2F4858",
                            "slate": "#2F4858", "band": "#EDEBE6"},
                "card_bg": "#2F4858", "card_fg": "#FAF9F7", "card_accent": "#FAF9F7",
                "card_mark": "#FAF9F7",
                "display_font": "Fjalla One", "display_css": "Fjalla+One",
                "display_weight": 400, "uppercase": False,
                "headline": "Ask the four houses on your street we did this year.",
                "phone": "(217) 331-9075",
                "tagline": "Licensed & insured, serving the metro area since 2004",
            },
            "meridian-roof-co": {
                "name": "Meridian Roof Co.",
                "device": "sawtooth ridge",
                "mark": MARK_MERIDIAN,
                "palette": {"ink": "#16181A", "surface": "#F1F2F3", "accent": "#9A3412",
                            "slate": "#2B3238", "band": "#2B3238"},
                "card_bg": "#16181A", "card_fg": "#E9EAEB", "card_accent": "#FF8C4A",
                "display_font": "Antonio", "display_css": "Antonio:wght@500;700",
                "display_weight": 700, "uppercase": True,
                "headline": "Two thousand four hundred roofs. Six crews.",
                "phone": "(463) 645-2130",
                "tagline": "2,400+ roofs completed, 24hr emergency response",
            },
            "anchor-peak-roofing": {
                "name": "Anchor Peak Roofing",
                "device": "hazard chevron",
                "mark": MARK_ANCHOR_PEAK,
                "palette": {"ink": "#17181A", "surface": "#F4F3F0", "accent": "#F5B301",
                            "slate": "#17181A", "band": "#17181A"},
                "card_bg": "#17181A", "card_fg": "#F4F3F0", "card_accent": "#F5B301",
                "display_font": "Bebas Neue", "display_css": "Bebas+Neue",
                "display_weight": 400, "uppercase": True,
                "headline": "Emergency response 24/7. Same-day tarping.",
                "phone": "(210) 872-6604",
                "tagline": "Emergency response 24/7, same-day tarping",
            },
            "sentry-roofing-and-restoration": {
                "name": "Sentry Roofing & Restoration",
                "device": "docket shield",
                "mark": MARK_SENTRY,
                "palette": {"ink": "#1A1D20", "surface": "#E9EBEC", "accent": "#4C5A63",
                            "slate": "#4C5A63", "band": "#E9EBEC"},
                "card_bg": "#1A1D20", "card_fg": "#E9EBEC", "card_accent": "#9FB0BA",
                "display_font": "Big Shoulders Display", "display_css": "Big+Shoulders+Display:wght@600;800",
                "display_weight": 800, "uppercase": True,
                "headline": "We meet your adjuster on the roof.",
                "phone": "(620) 490-7728",
                "tagline": "We meet your adjuster and handle the claim paperwork",
            },
            "northgate-roofing": {
                "name": "Northgate Roofing",
                "device": "dispatch band",
                "mark": MARK_NORTHGATE,
                "palette": {"ink": "#E8EAEB", "surface": "#17191B", "accent": "#FFC53D",
                            "slate": "#0F1113", "band": "#0F1113"},
                "card_bg": "#0F1113", "card_fg": "#E8EAEB", "card_accent": "#FFC53D",
                "display_font": "Teko", "display_css": "Teko:wght@500;600;700",
                "display_weight": 700, "uppercase": True,
                "headline": "Call during the storm. Someone answers.",
                "phone": "(570) 676-3382",
                "tagline": "Call and a human answers, day or night",
            },
        },
    },
}


def mark_svg(spec: dict, size: int | None = None, background: str | None = None) -> str:
    """Standalone SVG for a build's mark, optionally on a solid ground.

    Fair Oaks' accent *is* its card ground, so a mark drawn in the page palette
    would vanish on its own social card. `card_mark` overrides the accent for
    exactly that case; builds that read fine on their ground omit it.
    """
    palette = dict(spec["palette"])
    if background and spec.get("card_mark"):
        palette["accent"] = spec["card_mark"]
    inner = spec["mark"].format(**palette)
    dims = f' width="{size}" height="{size}"' if size else ""
    ground = f'<rect width="64" height="64" fill="{background}"/>' if background else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"{dims} '
            f'role="img" aria-label="{spec["name"]}">{ground}{inner}</svg>')
