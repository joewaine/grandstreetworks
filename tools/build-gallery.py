#!/usr/bin/env python3
"""Add a recent-work gallery — before/after plus process detail — to each build.

Sixteen of the 120 builds talk about before-and-after in copy while showing
nothing, and every build ships exactly one photograph. This injects the band the
copy already promises, immediately above each build's closing CTA.

The band has to sit inside six unrelated designs without looking bolted on, so
it borrows rather than declares:

  * colour comes from the custom properties every build defines anyway
    (--ink, --surface, --accent, --muted, --rule, --wrap), which means the dark
    build gets a dark band with no special case;
  * type comes from using a real <h2> and <p>, so each build's own display face
    and heading ramp apply with nothing hardcoded;
  * the image set differs per build, so six galleries in one trade index do not
    read as the same six photographs six times.

    python3 tools/build-gallery.py roofing
    python3 tools/build-gallery.py roofing --replace

Run build-responsive-images.py --kind library first; this points at that ladder.
"""

import argparse
import html
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
WORK = REPO / "work"
MARKER = "<!-- gsw:gallery -->"
END_MARKER = "<!-- /gsw:gallery -->"
CLOSE_RE = re.compile(r'<section class="(?:[\w-]+ )*close(?: [\w-]+)*"')

AVIF_WIDTHS = (640, 1280)
JPEG_WIDTH = 720

# name -> (caption, aspect)
CAPTIONS = {
    "roofing": {
        "tear-off": ("Tear-off, down to the deck", "4:3"),
        "underlayment": ("Synthetic underlayment", "4:3"),
        "courses": ("New courses going on", "4:3"),
        "ridge-vent": ("Ridge vent and cap", "4:3"),
        "flashing": ("Step flashing at the chimney", "4:3"),
        "drip-edge": ("Drip edge and gutter", "4:3"),
        "jobsite": ("Site protected, drive clear", "4:3"),
        "finished-home": ("Finished, from the kerb", "16:9"),
        "damage-before": ("Before", "4:3"),
        "damage-after": ("After", "4:3"),
    },
    "hvac": {
        "condenser-set": ("New condenser, set and levelled", "4:3"),
        "air-handler": ("Air handler, plenum sealed", "4:3"),
        "ductwork": ("Duct joints sealed with mastic", "4:3"),
        "attic-run": ("Attic runs, strapped and insulated", "4:3"),
        "thermostat": ("Thermostat set up before we leave", "4:3"),
        "gauges": ("Charged to the factory numbers", "4:3"),
        "coil-cleaning": ("Coil cleaned, fins straightened", "4:3"),
        "van-jobsite": ("Evening call, van at the kerb", "4:3"),
        "unit-before": ("Before", "4:3"),
        "unit-after": ("After", "4:3"),
    },
    "restoration": {
        "extraction": ("Extraction, first hour", "4:3"),
        "air-movers": ("Air movers and dehumidifiers set", "4:3"),
        "moisture-meter": ("Moisture readings, logged daily", "4:3"),
        "containment": ("Containment for mould work", "4:3"),
        "smoke-clean": ("Soot, half cleaned", "4:3"),
        "demo": ("Cut at the flood line", "4:3"),
        "truck-night": ("At the kerb, three in the morning", "4:3"),
        "rebuild": ("Drywall back, taped and mudded", "4:3"),
        "flood-before": ("Before", "4:3"),
        "flood-after": ("After", "4:3"),
    },
    "pool-builders": {
        "excavation": ("Steel tied, ready for gunite", "4:3"),
        "gunite": ("Gunite shell, shot in a day", "4:3"),
        "tile-line": ("Setting the waterline tile", "4:3"),
        "plaster": ("Plaster, trowelled by hand", "4:3"),
        "coping": ("Coping at the waterline", "4:3"),
        "spa-spillover": ("Spa spillover, dusk", "4:3"),
        "outdoor-living": ("The rest of the garden", "4:3"),
        "night-lights": ("Lit for the evening", "4:3"),
        "yard-before": ("Before", "4:3"),
        "yard-after": ("After", "4:3"),
    },
    "solar": {
        "rail-install": ("Rails flashed to the rafters", "4:3"),
        "panels-going-on": ("Panels going on", "4:3"),
        "inverter": ("Inverter and disconnect", "4:3"),
        "battery": ("Battery on the wall", "4:3"),
        "conduit": ("Conduit, clipped and painted", "4:3"),
        "roof-array-detail": ("Flashed at every foot", "4:3"),
        "street-of-roofs": ("Six arrays on one street", "4:3"),
        "crew-van": ("Our crew, our van", "4:3"),
        "roof-before": ("Before", "4:3"),
        "roof-after": ("After", "4:3"),
    },
    "general-contractors": {
        "kitchen-demo": ("Demolition, floors protected", "4:3"),
        "framing": ("Framing the new opening", "4:3"),
        "rough-in": ("Rough-in, inspected before it closes", "4:3"),
        "drywall": ("Drywall, taped and mudded", "4:3"),
        "tile-work": ("Setting the tile", "4:3"),
        "site-daily": ("Site, end of day", "4:3"),
        "finished-kitchen": ("Finished", "4:3"),
        "addition-exterior": ("Addition, framed and sheathed", "4:3"),
        "kitchen-before": ("Before", "4:3"),
        "kitchen-after": ("After", "4:3"),
    },
    "custom-home-builders": {
        "site-walk": ("Walking the site", "4:3"),
        "foundation": ("Foundation, stripped", "4:3"),
        "framing-detail": ("Framing the tall openings", "4:3"),
        "joinery": ("Joinery, fitted by hand", "4:3"),
        "stone-facade": ("Stone, laid course by course", "4:3"),
        "interior-finish": ("The great room, finished", "4:3"),
        "kitchen": ("Kitchen, handed over", "4:3"),
        "exterior-evening": ("Evening, from the drive", "4:3"),
        "house-framing": ("Framing", "4:3"),
        "house-finished": ("Move-in", "4:3"),
    },
    "interior-design": {
        "material-board": ("The sample board", "4:3"),
        "plaster-wall": ("Limewash, in afternoon light", "4:3"),
        "upholstery": ("The workroom", "4:3"),
        "joinery-detail": ("Joinery, brass and oak", "4:3"),
        "lighting": ("Lit for evening", "4:3"),
        "install-day": ("Install day", "4:3"),
        "styled-shelf": ("Styled, last", "4:3"),
        "living-room": ("The whole room", "4:3"),
        "room-before": ("Before", "4:3"),
        "room-after": ("After", "4:3"),
    },
    "architecture": {
        "model": ("Study model, third iteration", "4:3"),
        "drawing-macro": ("The section, drawn", "4:3"),
        "concrete-detail": ("Concrete meets oak", "4:3"),
        "stair": ("The stair", "4:3"),
        "site-visit": ("On site, before the drawings", "4:3"),
        "facade": ("The built work", "4:3"),
        "adaptive-reuse": ("New steel in an old shell", "4:3"),
        "civic-interior": ("The hall", "4:3"),
        "material-samples": ("Samples on the table", "4:3"),
        "construction": ("Under construction", "4:3"),
    },
    "luxury-real-estate": {
        "entry-hall": ("The entry", "4:3"),
        "kitchen": ("Kitchen, at twilight", "4:3"),
        "pool-terrace": ("Terrace and pool", "4:3"),
        "drone-estate": ("The estate, from above", "4:3"),
        "library-room": ("The study", "4:3"),
        "garden-path": ("The garden", "4:3"),
        "bathroom": ("Principal bath", "4:3"),
        "film-crew": ("Filmed, not photographed", "4:3"),
        "threshold": ("The threshold", "4:3"),
        "twilight-facade": ("Twilight, from the drive", "4:3"),
    },
    "dermatology": {
        "dermatoscope": ("The dermatoscope, every check", "4:3"),
        "exam-room": ("Exam room", "4:3"),
        "mohs-lab": ("Mohs lab, same day", "4:3"),
        "laser-suite": ("Laser suite", "4:3"),
        "skin-macro": ("Skin, in light", "4:3"),
        "reception": ("Reception", "4:3"),
        "instrument-tray": ("The biopsy tray", "4:3"),
        "phone-call": ("Results, by phone", "4:3"),
        "sunlight-window": ("The waiting room", "4:3"),
        "pediatric-room": ("Paediatric room", "4:3"),
    },
    "med-spas": {
        "treatment-room": ("Treatment room", "4:3"),
        "flatlay": ("Set up for the appointment", "4:3"),
        "injector-hands": ("Drawn up, in front of you", "4:3"),
        "laser-device": ("Laser and resurfacing", "4:3"),
        "skincare-shelf": ("What we stock", "4:3"),
        "consult-room": ("The consultation", "4:3"),
        "reception": ("Reception", "4:3"),
        "lounge": ("The lounge", "4:3"),
        "towel-detail": ("Ready", "4:3"),
        "evening-window": ("Evening appointments", "4:3"),
    },
    "plastic-surgeons": {
        "consult-room": ("The consultation room", "4:3"),
        "operating-suite": ("The suite", "4:3"),
        "recovery-room": ("Recovery", "4:3"),
        "gloved-hands": ("Preparation", "4:3"),
        "instrument-tray": ("Set out", "4:3"),
        "corridor": ("The corridor", "4:3"),
        "private-entrance": ("The private entrance", "4:3"),
        "imaging-room": ("Imaging", "4:3"),
        "waiting-lounge": ("One patient at a time", "4:3"),
        "aftercare-kit": ("Aftercare, packed", "4:3"),
    },
    "veterinary": {
        "exam-table": ("The exam room", "4:3"),
        "reception": ("Reception", "4:3"),
        "surgical-suite": ("Surgery", "4:3"),
        "dental": ("Dental", "4:3"),
        "lab": ("Lab, results the same visit", "4:3"),
        "kennel-recovery": ("Recovery", "4:3"),
        "pharmacy": ("Pharmacy and refills", "4:3"),
        "puppy-visit": ("Puppy visit", "4:3"),
        "cat-room": ("The cat room", "4:3"),
        "night-entrance": ("After hours", "4:3"),
    },
    "accounting-cpas": {
        "closed-ledger": ("Books closed", "4:3"),
        "folders": ("Everything in its place", "4:3"),
        "scanner": ("Scanned, not emailed", "4:3"),
        "meeting-room": ("The quarterly conversation", "4:3"),
        "office-morning": ("Seven in the morning, busy season", "4:3"),
        "signing": ("Signed off", "4:3"),
        "archive": ("Seven years, on file", "4:3"),
        "quiet-desk": ("The desk", "4:3"),
        "window": ("The view from the tenth", "4:3"),
        "handshake": ("Engaged", "4:3"),
    },
    "wealth-management": {
        "two-chairs": ("Two chairs", "4:3"),
        "ruled-sheet": ("The fee, on one page", "4:3"),
        "brass-door": ("The door", "4:3"),
        "bound-volumes": ("Sixty years of files", "4:3"),
        "graphite": ("Worked out in pencil", "4:3"),
        "street": ("The street, at eight", "4:3"),
        "family-table": ("The family table", "4:3"),
        "bound-plan": ("The plan, bound", "4:3"),
        "window-light": ("Afternoon", "4:3"),
        "keys": ("Handed over", "4:3"),
    },
    "recruiting": {
        "shop-floor": ("The floor", "4:3"),
        "control-panel": ("At the panel", "4:3"),
        "plant-exterior": ("Shift change", "4:3"),
        "interview-room": ("The interview", "4:3"),
        "hard-hats": ("Hooks by the door", "4:3"),
        "precision-parts": ("Precision parts", "4:3"),
        "phone-desk": ("Answered by a person", "4:3"),
        "warehouse": ("The warehouse", "4:3"),
        "welding": ("Second shift", "4:3"),
        "forklift-yard": ("The yard", "4:3"),
    },
    "property-management": {
        "keys-desk": ("The keys", "4:3"),
        "brick-facade": ("The asset", "4:3"),
        "lockbox": ("Lockbox, not a phone call", "4:3"),
        "maintenance-van": ("Maintenance, dispatched", "4:3"),
        "work-order": ("The work order, done", "4:3"),
        "unit-ready": ("Ready to let", "4:3"),
        "portfolio-aerial": ("The portfolio", "4:3"),
        "inspection": ("Inspected", "4:3"),
        "leasing-office": ("The office", "4:3"),
        "showing": ("Showing", "4:3"),
    },
    "cosmetic-dentists": {
        "chairside-preview": ("Chairside preview", "4:3"),
        "shade-guide": ("Shade matched", "4:3"),
        "operatory": ("The treatment room", "4:3"),
        "scanner": ("Scanned, not moulded", "4:3"),
        "veneer-macro": ("Porcelain, one at a time", "4:3"),
        "whitening-tray": ("Custom whitening tray", "4:3"),
        "lab-bench": ("On the technician's bench", "4:3"),
        "reception": ("Reception", "4:3"),
    },
}

