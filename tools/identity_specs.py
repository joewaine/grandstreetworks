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
    # From here on, only the mark and its device are hand-written; see derive().
    # Marks use {accent}, {fg} and {bg}; fg/bg are the page's text and ground on
    # the page, and the card's pair on a card.
    "hvac": {
        "trade_label": "Heating & air",
        "schema_type": "HVACBusiness",
        "builds": {
            "ironwood-heating-and-air": {
                "device": "dispatch strip",
                "mark": """\
<rect x="6" y="12" width="52" height="11" fill="{accent}"/>
<rect x="6" y="27" width="36" height="11" fill="{fg}" opacity=".72"/>
<rect x="6" y="42" width="20" height="11" fill="{fg}" opacity=".42"/>"""},
            "sutter-heating-and-cooling": {
                "device": "thermostat dial",
                "mark": """\
<circle cx="32" cy="32" r="22" fill="none" stroke="{accent}" stroke-width="7"/>
<path d="M32 32 L44 17" stroke="{fg}" stroke-width="6" stroke-linecap="round"/>
<circle cx="32" cy="32" r="4" fill="{fg}"/>"""},
            "vantage-air-systems": {
                "device": "hot and cold seam",
                "mark": """\
<path d="M6 8 H37 L27 56 H6 Z" fill="{accent}"/>
<path d="M43 8 H58 V56 H33 Z" fill="{fg}" opacity=".78"/>"""},
            "nightingale-heating-and-air": {
                "device": "night call glow",
                "mark": """\
<circle cx="32" cy="25" r="15" fill="{accent}"/>
<rect x="10" y="46" width="44" height="8" rx="4" fill="{fg}" opacity=".7"/>"""},
            "beacon-comfort-co": {
                "device": "plan panel with thermal edge",
                "mark": """\
<rect x="11" y="8" width="42" height="48" rx="3" fill="none" stroke="{fg}" stroke-width="5"/>
<rect x="11" y="8" width="10" height="48" rx="2" fill="{accent}"/>"""},
            "trueline-heating-and-air": {
                "device": "gauge sweep",
                "mark": """\
<path d="M10 46 A24 24 0 0 1 54 46" fill="none" stroke="{accent}" stroke-width="8" stroke-linecap="round"/>
<path d="M32 48 L41 27" stroke="{fg}" stroke-width="6" stroke-linecap="round"/>
<circle cx="32" cy="48" r="4.5" fill="{fg}"/>"""},
        },
    },
    "restoration": {
        "trade_label": "Restoration",
        "schema_type": "HomeAndConstructionBusiness",
        "builds": {
            "arbor-restoration-group": {
                "device": "referral card",
                "mark": """\
<rect x="8" y="12" width="48" height="40" rx="3" fill="none" stroke="{fg}" stroke-width="5"/>
<circle cx="20" cy="24" r="5.5" fill="{accent}"/>"""},
            "bluewater-restoration": {
                "device": "ticked rule",
                "mark": """\
<path d="M8 44 H56" stroke="{fg}" stroke-width="5" opacity=".7"/>
<path d="M18 28 L27 37 L46 14" fill="none" stroke="{accent}" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>"""},
            "claymore-restoration": {
                "device": "moisture readings",
                "mark": """\
<rect x="10" y="36" width="9" height="18" fill="{fg}" opacity=".5"/>
<rect x="23" y="26" width="9" height="28" fill="{fg}" opacity=".75"/>
<rect x="36" y="14" width="9" height="40" fill="{accent}"/>
<rect x="49" y="30" width="7" height="24" fill="{fg}" opacity=".35"/>"""},
            "keystone-restoration": {
                "device": "segmented dispatch meter",
                "mark": """\
<rect x="6" y="25" width="11" height="14" fill="{accent}"/>
<rect x="20" y="25" width="11" height="14" fill="{accent}"/>
<rect x="34" y="25" width="11" height="14" fill="{accent}" opacity=".55"/>
<rect x="48" y="25" width="10" height="14" fill="{fg}" opacity=".3"/>"""},
            "nightwatch-restoration": {
                "device": "night line",
                "mark": """\
<circle cx="30" cy="32" r="18" fill="{accent}"/>
<circle cx="38" cy="27" r="15" fill="{bg}"/>"""},
            "rapid-dry-restoration": {
                "device": "minute dial",
                "mark": """\
<circle cx="32" cy="32" r="23" fill="none" stroke="{fg}" stroke-width="5" opacity=".6"/>
<path d="M32 32 L32 9 A23 23 0 0 1 55 32 Z" fill="{accent}"/>"""},
        },
    },
    "pool-builders": {
        "trade_label": "Pool builder",
        "schema_type": "HomeAndConstructionBusiness",
        "builds": {
            "anvil-bay-pools": {
                "device": "deep end profile",
                "mark": """\
<path d="M6 14 H58 V30 L42 52 H6 Z" fill="{accent}"/>
<rect x="6" y="14" width="52" height="5" fill="{fg}"/>"""},
            "blue-harbor-pools": {
                "device": "raked water line",
                "mark": """\
<path d="M6 22q8-8 16 0t16 0 16 0" fill="none" stroke="{accent}" stroke-width="5" stroke-linecap="round"/>
<path d="M6 36q8-8 16 0t16 0 16 0" fill="none" stroke="{fg}" stroke-width="5" stroke-linecap="round" opacity=".6"/>
<path d="M6 50q8-8 16 0t16 0 16 0" fill="none" stroke="{fg}" stroke-width="5" stroke-linecap="round" opacity=".35"/>"""},
            "clearwater-pool-group": {
                "device": "monthly figure",
                "mark": """\
<circle cx="32" cy="32" r="24" fill="{accent}"/>
<rect x="20" y="29" width="24" height="6" fill="{bg}"/>"""},
            "cold-spring-pools": {
                "device": "spring marker on the year",
                "mark": """\
<circle cx="32" cy="32" r="21" fill="none" stroke="{fg}" stroke-width="6" opacity=".55"/>
<circle cx="32" cy="11" r="7.5" fill="{accent}"/>"""},
            "marlin-pool-co": {
                "device": "render with corner ticks",
                "mark": """\
<path d="M16 20 H48 L58 46 H6 Z" fill="{accent}"/>
<path d="M6 8 H14 M6 8 V16 M58 8 H50 M58 8 V16" fill="none" stroke="{fg}" stroke-width="4"/>"""},
            "verdant-pools-and-gardens": {
                "device": "pool drawn into the garden plan",
                "mark": """\
<rect x="6" y="6" width="52" height="52" rx="6" fill="none" stroke="{fg}" stroke-width="5" opacity=".7"/>
<rect x="18" y="22" width="28" height="20" rx="3" fill="{accent}"/>"""},
        },
    },
    "solar": {
        "trade_label": "Solar installer",
        "schema_type": "HomeAndConstructionBusiness",
        "builds": {
            "ansonia-solar": {
                "device": "open figure slot",
                "mark": """\
<path d="M12 12 H6 V52 H12 M52 12 H58 V52 H52" fill="none" stroke="{fg}" stroke-width="5"/>
<rect x="22" y="27" width="20" height="10" fill="{accent}"/>"""},
            "brightfold-solar": {
                "device": "incentive sheet",
                "mark": """\
<rect x="14" y="6" width="36" height="52" rx="2" fill="{accent}"/>
<rect x="21" y="18" width="22" height="5" fill="{bg}"/>
<rect x="21" y="29" width="22" height="5" fill="{bg}"/>
<rect x="21" y="40" width="14" height="5" fill="{bg}"/>"""},
            "cedar-line-solar": {
                "device": "three open figure slots",
                "mark": """\
<rect x="6" y="22" width="15" height="20" fill="{accent}"/>
<rect x="24.5" y="22" width="15" height="20" fill="{accent}" opacity=".7"/>
<rect x="43" y="22" width="15" height="20" fill="{accent}" opacity=".45"/>"""},
            "fairhaven-solar": {
                "device": "number above the button",
                "mark": """\
<rect x="10" y="8" width="44" height="30" fill="{accent}"/>
<rect x="10" y="46" width="28" height="8" fill="{fg}" opacity=".7"/>"""},
            "halgrove-energy": {
                "device": "unread meter",
                "mark": """\
<rect x="6" y="18" width="52" height="28" rx="3" fill="none" stroke="{fg}" stroke-width="5"/>
<rect x="14" y="27" width="20" height="10" fill="{accent}"/>"""},
            "kettle-ridge-solar": {
                "device": "panel grid",
                "mark": """\
<rect x="8" y="8" width="22" height="22" fill="{accent}"/>
<rect x="34" y="8" width="22" height="22" fill="{accent}"/>
<rect x="8" y="34" width="22" height="22" fill="{accent}"/>
<rect x="34" y="34" width="22" height="22" fill="{fg}" opacity=".5"/>"""},
        },
    },
    "general-contractors": {
        "trade_label": "General contractor",
        "schema_type": "GeneralContractor",
        "builds": {
            "bexley-build-group": {
                "device": "stages under a continuous rule",
                "mark": """\
<rect x="6" y="30" width="52" height="5" fill="{fg}" opacity=".6"/>
<rect x="10" y="18" width="8" height="28" fill="{accent}"/>
<rect x="28" y="18" width="8" height="28" fill="{accent}" opacity=".7"/>
<rect x="46" y="18" width="8" height="28" fill="{accent}" opacity=".45"/>"""},
            "granby-construction": {
                "device": "licence plate",
                "mark": """\
<rect x="6" y="16" width="52" height="32" rx="4" fill="{accent}"/>
<circle cx="14" cy="24" r="3" fill="{bg}"/><circle cx="50" cy="24" r="3" fill="{bg}"/>
<rect x="16" y="33" width="32" height="6" fill="{bg}"/>"""},
            "halverson-build-co": {
                "device": "dated site diary",
                "mark": """\
<rect x="8" y="12" width="48" height="44" rx="3" fill="none" stroke="{fg}" stroke-width="5"/>
<rect x="8" y="12" width="48" height="12" fill="{accent}"/>
<circle cx="32" cy="40" r="6" fill="{accent}"/>"""},
            "marrant-construction": {
                "device": "ruled ledger rows",
                "mark": """\
<rect x="8" y="14" width="48" height="4" fill="{fg}" opacity=".55"/>
<rect x="8" y="30" width="48" height="4" fill="{fg}" opacity=".55"/>
<rect x="8" y="46" width="48" height="4" fill="{fg}" opacity=".55"/>
<rect x="40" y="36" width="16" height="10" fill="{accent}"/>"""},
            "threshold-builders": {
                "device": "threshold panel",
                "mark": """\
<rect x="10" y="8" width="44" height="48" fill="none" stroke="{fg}" stroke-width="5"/>
<rect x="10" y="48" width="44" height="8" fill="{accent}"/>"""},
            "whitfield-build-co": {
                "device": "schedule bars",
                "mark": """\
<rect x="6" y="12" width="24" height="9" fill="{accent}"/>
<rect x="18" y="27" width="28" height="9" fill="{accent}" opacity=".75"/>
<rect x="32" y="42" width="26" height="9" fill="{accent}" opacity=".5"/>"""},
        },
    },
    "custom-home-builders": {
        "trade_label": "Custom home builder",
        "schema_type": "HomeAndConstructionBusiness",
        "builds": {
            "coulter-and-vane-homes": {
                "device": "site contours",
                "mark": """\
<rect x="26" y="12" width="12" height="12" fill="{accent}"/>
<path d="M6 44 Q20 30 32 38 T58 30" fill="none" stroke="{fg}" stroke-width="5" opacity=".6"/>
<path d="M6 56 Q22 42 34 50 T58 42" fill="none" stroke="{accent}" stroke-width="6"/>"""},
            "farrow-ridge-builders": {
                "device": "two entrances, one lintel",
                "mark": """\
<rect x="8" y="8" width="48" height="5" fill="{fg}"/>
<rect x="8" y="16" width="20" height="40" fill="{accent}"/>
<rect x="36" y="16" width="20" height="40" fill="{fg}" opacity=".7"/>"""},
            "kingsmere-build": {
                "device": "filmstrip",
                "mark": """\
<rect x="6" y="18" width="52" height="28" fill="{accent}"/>
<rect x="10" y="22" width="12" height="20" fill="{bg}"/>
<rect x="26" y="22" width="12" height="20" fill="{bg}"/>
<rect x="42" y="22" width="12" height="20" fill="{bg}"/>"""},
            "latham-homes": {
                "device": "the number over the ledger",
                "mark": """\
<rect x="8" y="10" width="48" height="18" fill="{accent}"/>
<rect x="8" y="36" width="48" height="4" fill="{fg}" opacity=".55"/>
<rect x="8" y="48" width="32" height="4" fill="{fg}" opacity=".55"/>"""},
            "sable-creek-homes": {
                "device": "bordered panel, four builds",
                "mark": """\
<rect x="8" y="8" width="48" height="48" fill="none" stroke="{fg}" stroke-width="4"/>
<circle cx="24" cy="24" r="5" fill="{accent}"/><circle cx="40" cy="24" r="5" fill="{accent}"/>
<circle cx="24" cy="40" r="5" fill="{accent}"/><circle cx="40" cy="40" r="5" fill="{fg}" opacity=".4"/>"""},
            "wyndham-custom-homes": {
                "device": "eighteen-month ladder",
                "mark": """\
<rect x="16" y="6" width="6" height="52" fill="{fg}" opacity=".7"/>
<rect x="42" y="6" width="6" height="52" fill="{fg}" opacity=".7"/>
<rect x="16" y="14" width="32" height="5" fill="{accent}"/><rect x="16" y="26" width="32" height="5" fill="{accent}"/>
<rect x="16" y="38" width="32" height="5" fill="{accent}"/><rect x="16" y="50" width="32" height="5" fill="{accent}"/>"""},
        },
    },
    "interior-design": {
        "trade_label": "Interior design",
        "schema_type": "ProfessionalService",
        "builds": {
            "bramble-and-stone": {
                "device": "mounted sample card",
                "mark": """\
<rect x="10" y="14" width="44" height="40" rx="2" fill="{accent}"/>
<rect x="10" y="8" width="18" height="10" fill="{fg}" opacity=".8"/>"""},
            "fairholme-design-co": {
                "device": "specification ledger",
                "mark": """\
<rect x="8" y="12" width="10" height="10" fill="{accent}"/><rect x="24" y="14" width="32" height="6" fill="{fg}" opacity=".6"/>
<rect x="8" y="27" width="10" height="10" fill="{accent}" opacity=".7"/><rect x="24" y="29" width="26" height="6" fill="{fg}" opacity=".6"/>
<rect x="8" y="42" width="10" height="10" fill="{accent}" opacity=".45"/><rect x="24" y="44" width="30" height="6" fill="{fg}" opacity=".6"/>"""},
            "ivory-lane-interiors": {
                "device": "filter chips, one lit",
                "mark": """\
<rect x="6" y="16" width="24" height="12" rx="6" fill="{accent}"/>
<rect x="34" y="16" width="24" height="12" rx="6" fill="{fg}" opacity=".35"/>
<rect x="6" y="36" width="34" height="12" rx="6" fill="{fg}" opacity=".35"/>"""},
            "nocturne-interiors": {
                "device": "pool of lamplight",
                "mark": """\
<rect x="29" y="8" width="6" height="18" fill="{fg}" opacity=".7"/>
<circle cx="32" cy="42" r="16" fill="{accent}"/>"""},
            "sorrel-studio": {
                "device": "terrazzo field",
                "mark": """\
<rect x="6" y="6" width="52" height="52" rx="4" fill="{fg}" opacity=".12"/>
<circle cx="18" cy="18" r="6" fill="{accent}"/>
<path d="M38 12 L50 16 L44 28 L32 24 Z" fill="{accent}" opacity=".75"/>
<path d="M12 40 L24 36 L28 50 L14 52 Z" fill="{fg}" opacity=".55"/>
<circle cx="44" cy="44" r="7" fill="{accent}" opacity=".5"/>"""},
            "wren-and-alder": {
                "device": "six-tile swatch board",
                "mark": """\
<rect x="6" y="12" width="15" height="18" fill="{accent}"/><rect x="24.5" y="12" width="15" height="18" fill="{fg}" opacity=".5"/>
<rect x="43" y="12" width="15" height="18" fill="{accent}" opacity=".6"/><rect x="6" y="34" width="15" height="18" fill="{fg}" opacity=".3"/>
<rect x="24.5" y="34" width="15" height="18" fill="{accent}" opacity=".8"/><rect x="43" y="34" width="15" height="18" fill="{fg}" opacity=".6"/>"""},
        },
    },
    "architecture": {
        "trade_label": "Architecture",
        "schema_type": "ProfessionalService",
        "builds": {
            "ansel-row-studio": {
                "device": "hairlines and one red mark",
                "mark": """\
<rect x="8" y="8" width="48" height="48" fill="none" stroke="{fg}" stroke-width="2"/>
<rect x="28" y="28" width="8" height="8" fill="{accent}"/>"""},
            "calderwood-architecture": {
                "device": "sheet set",
                "mark": """\
<rect x="14" y="6" width="40" height="44" fill="none" stroke="{fg}" stroke-width="3" opacity=".5"/>
<rect x="10" y="10" width="40" height="44" fill="none" stroke="{fg}" stroke-width="3" opacity=".75"/>
<rect x="6" y="14" width="40" height="44" fill="{bg}" stroke="{accent}" stroke-width="4"/>"""},
            "halloway-and-prentiss": {
                "device": "section cut line",
                "mark": """\
<path d="M14 42 V22 L32 8 L50 22 V42" fill="none" stroke="{fg}" stroke-width="4"/>
<path d="M6 42 H58" stroke="{accent}" stroke-width="4" stroke-dasharray="8 5"/>"""},
            "merton-field-architects": {
                "device": "drafting grid and site boundary",
                "mark": """\
<path d="M6 22 H58 M6 42 H58 M22 6 V58 M42 6 V58" stroke="{fg}" stroke-width="2" opacity=".45"/>
<path d="M14 14 H50 V50 H14 Z" fill="none" stroke="{accent}" stroke-width="4"/>"""},
            "ostergaard-architects": {
                "device": "title block",
                "mark": """\
<rect x="6" y="34" width="52" height="24" fill="none" stroke="{fg}" stroke-width="3"/>
<path d="M24 34 V58 M42 34 V58 M6 46 H58" stroke="{fg}" stroke-width="3"/>
<rect x="46" y="12" width="12" height="12" fill="{accent}"/>"""},
            "pell-and-marchant": {
                "device": "numbered register",
                "mark": """\
<rect x="8" y="12" width="6" height="6" fill="{accent}"/><rect x="20" y="13" width="36" height="4" fill="{fg}" opacity=".6"/>
<rect x="8" y="29" width="6" height="6" fill="{accent}"/><rect x="20" y="30" width="28" height="4" fill="{fg}" opacity=".6"/>
<rect x="8" y="46" width="6" height="6" fill="{accent}"/><rect x="20" y="47" width="32" height="4" fill="{fg}" opacity=".6"/>"""},
        },
    },
    "luxury-real-estate": {
        "trade_label": "Estate agency",
        "schema_type": "RealEstateAgent",
        "builds": {
            "ashcroft-residential": {
                "device": "the closed door",
                "mark": """\
<rect x="18" y="6" width="28" height="52" fill="{accent}"/>
<circle cx="39" cy="34" r="3" fill="{bg}"/>"""},
            "bellamy-estates": {
                "device": "plate index",
                "mark": """\
<rect x="8" y="10" width="13" height="19" fill="{accent}"/><rect x="25.5" y="10" width="13" height="19" fill="{accent}" opacity=".7"/>
<rect x="43" y="10" width="13" height="19" fill="{accent}" opacity=".5"/><rect x="8" y="35" width="13" height="19" fill="{fg}" opacity=".35"/>
<rect x="25.5" y="35" width="13" height="19" fill="{fg}" opacity=".5"/><rect x="43" y="35" width="13" height="19" fill="{fg}" opacity=".65"/>"""},
            "ellery-and-vane": {
                "device": "storyboard",
                "mark": """\
<rect x="6" y="14" width="24" height="16" fill="{accent}"/><rect x="34" y="14" width="24" height="16" fill="{fg}" opacity=".5"/>
<rect x="6" y="34" width="24" height="16" fill="{fg}" opacity=".5"/><rect x="34" y="34" width="24" height="16" fill="{accent}" opacity=".7"/>"""},
            "marlowe-and-hart": {
                "device": "masthead",
                "mark": """\
<rect x="6" y="14" width="52" height="3" fill="{fg}"/><rect x="6" y="20" width="52" height="3" fill="{fg}"/>
<rect x="14" y="30" width="36" height="12" fill="{accent}"/>
<rect x="6" y="48" width="52" height="3" fill="{fg}"/>"""},
            "rathmore-and-finch": {
                "device": "the plate under the headline",
                "mark": """\
<rect x="6" y="10" width="52" height="36" fill="{accent}"/>
<rect x="6" y="50" width="30" height="4" fill="{fg}" opacity=".6"/>"""},
            "thornbury-property-group": {
                "device": "second door",
                "mark": """\
<rect x="8" y="8" width="20" height="48" fill="{accent}"/><rect x="36" y="8" width="20" height="48" fill="{fg}" opacity=".75"/>
<circle cx="23" cy="32" r="2.5" fill="{bg}"/><circle cx="41" cy="32" r="2.5" fill="{bg}"/>"""},
        },
    },
    "dermatology": {
        "trade_label": "Dermatology",
        "schema_type": "MedicalClinic",
        "builds": {
            "colvin-dermatology": {
                "device": "booking board",
                "mark": """\
<rect x="8" y="10" width="48" height="44" rx="3" fill="none" stroke="{fg}" stroke-width="4"/>
<rect x="8" y="10" width="48" height="10" fill="{fg}" opacity=".7"/>
<rect x="16" y="28" width="14" height="14" fill="{accent}"/>"""},
            "fenmore-dermatology": {
                "device": "single ruled column",
                "mark": """\
<rect x="22" y="6" width="20" height="52" rx="10" fill="{accent}"/>
<circle cx="32" cy="46" r="4" fill="{bg}"/>"""},
            "harrowgate-dermatology": {
                "device": "two doors",
                "mark": """\
<rect x="8" y="8" width="21" height="48" rx="2" fill="{accent}"/>
<rect x="35" y="8" width="21" height="48" rx="2" fill="{fg}" opacity=".6"/>"""},
            "larkin-dermatology": {
                "device": "two lit windows",
                "mark": """\
<rect x="6" y="6" width="52" height="52" rx="3" fill="{fg}" opacity=".15"/>
<rect x="13" y="16" width="16" height="32" fill="{accent}"/>
<rect x="35" y="16" width="16" height="32" fill="{fg}" opacity=".8"/>"""},
            "sundial-dermatology": {
                "device": "sundial",
                "mark": """\
<circle cx="32" cy="32" r="22" fill="none" stroke="{fg}" stroke-width="4" opacity=".6"/>
<circle cx="32" cy="32" r="8" fill="{accent}"/>
<path d="M32 32 L48 16" stroke="{fg}" stroke-width="4" stroke-linecap="round"/>"""},
            "westbrook-skin-and-surgery": {
                "device": "dated slot",
                "mark": """\
<rect x="8" y="12" width="48" height="44" rx="3" fill="none" stroke="{fg}" stroke-width="4"/>
<rect x="8" y="12" width="48" height="10" fill="{fg}" opacity=".7"/>
<rect x="32" y="30" width="16" height="16" fill="{accent}"/>"""},
        },
    },
    "med-spas": {
        "trade_label": "Medical spa",
        "schema_type": "HealthAndBeautyBusiness",
        "builds": {
            "bright-hour-med-spa": {
                "device": "torn ticket",
                "mark": """\
<path d="M8 14 H56 V26 a6 6 0 0 0 0 12 V50 H8 V38 a6 6 0 0 0 0 -12 Z" fill="{accent}"/>"""},
            "juniper-aesthetics": {
                "device": "client quotes",
                "mark": """\
<circle cx="20" cy="26" r="8" fill="{accent}"/><path d="M12 26 q0 14 12 16" fill="none" stroke="{accent}" stroke-width="6" stroke-linecap="round"/>
<circle cx="44" cy="26" r="8" fill="{accent}"/><path d="M36 26 q0 14 12 16" fill="none" stroke="{accent}" stroke-width="6" stroke-linecap="round"/>"""},
            "marisol-aesthetics": {
                "device": "price rail",
                "mark": """\
<rect x="6" y="30" width="52" height="4" fill="{fg}" opacity=".5"/>
<rect x="8" y="16" width="14" height="32" rx="2" fill="{accent}"/>
<rect x="26" y="16" width="14" height="32" rx="2" fill="{accent}" opacity=".7"/>
<rect x="44" y="16" width="14" height="32" rx="2" fill="{accent}" opacity=".45"/>"""},
            "onyx-and-ivory-aesthetics": {
                "device": "owned grid",
                "mark": """\
<rect x="8" y="8" width="14" height="14" fill="{accent}"/><rect x="25" y="8" width="14" height="14" fill="{fg}" opacity=".6"/><rect x="42" y="8" width="14" height="14" fill="{accent}"/>
<rect x="8" y="25" width="14" height="14" fill="{fg}" opacity=".6"/><rect x="25" y="25" width="14" height="14" fill="{accent}"/><rect x="42" y="25" width="14" height="14" fill="{fg}" opacity=".6"/>
<rect x="8" y="42" width="14" height="14" fill="{accent}"/><rect x="25" y="42" width="14" height="14" fill="{fg}" opacity=".6"/><rect x="42" y="42" width="14" height="14" fill="{accent}"/>"""},
            "palmer-row-med-spa": {
                "device": "menu with dot leaders",
                "mark": """\
<rect x="8" y="16" width="20" height="5" fill="{fg}" opacity=".7"/><circle cx="34" cy="18.5" r="2" fill="{fg}" opacity=".4"/><circle cx="41" cy="18.5" r="2" fill="{fg}" opacity=".4"/><rect x="48" y="16" width="8" height="5" fill="{accent}"/>
<rect x="8" y="30" width="16" height="5" fill="{fg}" opacity=".7"/><circle cx="30" cy="32.5" r="2" fill="{fg}" opacity=".4"/><circle cx="37" cy="32.5" r="2" fill="{fg}" opacity=".4"/><rect x="48" y="30" width="8" height="5" fill="{accent}"/>
<rect x="8" y="44" width="22" height="5" fill="{fg}" opacity=".7"/><circle cx="37" cy="46.5" r="2" fill="{fg}" opacity=".4"/><rect x="48" y="44" width="8" height="5" fill="{accent}"/>"""},
            "verity-skin-and-aesthetics": {
                "device": "rolling credit",
                "mark": """\
<circle cx="32" cy="32" r="20" fill="none" stroke="{accent}" stroke-width="7" stroke-dasharray="92 40" stroke-linecap="round"/>
<circle cx="32" cy="32" r="6" fill="{fg}" opacity=".7"/>"""},
        },
    },
    "plastic-surgeons": {
        "trade_label": "Plastic surgery",
        "schema_type": "MedicalClinic",
        "builds": {
            "aldenmore-surgical-aesthetics": {
                "device": "credential seal",
                "mark": """\
<circle cx="32" cy="32" r="22" fill="{accent}"/>
<circle cx="32" cy="32" r="14" fill="none" stroke="{bg}" stroke-width="3"/>
<circle cx="32" cy="32" r="5" fill="{bg}"/>"""},
            "calder-aesthetic-surgery": {
                "device": "one suite",
                "mark": """\
<rect x="12" y="12" width="40" height="40" rx="8" fill="{accent}"/>
<circle cx="32" cy="32" r="6" fill="{bg}"/>"""},
            "marchetti-plastic-surgery": {
                "device": "split gallery frame",
                "mark": """\
<rect x="8" y="10" width="48" height="44" fill="none" stroke="{fg}" stroke-width="4"/>
<rect x="8" y="10" width="22" height="44" fill="{accent}"/>"""},
            "rothbury-plastic-surgery": {
                "device": "fifty minutes",
                "mark": """\
<circle cx="32" cy="32" r="22" fill="none" stroke="{fg}" stroke-width="4"/>
<path d="M32 32 V14 M32 32 L44 40" stroke="{accent}" stroke-width="5" stroke-linecap="round"/>"""},
            "sable-plastic-surgery": {
                "device": "private panel",
                "mark": """\
<rect x="10" y="10" width="44" height="44" rx="4" fill="none" stroke="{accent}" stroke-width="5"/>
<rect x="26" y="26" width="12" height="12" fill="{accent}"/>"""},
            "wyeth-plastic-surgery": {
                "device": "portfolio grid",
                "mark": """\
<rect x="8" y="8" width="22" height="22" fill="{fg}" opacity=".55"/><rect x="34" y="8" width="22" height="22" fill="{accent}"/>
<rect x="8" y="34" width="22" height="22" fill="{accent}" opacity=".7"/><rect x="34" y="34" width="22" height="22" fill="{fg}" opacity=".55"/>"""},
        },
    },
    "veterinary": {
        "trade_label": "Veterinary",
        "schema_type": "VeterinaryCare",
        "builds": {
            "beckett-animal-care": {
                "device": "front door with the prices on it",
                "mark": """\
<rect x="16" y="6" width="32" height="52" rx="3" fill="{accent}"/>
<rect x="22" y="20" width="20" height="6" fill="{bg}"/><rect x="22" y="32" width="14" height="6" fill="{bg}"/>"""},
            "corner-oak-veterinary": {
                "device": "two counter keys",
                "mark": """\
<rect x="6" y="20" width="24" height="24" rx="5" fill="{accent}"/>
<rect x="34" y="20" width="24" height="24" rx="5" fill="{fg}" opacity=".7"/>"""},
            "fernhill-veterinary": {
                "device": "row of portraits",
                "mark": """\
<circle cx="14" cy="28" r="8" fill="{accent}"/><circle cx="32" cy="28" r="8" fill="{accent}"/><circle cx="50" cy="28" r="8" fill="{accent}"/>
<rect x="6" y="42" width="52" height="8" rx="4" fill="{fg}" opacity=".5"/>"""},
            "hollis-animal-hospital": {
                "device": "amber after-hours rail",
                "mark": """\
<rect x="6" y="6" width="52" height="52" rx="4" fill="{fg}" opacity=".15"/>
<circle cx="32" cy="24" r="8" fill="{accent}"/>
<rect x="6" y="40" width="52" height="8" fill="{accent}"/>"""},
            "marlow-veterinary-clinic": {
                "device": "swinging open sign",
                "mark": """\
<path d="M20 6 V16 M44 6 V16" stroke="{fg}" stroke-width="4"/>
<rect x="10" y="16" width="44" height="32" rx="4" fill="{accent}"/>
<rect x="20" y="29" width="24" height="6" fill="{bg}"/>"""},
            "willowbank-animal-hospital": {
                "device": "lit lamp in a panel",
                "mark": """\
<rect x="8" y="8" width="48" height="48" rx="4" fill="none" stroke="{fg}" stroke-width="4"/>
<circle cx="32" cy="28" r="10" fill="{accent}"/>
<rect x="29" y="38" width="6" height="12" fill="{fg}" opacity=".7"/>"""},
        },
    },
    "accounting-cpas": {
        "trade_label": "CPA firm",
        "schema_type": "AccountingService",
        "builds": {
            "ashby-and-kerr-cpas": {
                "device": "ticked checklist",
                "mark": """\
<path d="M8 16 l4 4 7 -8" fill="none" stroke="{accent}" stroke-width="4" stroke-linecap="round"/><rect x="26" y="14" width="30" height="5" fill="{fg}" opacity=".6"/>
<path d="M8 33 l4 4 7 -8" fill="none" stroke="{accent}" stroke-width="4" stroke-linecap="round"/><rect x="26" y="31" width="24" height="5" fill="{fg}" opacity=".6"/>
<path d="M8 50 l4 4 7 -8" fill="none" stroke="{accent}" stroke-width="4" stroke-linecap="round"/><rect x="26" y="48" width="28" height="5" fill="{fg}" opacity=".6"/>"""},
            "brandt-and-yoo-cpas": {
                "device": "document down the rail into the portal",
                "mark": """\
<rect x="30" y="6" width="4" height="30" fill="{fg}" opacity=".5"/>
<rect x="22" y="8" width="20" height="14" fill="{accent}"/>
<rect x="12" y="40" width="40" height="18" rx="2" fill="{fg}" opacity=".75"/>"""},
            "corven-cpa-group": {
                "device": "four-node flow",
                "mark": """\
<rect x="8" y="30" width="48" height="4" fill="{fg}" opacity=".45"/>
<circle cx="12" cy="32" r="6" fill="{accent}"/><circle cx="25" cy="32" r="6" fill="{accent}"/>
<circle cx="39" cy="32" r="6" fill="{accent}"/><circle cx="52" cy="32" r="6" fill="{accent}"/>"""},
            "halstead-accounting": {
                "device": "three-box document path",
                "mark": """\
<rect x="6" y="24" width="13" height="16" fill="none" stroke="{fg}" stroke-width="3"/>
<rect x="25.5" y="24" width="13" height="16" fill="none" stroke="{fg}" stroke-width="3"/>
<rect x="45" y="24" width="13" height="16" fill="{accent}"/>"""},
            "latimer-accounting": {
                "device": "request ledger, ticked column",
                "mark": """\
<rect x="8" y="14" width="34" height="5" fill="{fg}" opacity=".6"/><rect x="48" y="12" width="8" height="8" fill="{accent}"/>
<rect x="8" y="30" width="34" height="5" fill="{fg}" opacity=".6"/><rect x="48" y="28" width="8" height="8" fill="{accent}"/>
<rect x="8" y="46" width="34" height="5" fill="{fg}" opacity=".6"/><rect x="48" y="44" width="8" height="8" fill="{accent}"/>"""},
            "rennick-cpa": {
                "device": "four-station track",
                "mark": """\
<rect x="10" y="10" width="44" height="44" rx="22" fill="none" stroke="{fg}" stroke-width="4" opacity=".5"/>
<circle cx="32" cy="10" r="5.5" fill="{accent}"/><circle cx="54" cy="32" r="5.5" fill="{accent}"/>
<circle cx="32" cy="54" r="5.5" fill="{accent}"/><circle cx="10" cy="32" r="5.5" fill="{accent}"/>"""},
        },
    },
    "wealth-management": {
        "trade_label": "Wealth management",
        "schema_type": "FinancialService",
        "builds": {
            "bracken-and-lowe": {
                "device": "three conversations",
                "mark": """\
<circle cx="14" cy="18" r="5" fill="{accent}"/><rect x="24" y="16" width="32" height="4" fill="{fg}" opacity=".6"/>
<circle cx="14" cy="32" r="5" fill="{accent}"/><rect x="24" y="30" width="26" height="4" fill="{fg}" opacity=".6"/>
<circle cx="14" cy="46" r="5" fill="{accent}"/><rect x="24" y="44" width="30" height="4" fill="{fg}" opacity=".6"/>"""},
            "copeland-fiduciary": {
                "device": "hairline ledger",
                "mark": """\
<rect x="8" y="8" width="48" height="48" fill="none" stroke="{fg}" stroke-width="2.5"/>
<path d="M40 8 V56" stroke="{fg}" stroke-width="2.5"/>
<rect x="44" y="18" width="8" height="4" fill="{accent}"/><rect x="44" y="30" width="8" height="4" fill="{accent}"/><rect x="44" y="42" width="8" height="4" fill="{accent}"/>"""},
            "ferrier-wealth-partners": {
                "device": "the statement",
                "mark": """\
<rect x="14" y="6" width="36" height="52" fill="none" stroke="{fg}" stroke-width="3"/>
<rect x="20" y="16" width="24" height="3" fill="{fg}" opacity=".6"/><rect x="20" y="26" width="24" height="3" fill="{fg}" opacity=".6"/>
<rect x="20" y="36" width="24" height="3" fill="{fg}" opacity=".6"/><rect x="20" y="46" width="14" height="5" fill="{accent}"/>"""},
            "hartwell-wealth-advisors": {
                "device": "dot leader",
                "mark": """\
<rect x="8" y="29" width="16" height="6" fill="{fg}" opacity=".7"/>
<circle cx="30" cy="32" r="2" fill="{fg}" opacity=".45"/><circle cx="37" cy="32" r="2" fill="{fg}" opacity=".45"/><circle cx="44" cy="32" r="2" fill="{fg}" opacity=".45"/>
<rect x="50" y="29" width="8" height="6" fill="{accent}"/>"""},
            "ostrander-wealth-counsel": {
                "device": "double-rule masthead",
                "mark": """\
<rect x="8" y="18" width="48" height="3" fill="{fg}"/><rect x="8" y="24" width="48" height="3" fill="{fg}"/>
<rect x="22" y="34" width="20" height="12" fill="{accent}"/>"""},
            "winslow-family-wealth": {
                "device": "two generations",
                "mark": """\
<circle cx="24" cy="32" r="16" fill="{accent}"/>
<circle cx="42" cy="32" r="16" fill="{fg}" opacity=".55"/>"""},
        },
    },
    "recruiting": {
        "trade_label": "Industrial recruitment",
        "schema_type": "EmploymentAgency",
        "builds": {
            "brandt-yates-recruitment": {
                "device": "four, not twelve",
                "mark": """\
<circle cx="16" cy="22" r="9" fill="{accent}"/><circle cx="48" cy="22" r="9" fill="{accent}"/>
<circle cx="16" cy="44" r="9" fill="{accent}"/><circle cx="48" cy="44" r="9" fill="{accent}"/>"""},
            "copperfield-industrial-search": {
                "device": "sector cog",
                "mark": """\
<circle cx="32" cy="32" r="14" fill="none" stroke="{accent}" stroke-width="8"/>
<path d="M32 6 V16 M32 48 V58 M6 32 H16 M48 32 H58" stroke="{accent}" stroke-width="7" stroke-linecap="round"/>"""},
            "ellings-search-group": {
                "device": "screening wall",
                "mark": """\
<rect x="8" y="10" width="22" height="10" fill="{accent}"/><rect x="34" y="10" width="22" height="10" fill="{fg}" opacity=".55"/>
<rect x="8" y="26" width="48" height="10" fill="{fg}" opacity=".55"/>
<rect x="8" y="42" width="22" height="10" fill="{fg}" opacity=".55"/><rect x="34" y="42" width="22" height="10" fill="{accent}"/>"""},
            "halbrook-search": {
                "device": "role list with a tap",
                "mark": """\
<rect x="8" y="14" width="30" height="6" fill="{fg}" opacity=".6"/><circle cx="50" cy="17" r="6" fill="{accent}"/>
<rect x="8" y="30" width="30" height="6" fill="{fg}" opacity=".6"/><circle cx="50" cy="33" r="6" fill="{accent}"/>
<rect x="8" y="46" width="30" height="6" fill="{fg}" opacity=".6"/><circle cx="50" cy="49" r="6" fill="{accent}"/>"""},
            "ironvale-partners": {
                "device": "the switch",
                "mark": """\
<rect x="6" y="20" width="52" height="24" rx="12" fill="{fg}" opacity=".45"/>
<circle cx="44" cy="32" r="10" fill="{accent}"/>"""},
            "kirkwall-talent": {
                "device": "one tap",
                "mark": """\
<circle cx="32" cy="32" r="10" fill="{accent}"/>
<circle cx="32" cy="32" r="20" fill="none" stroke="{accent}" stroke-width="4" opacity=".5"/>"""},
        },
    },
    "property-management": {
        "trade_label": "Property management",
        "schema_type": "RealEstateAgent",
        "builds": {
            "amberton-residential": {
                "device": "door run",
                "mark": """\
<rect x="6" y="14" width="10" height="36" fill="{accent}"/><rect x="20" y="14" width="10" height="36" fill="{accent}" opacity=".75"/>
<rect x="34" y="14" width="10" height="36" fill="{accent}" opacity=".5"/><rect x="48" y="14" width="10" height="36" fill="{fg}" opacity=".35"/>"""},
            "colvert-property-group": {
                "device": "eight percent",
                "mark": """\
<circle cx="20" cy="20" r="8" fill="{accent}"/><circle cx="44" cy="44" r="8" fill="{accent}"/>
<path d="M12 52 L52 12" stroke="{fg}" stroke-width="6" stroke-linecap="round"/>"""},
            "halcombe-management": {
                "device": "lit strip on the night",
                "mark": """\
<rect x="6" y="6" width="52" height="52" rx="4" fill="{fg}" opacity=".15"/>
<rect x="6" y="28" width="52" height="10" fill="{accent}"/>"""},
            "ridgemont-property-services": {
                "device": "work-order docket",
                "mark": """\
<rect x="10" y="6" width="44" height="52" fill="none" stroke="{fg}" stroke-width="4"/>
<rect x="18" y="16" width="28" height="5" fill="{accent}"/>
<rect x="18" y="28" width="20" height="4" fill="{fg}" opacity=".6"/><rect x="18" y="38" width="24" height="4" fill="{fg}" opacity=".6"/><rect x="18" y="48" width="12" height="4" fill="{fg}" opacity=".6"/>"""},
            "rowan-property-group": {
                "device": "owner statement",
                "mark": """\
<rect x="8" y="14" width="48" height="5" fill="{accent}"/>
<rect x="8" y="26" width="48" height="3" fill="{fg}" opacity=".6"/><rect x="8" y="36" width="48" height="3" fill="{fg}" opacity=".6"/><rect x="8" y="46" width="30" height="3" fill="{fg}" opacity=".6"/>"""},
            "weatherby-property-co": {
                "device": "portal window",
                "mark": """\
<rect x="8" y="10" width="48" height="44" rx="3" fill="none" stroke="{fg}" stroke-width="4"/>
<rect x="8" y="10" width="48" height="8" fill="{fg}"/><circle cx="14" cy="14" r="2" fill="{accent}"/>
<rect x="16" y="26" width="32" height="5" fill="{accent}"/><rect x="16" y="37" width="22" height="5" fill="{fg}" opacity=".5"/>"""},
        },
    },
    "cosmetic-dentists": {
        "trade_label": "Cosmetic dentistry",
        "schema_type": "Dentist",
        "builds": {
            "aldridge-dental": {
                "device": "one plan",
                "mark": """\
<rect x="12" y="18" width="40" height="28" rx="4" fill="{accent}"/>
<rect x="20" y="30" width="24" height="4" fill="{bg}"/>"""},
            "belmont-smile-design": {
                "device": "preview beside the headline",
                "mark": """\
<rect x="6" y="12" width="22" height="40" fill="{fg}" opacity=".5"/>
<rect x="34" y="12" width="24" height="40" rx="3" fill="{accent}"/>"""},
            "callaway-dental-arts": {
                "device": "the free hour",
                "mark": """\
<circle cx="32" cy="32" r="22" fill="none" stroke="{fg}" stroke-width="4" opacity=".5"/>
<path d="M32 32 V12 A20 20 0 0 1 52 32 Z" fill="{accent}"/>"""},
            "fairmont-dental-studio": {
                "device": "scanned, planned, priced",
                "mark": """\
<circle cx="13" cy="32" r="8" fill="{accent}"/><circle cx="32" cy="32" r="8" fill="{accent}" opacity=".7"/><circle cx="51" cy="32" r="8" fill="{accent}" opacity=".45"/>"""},
            "havenwood-dental": {
                "device": "the warm band",
                "mark": """\
<rect x="6" y="22" width="52" height="20" rx="10" fill="{accent}"/>
<circle cx="18" cy="32" r="5" fill="{bg}"/>"""},
            "verano-cosmetic-dentistry": {
                "device": "showcase grid",
                "mark": """\
<rect x="6" y="12" width="15" height="18" fill="{accent}"/><rect x="24.5" y="12" width="15" height="18" fill="{fg}" opacity=".5"/><rect x="43" y="12" width="15" height="18" fill="{accent}" opacity=".6"/>
<rect x="6" y="34" width="15" height="18" fill="{fg}" opacity=".5"/><rect x="24.5" y="34" width="15" height="18" fill="{accent}" opacity=".8"/><rect x="43" y="34" width="15" height="18" fill="{fg}" opacity=".35"/>"""},
        },
    },
}


# --- resolving a spec from the build itself ---------------------------------
# Roofing's specs were typed out in full. Every trade after it hands over only
# the mark and the device it is drawn from; the name, palette, display face,
# headline, phone and tagline are all already on the page, and reading them
# from there means a copy change in the harness cannot leave a stale social
# card behind.

import re
from pathlib import Path

WORK = Path(__file__).resolve().parent.parent / "work"
_HEX = re.compile(r"#(?:[0-9a-fA-F]{3}){1,2}")


def _lum(hex_colour: str) -> float:
    h = hex_colour.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _tokens(src: str) -> dict:
    m = re.search(r":root\s*\{(.*?)\}", src, re.S)
    out = {}
    if m:
        for decl in m.group(1).split(";"):
            if ":" in decl:
                k, v = decl.split(":", 1)
                out[k.strip()] = v.strip()
    return out


def _hex_of(tokens: dict, *names: str):
    for n in names:
        m = _HEX.fullmatch(tokens.get(n, ""))
        if m:
            return m.group(0)
    return None


def derive(trade_slug: str, slug: str) -> dict:
    """Everything about a build that is not the mark, read off its page."""
    src = (WORK / trade_slug / f"{slug}.html").read_text()
    t = _tokens(src)

    surface = _hex_of(t, "--surface", "--bg", "--paper", "--slate", "--panel") or "#FFFFFF"
    accent = _hex_of(t, "--accent") or "#000000"
    ink = _hex_of(t, "--ink")
    text = _hex_of(t, "--text")
    if not text:
        text = ink if ink and abs(_lum(ink) - _lum(surface)) > 0.35 else (
            "#FFFFFF" if _lum(surface) < 0.45 else "#111111")
    dark, light = sorted([surface, text], key=_lum)
    # The social card sits on the build's darker colour; the accent has to
    # read against it or the mark takes the light colour instead.
    card_accent = accent if abs(_lum(accent) - _lum(dark)) > 0.25 else light

    m = re.search(r'<a class="brand"[^>]*>(.*?)</a>', src, re.S)
    name = re.sub(r"<[^>]+>", "", m.group(1)).strip() if m else slug
    name = name.replace("&amp;", "&")

    m = re.search(r"<h1[^>]*>(.*?)</h1>", src, re.S)
    headline = " ".join(re.sub(r"<[^>]+>", " ", m.group(1)).split()) if m else ""

    m = re.search(r'class="topbar"[^>]*>(.*?)</div>', src, re.S)
    tagline = " ".join(re.sub(r"<[^>]+>", " ", m.group(1)).split()) if m else ""
    tagline = tagline.replace("&amp;", "&")

    m = re.search(r"\(\d{3}\) \d{3}-\d{4}", src)
    phone = m.group(0) if m else ""

    families = re.findall(r"family=([^&\"]+)", src)
    m = re.search(r"^\s*(.+?) display / .+? body", src, re.M)
    display = m.group(1).strip() if m else (families[0].split(":")[0].replace("+", " ") if families else "Inter")
    display_css = next((f for f in families if f.split(":")[0].replace("+", " ") == display),
                       display.replace(" ", "+"))
    weights = [int(w) for w in re.findall(r"\d{3}", display_css.split(":")[1])] if ":" in display_css else []
    display_weight = max(weights) if weights else 400
    uppercase = bool(re.search(r"h1[^{]*\{[^}]*text-transform:\s*uppercase", src))

    return {
        "name": name,
        "palette": {"ink": ink or text, "surface": surface, "accent": accent,
                    "text": text, "dark": dark, "light": light,
                    "fg": text, "bg": surface},
        "card_bg": dark, "card_fg": light, "card_accent": card_accent,
        "card_mark": None if card_accent == accent else light,
        "display_font": display, "display_css": display_css,
        "display_weight": display_weight, "uppercase": uppercase,
        "headline": headline, "phone": phone, "tagline": tagline,
    }