# The before/after pair that leads each trade's band, where the trade has an
# honest one. Named per trade because what "before" means differs: storm damage
# for a roof, a failed unit for HVAC. Trades without an entry get six tiles.
PAIRS = {
    "roofing": ("damage-before", "damage-after"),
    "hvac": ("unit-before", "unit-after"),
    "restoration": ("flood-before", "flood-after"),
    "pool-builders": ("yard-before", "yard-after"),
    "solar": ("roof-before", "roof-after"),
    "general-contractors": ("kitchen-before", "kitchen-after"),
    "custom-home-builders": ("house-framing", "house-finished"),
    "interior-design": ("room-before", "room-after"),
}

# Each build shows a different three, so a trade index scrolling six builds does
# not show the same gallery six times.
SETS = {
    "roofing": {
        "halloran-roofing": {
            "label": "Recent work", "heading": "The storm week, start to finish.",
            "note": "One street, one week: the call that came in at nine, and the roof that "
                    "was finished before the next front arrived.",
            "tiles": ["tear-off", "jobsite", "finished-home"]},
        "fair-oaks-roofing": {
            "label": "On your street", "heading": "Four houses, same postcode.",
            "note": "Every one of these is a house someone can drive past. Ask them what "
                    "the week was like. That is the only reference that counts.",
            "tiles": ["finished-home", "drip-edge", "courses"]},
        "meridian-roof-co": {
            "label": "Recent work", "heading": "What 2,400 roofs looks like up close.",
            "note": "The same sequence on every job, whether it is a repair or a full "
                    "replacement. Six crews, one standard.",
            "tiles": ["courses", "ridge-vent", "jobsite"]},
        "anchor-peak-roofing": {
            "label": "On the job", "heading": "Tarped, stripped, replaced.",
            "note": "Emergency work does not mean rough work. The same details get done "
                    "at two in the morning as at two in the afternoon.",
            "tiles": ["tear-off", "underlayment", "flashing"]},
        "sentry-roofing-and-restoration": {
            "label": "Documented", "heading": "Photographed for the adjuster.",
            "note": "Every job is documented the way a claim needs it: before, during "
                    "and after, with the detail shots the adjuster will ask for.",
            "tiles": ["flashing", "drip-edge", "ridge-vent"]},
        "northgate-roofing": {
            "label": "Dispatched", "heading": "From the call to the clear-up.",
            "note": "What happens after someone answers: a crew, a protected site, and "
                    "a driveway you can park on the same evening.",
            "tiles": ["jobsite", "underlayment", "tear-off"]},
    },
    "hvac": {
        "ironwood-heating-and-air": {
            "label": "Dispatched", "heading": "From the call to the first warm vent.",
            "note": "What happens after a human answers: a van at the kerb, the fault "
                    "photographed, and a written price before anything is touched.",
            "tiles": ["van-jobsite", "gauges", "air-handler"]},
        "sutter-heating-and-cooling": {
            "label": "Recent work", "heading": "What $89 a month actually buys.",
            "note": "A right-sized system from a proper load calculation, and the rebate "
                    "paperwork done before install day rather than after.",
            "tiles": ["condenser-set", "thermostat", "ductwork"]},
        "vantage-air-systems": {
            "label": "Hot side, cold side", "heading": "Where the uneven rooms come from.",
            "note": "Leaking joints and crushed runs in the attic, more often than the "
                    "unit itself. We seal what we find and show you the photographs.",
            "tiles": ["ductwork", "attic-run", "thermostat"]},
        "nightingale-heating-and-air": {
            "label": "The night call", "heading": "Two in the morning looks like this.",
            "note": "Same tools, same checks, same price as a Tuesday. The only thing "
                    "that changes is the light we work in.",
            "tiles": ["van-jobsite", "gauges", "coil-cleaning"]},
        "beacon-comfort-co": {
            "label": "On a plan", "heading": "Two visits a year. This is what they look like.",
            "note": "Coils cleaned, the charge checked against the manufacturer's numbers, "
                    "and the small fault found in April instead of July.",
            "tiles": ["coil-cleaning", "gauges", "thermostat"]},
        "trueline-heating-and-air": {
            "label": "Commissioned", "heading": "Set, sealed, charged, signed off.",
            "note": "Every install is levelled, the plenum sealed, the charge set to the "
                    "factory numbers and the permit closed. That is the whole job.",
            "tiles": ["condenser-set", "air-handler", "ductwork"]},
    },
    "restoration": {
        "arbor-restoration-group": {
            "label": "For the plumber and the adjuster",
            "heading": "What we hand back to the people who sent it.",
            "note": "The job as the referring plumber or agent sees it: readings logged "
                    "daily, the room documented at every stage, and a homeowner who "
                    "thinks well of them for the call.",
            "tiles": ["moisture-meter", "air-movers", "rebuild"]},
        "bluewater-restoration": {
            "label": "Documented for the claim",
            "heading": "Every stage, photographed the way the insurer needs it.",
            "note": "The extraction, the readings and the rebuild, each dated and filed "
                    "with the claim. Your deductible is the only invoice you see.",
            "tiles": ["extraction", "moisture-meter", "demo"]},
        "claymore-restoration": {
            "label": "With the adjuster", "heading": "The readings we show the adjuster.",
            "note": "Moisture logged at the same points every day until the structure "
                    "reads dry, and the drying plan the adjuster signs off against.",
            "tiles": ["moisture-meter", "air-movers", "containment"]},
        "keystone-restoration": {
            "label": "Dispatched", "heading": "Crews on site before the paperwork starts.",
            "note": "Extraction begins in the first hour. Who pays is worked out "
                    "afterwards, with the readings to back it.",
            "tiles": ["truck-night", "extraction", "air-movers"]},
        "nightwatch-restoration": {
            "label": "The night call",
            "heading": "What three in the morning looks like from our side.",
            "note": "A truck at the kerb, water out before dawn, and drying equipment "
                    "running by the time you have found the insurer's number.",
            "tiles": ["truck-night", "extraction", "demo"]},
        "rapid-dry-restoration": {
            "label": "Inside the hour", "heading": "Sixty minutes. Then this.",
            "note": "Extraction starts the minute the truck stops. The room is stripped "
                    "to the flood line and drying by the end of the first visit.",
            "tiles": ["extraction", "demo", "air-movers"]},
    },
    "pool-builders": {
        "anvil-bay-pools": {
            "label": "Built to last", "heading": "Steel, gunite, and nothing that floats.",
            "note": "Every shell is steel-tied and shot as one piece. This is what is "
                    "under the water for the next forty years.",
            "tiles": ["excavation", "gunite", "coping"]},
        "blue-harbor-pools": {
            "label": "In your garden", "heading": "The yard before, and the yard after.",
            "note": "Every one of these started as a lawn and a fence. The design is "
                    "drawn into your garden before anything is dug.",
            "tiles": ["outdoor-living", "night-lights", "spa-spillover"]},
        "clearwater-pool-group": {
            "label": "Recent work", "heading": "What the monthly figure is buying.",
            "note": "Gunite, tile, plaster and coping, built to the drawing you signed. "
                    "The number a month covers all of it.",
            "tiles": ["tile-line", "plaster", "coping"]},
        "cold-spring-pools": {
            "label": "Booked in January", "heading": "Dug in March, swimming by June.",
            "note": "The pools that opened this summer were signed in the winter. This "
                    "is the season they were built in.",
            "tiles": ["excavation", "gunite", "night-lights"]},
        "marlin-pool-co": {
            "label": "From the render", "heading": "Built to the drawing, corner for corner.",
            "note": "The spa is where the render put it, the coping is the stone you "
                    "chose on screen, and the lights come on the way they did in the "
                    "walk-through.",
            "tiles": ["spa-spillover", "coping", "night-lights"]},
        "verdant-pools-and-gardens": {
            "label": "The whole garden", "heading": "The pool is a quarter of it.",
            "note": "Patio, planting, kitchen and pool designed as one drawing, so "
                    "nothing is squeezed in afterwards.",
            "tiles": ["outdoor-living", "spa-spillover", "plaster"]},
    },
    "solar": {
        "ansonia-solar": {
            "label": "When the roof is worth it", "heading": "The ones we said yes to.",
            "note": "Every array here went on a roof that earned it: the right pitch, "
                    "the right aspect, no shade. The others got a phone call saying so.",
            "tiles": ["roof-array-detail", "rail-install", "street-of-roofs"]},
        "brightfold-solar": {
            "label": "What the credit paid for", "heading": "The install behind the numbers.",
            "note": "Panels, inverter and battery, itemised on the same sheet as the "
                    "credit and the rebate that paid for part of it.",
            "tiles": ["panels-going-on", "inverter", "battery"]},
        "cedar-line-solar": {
            "label": "How the work gets done", "heading": "Nobody knocked. You asked.",
            "note": "Every roof here belongs to someone who found us, read the number "
                    "and rang. The install looks the same either way; the start of it "
                    "does not.",
            "tiles": ["crew-van", "panels-going-on", "conduit"]},
        "fairhaven-solar": {
            "label": "After the number", "heading": "What happens once you have seen it.",
            "note": "A survey, a design and an install day. The number you saw first is "
                    "the number the crew is working to.",
            "tiles": ["rail-install", "panels-going-on", "inverter"]},
        "halgrove-energy": {
            "label": "Twelve months later", "heading": "The meter, and what is feeding it.",
            "note": "The array on the roof and the inverter in the garage, sized to your "
                    "own twelve months of readings rather than a neighbour's.",
            "tiles": ["inverter", "roof-array-detail", "battery"]},
        "kettle-ridge-solar": {
            "label": "Our crews", "heading": "The same people on every roof.",
            "note": "No subcontractors. The van, the rails and the flashing are all "
                    "ours, and so is the phone number if anything needs looking at.",
            "tiles": ["crew-van", "rail-install", "conduit"]},
    },
    "general-contractors": {
        "bexley-build-group": {
            "label": "In the contract",
            "heading": "Every stage on this page is a line in the schedule.",
            "note": "Demolition, framing, rough-in, close-up and finish, each with a "
                    "date next to it before the deposit is paid.",
            "tiles": ["kitchen-demo", "framing", "finished-kitchen"]},
        "granby-construction": {
            "label": "Permitted and inspected",
            "heading": "The inspections, and what they are inspecting.",
            "note": "Rough-in stays open until the inspector has seen it. The permit "
                    "card is on the door and the photographs are in your folder.",
            "tiles": ["rough-in", "framing", "drywall"]},
        "halverson-build-co": {
            "label": "From the site diary",
            "heading": "Photographs from your site, every single day.",
            "note": "Floors protected, walls open, inspection passed, tile set. The same "
                    "day-by-day record every client gets, so nobody wonders what "
                    "happened on Tuesday.",
            "tiles": ["site-daily", "rough-in", "tile-work"]},
        "marrant-construction": {
            "label": "Itemised", "heading": "What each allowance turned into.",
            "note": "Tile, fixtures, cabinetry and finish carpentry, each against the "
                    "allowance it was quoted at. No adjectives here either.",
            "tiles": ["tile-work", "drywall", "finished-kitchen"]},
        "threshold-builders": {
            "label": "Worth doing", "heading": "The jobs we said yes to.",
            "note": "An addition that changed how the house is lived in, a kitchen that "
                    "was a structural problem first. Big enough to do properly, which "
                    "is the only way we do them.",
            "tiles": ["addition-exterior", "framing", "finished-kitchen"]},
        "whitfield-build-co": {
            "label": "On schedule", "heading": "Week three looks like this.",
            "note": "Demolition in week one, framing in two, rough-in and inspection by "
                    "three. The schedule you were given before the hammer, kept.",
            "tiles": ["kitchen-demo", "framing", "rough-in"]},
    },
    "custom-home-builders": {
        "coulter-and-vane-homes": {
            "label": "The land first", "heading": "Walk it before you draw it.",
            "note": "Every house here started with a survey and a budget that the land "
                    "set. The plan came second.",
            "tiles": ["site-walk", "foundation", "exterior-evening"]},
        "farrow-ridge-builders": {
            "label": "One contract",
            "heading": "Architect, interiors and builder in the same photographs.",
            "note": "The drawings, the finishes and the build were one conversation. "
                    "That is what a single contract looks like on site.",
            "tiles": ["framing-detail", "joinery", "interior-finish"]},
        "kingsmere-build": {
            "label": "Fifteen this year", "heading": "Three of these you can visit.",
            "note": "Every house is somebody's, and three owners a year agree to open "
                    "the door. Ask us which.",
            "tiles": ["exterior-evening", "kitchen", "interior-finish"]},
        "latham-homes": {
            "label": "Priced, then built",
            "heading": "The number held from this stage to this one.",
            "note": "Foundation, framing, finish. The quote was fixed before the first "
                    "of them and was the invoice after the last.",
            "tiles": ["foundation", "framing-detail", "kitchen"]},
        "sable-creek-homes": {
            "label": "Four at a time", "heading": "This year's four.",
            "note": "Two in framing, one in finish, one handed over. There is no fifth, "
                    "which is why these look the way they do.",
            "tiles": ["framing-detail", "joinery", "stone-facade"]},
        "wyndham-custom-homes": {
            "label": "Month by month", "heading": "Eighteen months, four rungs.",
            "note": "Site, structure, envelope, finish. Where each house sits on the "
                    "ladder, and what that stage looks like when you visit.",
            "tiles": ["site-walk", "framing-detail", "stone-facade"]},
    },
    "interior-design": {
        "bramble-and-stone": {
            "label": "Materials first", "heading": "The board before the room.",
            "note": "Every room here began as a sample board. The colour came last, "
                    "and it came from the materials.",
            "tiles": ["material-board", "plaster-wall", "joinery-detail"]},
        "fairholme-design-co": {
            "label": "Every item", "heading": "What the line items turned into.",
            "note": "Each of these rooms is a ledger of specified pieces, ordered, "
                    "tracked and installed. Nothing was bought on the day.",
            "tiles": ["joinery-detail", "upholstery", "install-day"]},
        "ivory-lane-interiors": {
            "label": "Filtered", "heading": "The work, by what you like.",
            "note": "Warm, pared back, layered. Every room here sits under one of the "
                    "chips at the top of the page.",
            "tiles": ["living-room", "styled-shelf", "plaster-wall"]},
        "nocturne-interiors": {
            "label": "After dark", "heading": "Rooms lit like rooms.",
            "note": "Lamps, not downlights. Panelling that holds the light instead of "
                    "bouncing it. The register the daytime photograph never shows.",
            "tiles": ["lighting", "plaster-wall", "living-room"]},
        "sorrel-studio": {
            "label": "Installed by us", "heading": "Install day, and the day after.",
            "note": "We unpack it, place it, hang it and style it. The room is finished "
                    "when we leave, not when the courier does.",
            "tiles": ["install-day", "styled-shelf", "living-room"]},
        "wren-and-alder": {
            "label": "Recent rooms", "heading": "Rooms that look like the people in them.",
            "note": "No two of these share a palette. They share a way of working: the "
                    "materials first, then the people, then the room.",
            "tiles": ["material-board", "living-room", "upholstery"]},
    },
    "architecture": {
        "ansel-row-studio": {
            "label": "Built work", "heading": "Buildings that don't announce themselves.",
            "note": "Six projects, photographed once each and left alone. The thinking "
                    "is on the drawings; this is what it built.",
            "tiles": ["facade", "concrete-detail", "stair",
                      "material-samples", "model", "construction"]},
        "calderwood-architecture": {
            "label": "From the sheet set", "heading": "Drawn to be built from.",
            "note": "The detail on the sheet and the detail on site, side by side. A "
                    "builder can put a tape on either one.",
            "tiles": ["drawing-macro", "construction", "concrete-detail",
                      "stair", "facade", "adaptive-reuse"]},
        "halloway-and-prentiss": {
            "label": "In section", "heading": "Designed in section, not in plan.",
            "note": "The cut through the building is where the light and the structure "
                    "are decided. These are the sections, built.",
            "tiles": ["stair", "civic-interior", "drawing-macro",
                      "concrete-detail", "adaptive-reuse", "facade"]},
        "merton-field-architects": {
            "label": "On site", "heading": "Walk the site with us before you buy it.",
            "note": "Every project started with a site visit before there was a brief. "
                    "The ground, the light and the neighbours came first.",
            "tiles": ["site-visit", "material-samples", "model",
                      "facade", "construction", "concrete-detail"]},
        "ostergaard-architects": {
            "label": "The thinking", "heading": "The drawing is not the work.",
            "note": "Models, sections and samples: the record of decisions, and the "
                    "buildings that came out of them.",
            "tiles": ["model", "drawing-macro", "material-samples",
                      "stair", "civic-interior", "facade"]},
        "pell-and-marchant": {
            "label": "From the index", "heading": "Six of forty-one.",
            "note": "Each one is numbered in the register above. These are the entries "
                    "with the most to show.",
            "tiles": ["adaptive-reuse", "civic-interior", "facade",
                      "stair", "construction", "model"]},
    },
    "luxury-real-estate": {
        "ashcroft-residential": {
            "label": "Sold quietly", "heading": "Never listed. Photographed anyway.",
            "note": "Every one of these changed hands without a portal listing. The "
                    "photography was for the four buyers who saw it, not the four "
                    "thousand.",
            "tiles": ["threshold", "library-room", "garden-path",
                      "entry-hall", "twilight-facade", "bathroom"]},
        "bellamy-estates": {
            "label": "From the prospectus",
            "heading": "Plates from the last three instructions.",
            "note": "Each listing is produced as a printed prospectus. These are its "
                    "plates.",
            "tiles": ["twilight-facade", "entry-hall", "kitchen",
                      "pool-terrace", "library-room", "drone-estate"]},
        "ellery-and-vane": {
            "label": "From the shot list",
            "heading": "Every house gets a film. These are the stills.",
            "note": "The stills are frames from the film, not a separate shoot. The "
                    "shot list is the same for both.",
            "tiles": ["film-crew", "entry-hall", "pool-terrace",
                      "twilight-facade", "kitchen", "garden-path"]},
        "marlowe-and-hart": {
            "label": "The same six streets",
            "heading": "Forty-one years of the same addresses.",
            "note": "Houses we have sold twice, and one we have sold three times. The "
                    "street has not changed; the photography has.",
            "tiles": ["twilight-facade", "threshold", "garden-path",
                      "drone-estate", "entry-hall", "library-room"]},
        "rathmore-and-finch": {
            "label": "The plates", "heading": "Photographed the way the house deserves.",
            "note": "More than six photographs. The first six are here; the rest are "
                    "on the listing page, with the film.",
            "tiles": ["entry-hall", "kitchen", "bathroom",
                      "pool-terrace", "drone-estate", "twilight-facade"]},
        "thornbury-property-group": {
            "label": "What your listings would look like",
            "heading": "For the agents who wish they'd joined sooner.",
            "note": "This is the production every instruction gets, whoever the agent "
                    "is. Your name goes on it.",
            "tiles": ["drone-estate", "kitchen", "pool-terrace",
                      "entry-hall", "film-crew", "twilight-facade"]},
    },
    "dermatology": {
        "colvin-dermatology": {
            "label": "Inside two weeks", "heading": "What the appointment is.",
            "note": "A full-body check with the dermatoscope, the biopsy if it needs "
                    "one, and the lab in the same building.",
            "tiles": ["dermatoscope", "exam-room", "mohs-lab",
                      "instrument-tray", "reception", "skin-macro"]},
        "fenmore-dermatology": {
            "label": "Results, from a person", "heading": "The call, and where it comes from.",
            "note": "The slide is read here. The person who read it rings you.",
            "tiles": ["phone-call", "mohs-lab", "dermatoscope",
                      "exam-room", "instrument-tray", "sunlight-window"]},
        "harrowgate-dermatology": {
            "label": "Two doors", "heading": "Two clinics under one roof.",
            "note": "The medical clinic and the cosmetic clinic, each with its own "
                    "rooms, its own diary and its own front door.",
            "tiles": ["exam-room", "laser-suite", "dermatoscope",
                      "skin-macro", "reception", "pediatric-room"]},
        "larkin-dermatology": {
            "label": "The cosmetic clinic", "heading": "Priced on the page, treated in here.",
            "note": "The laser suite and the treatment rooms the price list refers to.",
            "tiles": ["laser-suite", "skin-macro", "sunlight-window",
                      "reception", "exam-room", "instrument-tray"]},
        "sundial-dermatology": {
            "label": "If it changed", "heading": "What happens when you bring it in.",
            "note": "It is looked at under the dermatoscope the same day, and if it "
                    "needs the lab, it goes to the lab.",
            "tiles": ["dermatoscope", "instrument-tray", "mohs-lab",
                      "exam-room", "phone-call", "reception"]},
        "westbrook-skin-and-surgery": {
            "label": "One appointment",
            "heading": "Diagnosis and removal in the same building.",
            "note": "The Mohs lab is down the corridor from the exam room. The slide "
                    "is read while you wait.",
            "tiles": ["mohs-lab", "instrument-tray", "exam-room",
                      "dermatoscope", "sunlight-window", "pediatric-room"]},
    },
    "med-spas": {
        "bright-hour-med-spa": {
            "label": "Two taps later", "heading": "Where the appointment happens.",
            "note": "Book the slot, walk in, sit down. There is nothing between the "
                    "two.",
            "tiles": ["reception", "treatment-room", "flatlay",
                      "consult-room", "lounge", "evening-window"]},
        "juniper-aesthetics": {
            "label": "Your injector",
            "heading": "The same room, the same hands, every visit.",
            "note": "One treatment room, one injector, and notes that carry from one "
                    "appointment to the next.",
            "tiles": ["injector-hands", "treatment-room", "flatlay",
                      "consult-room", "skincare-shelf", "towel-detail"]},
        "marisol-aesthetics": {
            "label": "Priced on the page", "heading": "What each line on the list buys.",
            "note": "Neurotoxin, filler, laser and skincare, in the rooms and with the "
                    "equipment the price refers to.",
            "tiles": ["flatlay", "laser-device", "skincare-shelf",
                      "treatment-room", "injector-hands", "reception"]},
        "onyx-and-ivory-aesthetics": {
            "label": "The owned grid", "heading": "Our feed, on our page.",
            "note": "The photographs that would otherwise live on someone else's "
                    "platform. The same rooms, the same light, no algorithm.",
            "tiles": ["evening-window", "treatment-room", "flatlay",
                      "towel-detail", "lounge", "injector-hands"]},
        "palmer-row-med-spa": {
            "label": "The menu", "heading": "Read it, then sit down.",
            "note": "Each item on the menu is done in one of these rooms with one of "
                    "these tools. No surprises after the chair.",
            "tiles": ["treatment-room", "laser-device", "flatlay",
                      "skincare-shelf", "lounge", "consult-room"]},
        "verity-skin-and-aesthetics": {
            "label": "On the membership",
            "heading": "What the monthly credit is spent on.",
            "note": "Treatments, products and the review appointment, all against the "
                    "same rolling credit.",
            "tiles": ["skincare-shelf", "injector-hands", "laser-device",
                      "treatment-room", "consult-room", "reception"]},
    },
    "plastic-surgeons": {
        "aldenmore-surgical-aesthetics": {
            "label": "What accredited means",
            "heading": "The suite the certification refers to.",
            "note": "An accredited suite, a dedicated anaesthetist, and instruments "
                    "set out for one operation at a time.",
            "tiles": ["operating-suite", "instrument-tray", "recovery-room",
                      "gloved-hands", "consult-room", "imaging-room"]},
        "calder-aesthetic-surgery": {
            "label": "One suite", "heading": "One surgeon, one team, one room.",
            "note": "The same suite and the same team for every case, which is the "
                    "only way the results stay consistent.",
            "tiles": ["operating-suite", "gloved-hands", "recovery-room",
                      "instrument-tray", "corridor", "consult-room"]},
        "marchetti-plastic-surgery": {
            "label": "Every stage",
            "heading": "Photographed from consultation to recovery.",
            "note": "Imaging before, the suite during, recovery after. The gallery is "
                    "built from the same record.",
            "tiles": ["imaging-room", "operating-suite", "recovery-room",
                      "consult-room", "instrument-tray", "aftercare-kit"]},
        "rothbury-plastic-surgery": {
            "label": "Fifty minutes", "heading": "The room the consultation happens in.",
            "note": "One chair for you, one for the surgeon who will operate, and "
                    "nothing on the table but your file.",
            "tiles": ["consult-room", "waiting-lounge", "imaging-room",
                      "corridor", "recovery-room", "operating-suite"]},
        "sable-plastic-surgery": {
            "label": "Discreet", "heading": "From the door to the room.",
            "note": "A private entrance, a corridor nobody else uses, and a lounge "
                    "with one chair in it.",
            "tiles": ["private-entrance", "corridor", "waiting-lounge",
                      "consult-room", "recovery-room", "aftercare-kit"]},
        "wyeth-plastic-surgery": {
            "label": "Behind the cases", "heading": "Where the cases were done.",
            "note": "The suite, the imaging and the recovery room behind every case in "
                    "the portfolio above.",
            "tiles": ["operating-suite", "imaging-room", "gloved-hands",
                      "instrument-tray", "recovery-room", "consult-room"]},
    },
    "veterinary": {
        "beckett-animal-care": {
            "label": "Priced on the page",
            "heading": "The ordinary things, and where they happen.",
            "note": "Vaccinations, dental, the puppy visit. The rooms the prices at "
                    "the top refer to.",
            "tiles": ["exam-table", "dental", "puppy-visit",
                      "lab", "reception", "pharmacy"]},
        "corner-oak-veterinary": {
            "label": "Without the phone",
            "heading": "Refills, bookings, and the counter that handles them.",
            "note": "Order the refill online and collect it here. Book the slot online "
                    "and walk straight into this room.",
            "tiles": ["pharmacy", "reception", "exam-table",
                      "lab", "cat-room", "dental"]},
        "fernhill-veterinary": {
            "label": "The same team", "heading": "The rooms you will get to know.",
            "note": "One exam room, one vet, one nurse, for the whole ten years.",
            "tiles": ["exam-table", "surgical-suite", "kennel-recovery",
                      "puppy-visit", "cat-room", "reception"]},
        "hollis-animal-hospital": {
            "label": "After hours", "heading": "Where to go at two in the morning.",
            "note": "The light stays on. Surgery, recovery and the lab are ready "
                    "overnight, not just in the daytime.",
            "tiles": ["night-entrance", "surgical-suite", "kennel-recovery",
                      "lab", "exam-table", "reception"]},
        "marlow-veterinary-clinic": {
            "label": "Held for today",
            "heading": "Sick this morning? This is where you come.",
            "note": "Slots held every morning for the animal that was fine last night. "
                    "The exam room and the lab are ready for them.",
            "tiles": ["reception", "exam-table", "lab",
                      "dental", "kennel-recovery", "pharmacy"]},
        "willowbank-animal-hospital": {
            "label": "Yes, new patients", "heading": "The first visit.",
            "note": "The exam room, the scale, and the people who will know your "
                    "animal's name by the second visit.",
            "tiles": ["puppy-visit", "exam-table", "reception",
                      "cat-room", "dental", "surgical-suite"]},
    },
    "accounting-cpas": {
        "ashby-and-kerr-cpas": {
            "label": "What we are waiting on", "heading": "Nothing, usually.",
            "note": "The portal, the folders and the desk where the list gets ticked. "
                    "When the list is empty, the books are closed.",
            "tiles": ["folders", "scanner", "closed-ledger",
                      "quiet-desk", "meeting-room", "signing"]},
        "brandt-and-yoo-cpas": {
            "label": "The intake", "heading": "Where the attachments stop.",
            "note": "Documents come in through the portal, get scanned once, and go "
                    "into a file with your name on it. Never into an inbox.",
            "tiles": ["scanner", "folders", "archive",
                      "quiet-desk", "office-morning", "signing"]},
        "corven-cpa-group": {
            "label": "The year", "heading": "Four conversations, not one filing.",
            "note": "The meeting room gets used every quarter. The filing happens in "
                    "between, and it is the smaller part of the work.",
            "tiles": ["meeting-room", "handshake", "window",
                      "closed-ledger", "quiet-desk", "signing"]},
        "halstead-accounting": {
            "label": "The practice", "heading": "A firm that is choosing.",
            "note": "Small, deliberate, and unhurried. The fee is agreed at this table "
                    "before anything is opened.",
            "tiles": ["meeting-room", "closed-ledger", "office-morning",
                      "folders", "window", "signing"]},
        "latimer-accounting": {
            "label": "Closed by the tenth", "heading": "The month, closed.",
            "note": "The ledger balanced, the folders filed and the desk clear by the "
                    "tenth. Every month looks like this one.",
            "tiles": ["closed-ledger", "folders", "archive",
                      "scanner", "quiet-desk", "office-morning"]},
        "rennick-cpa": {
            "label": "The rhythm", "heading": "Intake, close, review, fee.",
            "note": "Four stations in the year and a room for each. The panic in "
                    "April is what happens to firms without them.",
            "tiles": ["scanner", "closed-ledger", "meeting-room",
                      "signing", "office-morning", "handshake"]},
    },
    "wealth-management": {
        "bracken-and-lowe": {
            "label": "Three conversations", "heading": "The room they happen in.",
            "note": "Two chairs, one table, no screen. The third conversation ends "
                    "with a signature or a handshake and either is fine.",
            "tiles": ["two-chairs", "ruled-sheet", "graphite",
                      "bound-plan", "window-light", "street"]},
        "copeland-fiduciary": {
            "label": "Every dollar", "heading": "Where the ledger is kept.",
            "note": "The fee on one page, the plan bound, the files kept. Nothing here "
                    "that a network could hand to a second firm.",
            "tiles": ["ruled-sheet", "bound-volumes", "bound-plan",
                      "graphite", "two-chairs", "brass-door"]},
        "ferrier-wealth-partners": {
            "label": "The statement", "heading": "Printed, not presented.",
            "note": "The fee schedule on the page above is the same sheet that sits on "
                    "this desk.",
            "tiles": ["ruled-sheet", "window-light", "two-chairs",
                      "bound-plan", "brass-door", "street"]},
        "hartwell-wealth-advisors": {
            "label": "No charts", "heading": "What you have and what it does.",
            "note": "Worked out in pencil, on paper, in a room with a window. Then "
                    "bound and given to you.",
            "tiles": ["graphite", "ruled-sheet", "bound-plan",
                      "window-light", "two-chairs", "family-table"]},
        "ostrander-wealth-counsel": {
            "label": "Sixty-one families", "heading": "The same door for sixty years.",
            "note": "The brass has been polished more often than the name has "
                    "changed. Sixty-one families, and their children, walk through it.",
            "tiles": ["brass-door", "bound-volumes", "street",
                      "two-chairs", "keys", "window-light"]},
        "winslow-family-wealth": {
            "label": "The handover", "heading": "Your children should know this room.",
            "note": "The family table is where the second generation meets us, usually "
                    "years before they need to.",
            "tiles": ["family-table", "keys", "two-chairs",
                      "bound-plan", "brass-door", "graphite"]},
    },
    "recruiting": {
        "brandt-yates-recruitment": {
            "label": "Four, not twelve",
            "heading": "The kind of floor the four have worked.",
            "note": "Every shortlist comes from people who have stood on a floor like "
                    "this one. That is why it is four names and not a stack.",
            "tiles": ["shop-floor", "control-panel", "welding",
                      "precision-parts", "plant-exterior", "interview-room"]},
        "copperfield-industrial-search": {
            "label": "Only industrial", "heading": "The whole sector, and nothing else.",
            "note": "Plants, floors, panels and yards. We do not place accountants, "
                    "and we would not know how.",
            "tiles": ["plant-exterior", "shop-floor", "control-panel",
                      "warehouse", "forklift-yard", "welding"]},
        "ellings-search-group": {
            "label": "What you are screening", "heading": "Where the roles actually are.",
            "note": "The floors, the panels and the yards behind every role we take "
                    "on. If we would not stand there ourselves, we do not fill it.",
            "tiles": ["shop-floor", "hard-hats", "interview-room",
                      "plant-exterior", "control-panel", "warehouse"]},
        "halbrook-search": {
            "label": "The role list", "heading": "The floors the salaries are for.",
            "note": "Every band published, every role on a floor like these. Tap the "
                    "number and a person answers.",
            "tiles": ["control-panel", "precision-parts", "warehouse",
                      "shop-floor", "phone-desk", "welding"]},
        "ironvale-partners": {
            "label": "Two doors", "heading": "Hiring, or being hired.",
            "note": "The interview room and the floor outside it. Whichever door you "
                    "came in, this is where it leads.",
            "tiles": ["interview-room", "shop-floor", "hard-hats",
                      "plant-exterior", "phone-desk", "precision-parts"]},
        "kirkwall-talent": {
            "label": "From the shop floor", "heading": "Apply from here, on your phone.",
            "note": "The floor, the yard, the second shift. One tap from any of them "
                    "and the phone on our desk rings.",
            "tiles": ["shop-floor", "welding", "forklift-yard",
                      "phone-desk", "hard-hats", "warehouse"]},
    },
    "property-management": {
        "amberton-residential": {
            "label": "One door or two hundred", "heading": "Same eight percent.",
            "note": "A single unit and a forty-door portfolio get the same inspection, "
                    "the same work orders and the same statement.",
            "tiles": ["brick-facade", "keys-desk", "unit-ready",
                      "portfolio-aerial", "inspection", "work-order"]},
        "colvert-property-group": {
            "label": "Eight percent", "heading": "What the fee covers.",
            "note": "Leasing, inspection, maintenance and the statement, all in the "
                    "one number at the top of the page.",
            "tiles": ["unit-ready", "work-order", "inspection",
                      "keys-desk", "lockbox", "brick-facade"]},
        "halcombe-management": {
            "label": "Sunday night", "heading": "The call that comes to us.",
            "note": "The van, the plumber and the follow-up. You hear about it on the "
                    "statement, not at nine on a Sunday.",
            "tiles": ["maintenance-van", "work-order", "inspection",
                      "lockbox", "brick-facade", "unit-ready"]},
        "ridgemont-property-services": {
            "label": "No mark-up", "heading": "The invoice, and the work it was for.",
            "note": "The plumber's invoice is the one you see. The photograph of the "
                    "job is attached to it.",
            "tiles": ["work-order", "maintenance-van", "inspection",
                      "unit-ready", "keys-desk", "leasing-office"]},
        "rowan-property-group": {
            "label": "Eight rentals", "heading": "The plumber's first call is now us.",
            "note": "The keys, the van and the office that take the calls a landlord "
                    "with eight doors used to take himself.",
            "tiles": ["keys-desk", "maintenance-van", "leasing-office",
                      "work-order", "showing", "brick-facade"]},
        "weatherby-property-co": {
            "label": "Everything visible", "heading": "What the portal is showing you.",
            "note": "The inspection, the work order, the vacant unit and the showing, "
                    "each photographed and filed where you can see it.",
            "tiles": ["inspection", "work-order", "unit-ready",
                      "showing", "lockbox", "portfolio-aerial"]},
    },
    "cosmetic-dentists": {
        "aldridge-dental": {
            "label": "One plan", "heading": "The rooms the plan is made in.",
            "note": "A scan, a shade match and a conversation. Then one written plan, "
                    "which is the only thing you are asked to decide on.",
            "tiles": ["scanner", "shade-guide", "operatory",
                      "veneer-macro", "lab-bench", "reception"]},
        "belmont-smile-design": {
            "label": "The preview", "heading": "Try it on, in this chair.",
            "note": "The scan and the chairside preview happen at the first visit. The "
                    "porcelain is made afterwards, to match what you saw.",
            "tiles": ["chairside-preview", "scanner", "shade-guide",
                      "veneer-macro", "operatory", "lab-bench"]},
        "callaway-dental-arts": {
            "label": "The free hour", "heading": "What happens in it.",
            "note": "A scan, a shade match, a preview, and the number written down "
                    "before you leave.",
            "tiles": ["scanner", "chairside-preview", "shade-guide",
                      "operatory", "reception", "whitening-tray"]},
        "fairmont-dental-studio": {
            "label": "Scanned, planned, priced", "heading": "Before a tooth is touched.",
            "note": "The scanner, the preview and the bench where the porcelain is "
                    "made. Nothing is drilled until all three have been.",
            "tiles": ["scanner", "chairside-preview", "lab-bench",
                      "veneer-macro", "shade-guide", "operatory"]},
        "havenwood-dental": {
            "label": "For the nervous", "heading": "A calmer room than you remember.",
            "note": "Quiet reception, a treatment room without the smell, and the "
                    "whitening tray you can take home.",
            "tiles": ["reception", "operatory", "whitening-tray",
                      "shade-guide", "chairside-preview", "scanner"]},
        "verano-cosmetic-dentistry": {
            "label": "The work", "heading": "Look through it, then decide.",
            "note": "Porcelain from the bench, the shade matched in daylight, and the "
                    "preview that came before all of it.",
            "tiles": ["veneer-macro", "lab-bench", "shade-guide",
                      "chairside-preview", "scanner", "operatory"]},
    },
}

CSS = """
<style>
  /* Recent-work gallery. Everything here is drawn from the properties the build
     already declares, so the band inherits each design's palette and heading
     face rather than importing a seventh look. */
  .gsw-gal { background: __SURFACE__; color: __TEXT__;
             padding: clamp(38px, 6vw, 74px) 0; }
  .gsw-gal-in { max-width: var(--wrap, 1140px); margin: 0 auto; padding: 0 20px; }
  .gsw-gal-lab { font-size: 13px; letter-spacing: .18em; text-transform: uppercase;
                 font-weight: 600; color: var(--accent); margin: 0 0 14px; }
  .gsw-gal h2 { margin: 0; color: inherit; }
  .gsw-gal-note { color: var(--muted); margin: 14px 0 30px; max-width: 58ch; }
  .gsw-ba { display: grid; grid-template-columns: 1fr 1fr; gap: 2px; margin-bottom: 2px; }
  .gsw-gal-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 2px; }
  .gsw-gal figure { margin: 0; position: relative; overflow: hidden;
                    background: var(--rule, rgba(0,0,0,.1)); }
  .gsw-gal picture { display: block; }
  /* height:auto matters — the width/height attributes are a presentational
     hint, and without this the 1200px hint beats aspect-ratio. */
  .gsw-gal img { display: block; width: 100%; height: auto; aspect-ratio: 4 / 3;
                 object-fit: cover; transition: transform .5s ease; }
  .gsw-gal figure:hover img { transform: scale(1.035); }
  .gsw-gal figcaption { position: absolute; left: 0; bottom: 0;
                        background: __TEXT__; color: __SURFACE__;
                        font-size: 12px; font-weight: 600; letter-spacing: .14em;
                        text-transform: uppercase; padding: 7px 12px; }
  @media (max-width: 720px) {
    .gsw-ba, .gsw-gal-grid { grid-template-columns: 1fr; }
  }
  @media (prefers-reduced-motion: reduce) {
    .gsw-gal img { transition: none; }
    .gsw-gal figure:hover img { transform: none; }
  }
</style>"""