def resolve(trade_slug: str, slug: str) -> dict | None:
    """The hand-written spec over the derived one. Roofing's full specs pass
    through untouched; a newer trade's `{"device", "mark"}` gets the rest."""
    hand = BUILDS.get(trade_slug, {}).get("builds", {}).get(slug)
    if not hand:
        return None
    if "palette" in hand and "headline" in hand:
        return hand
    base = derive(trade_slug, slug)
    merged = {**base, **hand}
    merged["palette"] = {**base["palette"], **hand.get("palette", {})}
    return merged


def resolved_builds(trade_slug: str) -> dict:
    return {slug: resolve(trade_slug, slug)
            for slug in BUILDS.get(trade_slug, {}).get("builds", {})}


def mark_svg(spec: dict, size: int | None = None, background: str | None = None) -> str:
    """Standalone SVG for a build's mark, optionally on a solid ground.

    Fair Oaks' accent *is* its card ground, so a mark drawn in the page palette
    would vanish on its own social card. `card_mark` overrides the accent for
    exactly that case; builds that read fine on their ground omit it.

    Derived specs draw with `fg` / `bg` rather than literal colours, so on a
    card those two are remapped to the card's own pair.
    """
    palette = dict(spec["palette"])
    if background:
        if spec.get("card_mark"):
            palette["accent"] = spec["card_mark"]
        if "fg" in palette:
            palette["fg"] = spec.get("card_fg", palette["fg"])
            palette["bg"] = spec.get("card_bg", palette["bg"])
    inner = spec["mark"].format(**palette)
    dims = f' width="{size}" height="{size}"' if size else ""
    ground = f'<rect width="64" height="64" fill="{background}"/>' if background else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"{dims} '
            f'role="img" aria-label="{spec["name"]}">{ground}{inner}</svg>')