HEX_RE = re.compile(r"#(?:[0-9a-fA-F]{3}){1,2}")


def luminance(hex_colour: str) -> float:
    h = hex_colour.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ground_and_text(src: str) -> tuple[str, str]:
    """Resolve the band's ground and text colour from the build's own tokens.

    `var(--surface)` / `var(--ink)` looked safe and were not: the dark builds
    set --ink and --surface to the same dark and put their text in --text, and
    one build has no --surface at all. Either way the band's heading and the
    tile captions vanished. So the colours are resolved here, at build time,
    from whatever the page actually defines, and written as literals.
    """
    root = re.search(r":root\s*\{(.*?)\}", src, re.S)
    tokens = {}
    if root:
        for decl in root.group(1).split(";"):
            if ":" in decl:
                k, v = decl.split(":", 1)
                tokens[k.strip()] = v.strip()

    def hex_of(*names):
        for n in names:
            m = HEX_RE.fullmatch(tokens.get(n, ""))
            if m:
                return m.group(0)
        return None

    surface = hex_of("--surface", "--bg", "--paper", "--slate", "--panel") or "#FFFFFF"
    text = hex_of("--text")
    if not text:
        ink = hex_of("--ink")
        if ink and abs(luminance(ink) - luminance(surface)) > 0.35:
            text = ink
        else:
            text = "#FFFFFF" if luminance(surface) < 0.45 else "#111111"
    return surface, text


def css_for(src: str) -> str:
    surface, text = ground_and_text(src)
    return CSS.replace("__SURFACE__", surface).replace("__TEXT__", text)


def picture(trade: str, name: str, caption: str, sizes: str, aspect: str) -> str:
    base = f"../_assets/library/{trade}/{name}"
    srcset = ", ".join(f"{base}-{w}.avif {w}w" for w in AVIF_WIDTHS)
    w, h = (1600, 1200) if aspect == "4:3" else (1600, 900)
    return (
        f'<figure><picture>'
        f'<source type="image/avif" srcset="{srcset}" sizes="{sizes}">'
        f'<img src="{base}-{JPEG_WIDTH}.jpg" width="{w}" height="{h}" '
        f'alt="{html.escape(caption)}" loading="lazy" decoding="async">'
        f'</picture><figcaption>{html.escape(caption)}</figcaption></figure>')


def section(trade: str, spec: dict) -> str:
    caps = CAPTIONS[trade]
    # Trades with a real before/after lead with the pair over three tiles; the
    # rest carry six tiles, because a manufactured "before" on a wealth
    # manager's page is worse than none.
    pair = PAIRS.get(trade)
    ba = "".join(
        picture(trade, n, caps[n][0], "(max-width: 720px) 100vw, 50vw", caps[n][1])
        for n in pair) if pair else ""
    tiles = "".join(
        picture(trade, n, caps[n][0], "(max-width: 720px) 100vw, 33vw", caps[n][1])
        for n in spec["tiles"])
    return (
        f'{MARKER}\n<section class="gsw-gal"><div class="gsw-gal-in">'
        f'<p class="gsw-gal-lab">{html.escape(spec["label"])}</p>'
        f'<h2>{html.escape(spec["heading"])}</h2>'
        f'<p class="gsw-gal-note">{html.escape(spec["note"])}</p>'
        + (f'<div class="gsw-ba">{ba}</div>' if pair else "") +
        f'<div class="gsw-gal-grid">{tiles}</div>'
        f'</div></section>\n{END_MARKER}\n')


def patch(page: Path, trade: str, spec: dict, replace: bool) -> str:
    src = page.read_text()
    if MARKER in src:
        if not replace:
            return "already has a gallery"
        src = re.sub(re.escape(MARKER) + r".*?" + re.escape(END_MARKER) + r"\n?",
                     "", src, flags=re.S)
        src = re.sub(r"\n<style>\n  /\* Recent-work gallery.*?</style>", "",
                     src, flags=re.S)

    # Most builds call it `close`; a few compose it, e.g. `sec close`.
    close = CLOSE_RE.search(src)
    if not close:
        return "no closing section to sit above"
    src = src.replace("</head>", css_for(src) + "\n</head>", 1)
    close = CLOSE_RE.search(src)
    src = src[:close.start()] + section(trade, spec) + src[close.start():]
    page.write_text(src)
    return "gallery added"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("trades", nargs="+")
    ap.add_argument("--replace", action="store_true",
                    help="regenerate a gallery that is already present")
    args = ap.parse_args()

    for trade in args.trades:
        sets = SETS.get(trade)
        if not sets:
            print(f"  {trade}: no gallery sets defined")
            continue
        missing = [n for n in CAPTIONS[trade]
                   if not (WORK / "_assets" / "library" / trade /
                           f"{n}-{JPEG_WIDTH}.jpg").exists()]
        if missing:
            sys.exit(f"missing encoded library images: {', '.join(missing)}")
        for slug, spec in sets.items():
            page = WORK / trade / f"{slug}.html"
            status = patch(page, trade, spec, args.replace) if page.exists() \
                else "page missing"
            print(f"  {slug:<34} {status}")


if __name__ == "__main__":
    main()
