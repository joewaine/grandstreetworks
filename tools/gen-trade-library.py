#!/usr/bin/env python3
"""Generate the shared per-trade image library the builds draw their gallery from.

The photography pass gave every build exactly one plate. One photograph is a
placeholder pattern, not a finished site: real trade sites carry a project
gallery, a before/after, process detail and a job-site shot.

The obvious move — a private library per build — is wrong. Six builds x 120
pages of their own photography blows the repo past 100MB, and a trade index page
already loads six full builds in iframes at once. So the split is:

    shared per trade   trade-generic texture, process, detail  <- this file
    unique per build   mark, favicon, social card, hero plate  <- identity kits

Sharing the trade-generic half is invisible to a visitor; the identity half is
what makes the six read as six businesses, and it costs almost nothing.

    python3 tools/gen-trade-library.py roofing
    python3 tools/gen-trade-library.py roofing --only damage-after --force

Needs GEMINI_API_KEY. Same model and negative prompt as cash_rich/gen_heroes.py.
"""

import argparse
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
# Originals are 3-4MB each and are the source, not the deliverable: they live
# beside the hero library in cash_rich, exactly as hero_images does. The repo
# only ever carries the encoded ladder that build-responsive-images.py emits.
OUT = Path.home() / "fractal" / "cash_rich" / "trade_library"
MODEL = "gemini-3-pro-image"
URL = "https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={k}"
SIZE = "2K"

# Same rule the hero library was generated under. Faces stay out: these are
# invented businesses, and inventing identifiable people to staff them is a
# line the set has not crossed. Text stays out because a legible brand name
# baked into a shared image would break the sharing.
NEGATIVE = (
    "No text, no lettering, no signage, no logos, no watermarks, no UI elements. "
    "No recognisable faces. Nothing that reads as stock photography."
)

# `after` names an earlier image in the same set to pass back as a reference, so
# the before/after pair is demonstrably the same house rather than two houses.
LIBRARIES = {
    "cosmetic-dentists": [
        ("smile-a-before",
         "Clinical dental photograph cropped to the lower face only — lips and teeth, no eyes, no nose, no full face; the top edge of the frame sits below the nostrils. The photograph fills the entire frame edge to edge — no border, no letterboxing, no inset. Neutral grey backdrop, flat clinical lighting, unretouched, 100mm macro. "
         "Upper and lower front teeth heavily stained a dull yellow-brown from years of coffee and tea, the colour deepest near the gum line and between the teeth.", "4:3", None),
        ("smile-a-after",
         "The same mouth, the same lips, the same skin, and exactly the same framing, angle and lighting as the reference image, after professional cleaning and whitening: the teeth are now distinctly white, bright and clean — all staining, discolouration and deposit completely gone, surfaces polished and even. The change in shade must be dramatic and obvious at a glance while the teeth still look like real teeth with natural form and a little translucency at the edges. Keep the crop, the lip shape and the lighting identical; change only the teeth. ", "4:3", "smile-a-before"),
        ("smile-b-before",
         "Clinical dental photograph cropped to the lower face only — lips and teeth, no eyes, no nose, no full face; the top edge of the frame sits below the nostrils. The photograph fills the entire frame edge to edge — no border, no letterboxing, no inset. Neutral grey backdrop, flat clinical lighting, unretouched, 100mm macro. "
         "Upper front teeth deeply yellowed with brown nicotine staining and visible hardened tartar along the gum line, plus a gap between the central incisors.", "4:3", None),
        ("smile-b-after",
         "The same mouth, the same lips, the same skin, and exactly the same framing, angle and lighting as the reference image, after professional cleaning and whitening: the teeth are now distinctly white, bright and clean — all staining, discolouration and deposit completely gone, surfaces polished and even. The change in shade must be dramatic and obvious at a glance while the teeth still look like real teeth with natural form and a little translucency at the edges. Keep the crop, the lip shape and the lighting identical; change only the teeth. ", "4:3", "smile-b-before"),
        ("smile-c-before",
         "Clinical dental photograph cropped to the lower face only — lips and teeth, no eyes, no nose, no full face; the top edge of the frame sits below the nostrils. The photograph fills the entire frame edge to edge — no border, no letterboxing, no inset. Neutral grey backdrop, flat clinical lighting, unretouched, 100mm macro. "
         "Upper front teeth discoloured a blotchy yellow-grey with dark staining in the gaps between them, and a chipped corner on one central incisor.", "4:3", None),
        ("smile-c-after",
         "The same mouth, the same lips, the same skin, and exactly the same framing, angle and lighting as the reference image, after professional cleaning and whitening: the teeth are now distinctly white, bright and clean — all staining, discolouration and deposit completely gone, surfaces polished and even. The change in shade must be dramatic and obvious at a glance while the teeth still look like real teeth with natural form and a little translucency at the edges. Keep the crop, the lip shape and the lighting identical; change only the teeth. ", "4:3", "smile-c-before"),
        ("smile-d-before",
         "Clinical dental photograph cropped to the lower face only — lips and teeth, no eyes, no nose, no full face; the top edge of the frame sits below the nostrils. The photograph fills the entire frame edge to edge — no border, no letterboxing, no inset. Neutral grey backdrop, flat clinical lighting, unretouched, 100mm macro. "
         "Upper front teeth yellowed and dulled, the edges worn flat and square from grinding, with brown staining collected in the worn surfaces.", "4:3", None),
        ("smile-d-after",
         "The same mouth, the same lips, the same skin, and exactly the same framing, angle and lighting as the reference image, after professional cleaning and whitening: the teeth are now distinctly white, bright and clean — all staining, discolouration and deposit completely gone, surfaces polished and even. The change in shade must be dramatic and obvious at a glance while the teeth still look like real teeth with natural form and a little translucency at the edges. Keep the crop, the lip shape and the lighting identical; change only the teeth. ", "4:3", "smile-d-before"),
        ("smile-e-before",
         "Clinical dental photograph cropped to the lower face only — lips and teeth, no eyes, no nose, no full face; the top edge of the frame sits below the nostrils. The photograph fills the entire frame edge to edge — no border, no letterboxing, no inset. Neutral grey backdrop, flat clinical lighting, unretouched, 100mm macro. "
         "Upper front teeth badly discoloured, with two dark ageing composite repairs on the central incisors that have gone brown against an already yellow arch.", "4:3", None),
        ("smile-e-after",
         "The same mouth, the same lips, the same skin, and exactly the same framing, angle and lighting as the reference image, after professional cleaning and whitening: the teeth are now distinctly white, bright and clean — all staining, discolouration and deposit completely gone, surfaces polished and even. The change in shade must be dramatic and obvious at a glance while the teeth still look like real teeth with natural form and a little translucency at the edges. Keep the crop, the lip shape and the lighting identical; change only the teeth. ", "4:3", "smile-e-before"),
        ("smile-f-before",
         "Clinical dental photograph cropped to the lower face only — lips and teeth, no eyes, no nose, no full face; the top edge of the frame sits below the nostrils. The photograph fills the entire frame edge to edge — no border, no letterboxing, no inset. Neutral grey backdrop, flat clinical lighting, unretouched, 100mm macro. "
         "Upper front teeth stained an uneven grey-brown with dark horizontal banding through the enamel and heavy deposit along the gum line.", "4:3", None),
        ("smile-f-after",
         "The same mouth, the same lips, the same skin, and exactly the same framing, angle and lighting as the reference image, after professional cleaning and whitening: the teeth are now distinctly white, bright and clean — all staining, discolouration and deposit completely gone, surfaces polished and even. The change in shade must be dramatic and obvious at a glance while the teeth still look like real teeth with natural form and a little translucency at the edges. Keep the crop, the lip shape and the lighting identical; change only the teeth. ", "4:3", "smile-f-before"),
        ("chairside-preview",
         "Documentary photograph of a dental surgery: a large monitor on an articulated "
         "arm showing an abstract, unreadable three-dimensional render, a clinician's "
         "gloved hands at the edge of frame, no face. Calm oak and off-white room, "
         "daylight from the left. 35mm, shallow depth of field.", "4:3", None),
        ("shade-guide",
         "Close documentary photograph of a porcelain shade guide fanned out on a clean "
         "white worktop beside a small mirror, tabs graded from warm to bright. Soft "
         "daylight, strong shallow focus on the middle tabs. 100mm macro.", "4:3", None),
        # The gallery band's six, added after the smile pairs; those stay with
        # the compare slider.
        ("operatory",
         "Photograph of a bright, calm cosmetic dentistry treatment room: a plain "
         "modern chair in pale upholstery, an overhead light, a window with a white "
         "blind, clean surfaces. No people, no screens with text, no branding. 35mm.",
         "4:3", None),
        ("scanner",
         "Close photograph of a gloved hand holding an intraoral scanner wand above a "
         "tray, the small screen beside it showing only a plain 3D tooth model with "
         "no text or numbers, no face in frame. Clinical light. 85mm.", "4:3", None),
        ("veneer-macro",
         "Macro photograph of a single porcelain veneer standing on a matte black "
         "surface, translucent at the edge, lit from the side. No text, no people. "
         "100mm macro.", "4:3", None),
        ("whitening-tray",
         "Close photograph of a clear custom whitening tray seated on a white dental "
         "model of an upper arch, on a clean worktop. No text, no people. Soft "
         "daylight. 85mm.", "4:3", None),
        ("lab-bench",
         "Photograph of a dental technician's bench: gloved hands holding a plaster "
         "model with a fine brush, a porcelain furnace behind, tools in a row, no "
         "face in frame. Warm work light. 50mm.", "4:3", None),
        ("reception",
         "Photograph of a calm dental practice reception: pale oak counter, a plant, "
         "two linen chairs, morning light. No people, no signage, no text. 35mm.",
         "4:3", None),
    ],
    "roofing": [
        ("tear-off",
         "Documentary photograph of a roofing crew stripping old asphalt shingles from "
         "a suburban roof, seen from behind and above so no face is in frame. Torn felt, "
         "a flat bar, stacked debris. Overcast midday light, honest and unstyled. 35mm.",
         "4:3", None),
        ("underlayment",
         "Documentary photograph of synthetic roofing underlayment rolled out over fresh "
         "plywood decking, one course half-unrolled, cap nails in a neat line. Bright "
         "diffuse daylight, strong texture. 50mm, slight top-down angle.", "4:3", None),
        ("courses",
         "Close documentary photograph of new architectural asphalt shingles being laid "
         "in courses, a nail gun and one gloved hand at the edge of frame, no face. "
         "Raking afternoon light picking out the granule texture. 50mm.", "4:3", None),
        ("ridge-vent",
         "Close documentary photograph of a finished ridge line on an asphalt shingle "
         "roof — ridge cap shingles over a low-profile ridge vent, clean straight run "
         "against open sky. Late afternoon light. 85mm compression.", "4:3", None),
        ("flashing",
         "Close documentary photograph of new step flashing where an asphalt shingle "
         "roof meets a brick chimney, counter-flashing tucked into the mortar joint, "
         "sealant line neat. Hard directional sun. 85mm, shallow depth of field.",
         "4:3", None),
        ("drip-edge",
         "Close documentary photograph of a new aluminium drip edge and seamless gutter "
         "along a roof eave, shingle overhang crisp above it, soffit below in shadow. "
         "Clear morning light. 50mm.", "4:3", None),
        ("damage-before",
         "Documentary photograph of a storm-damaged suburban roof: a patch of asphalt "
         "shingles torn away exposing dark underlayment, lifted tabs around it, a blue "
         "tarp weighted at one edge. Flat grey light after rain, wet shingles. 35mm, "
         "three-quarter view of the roof plane from a neighbouring height.", "4:3", None),
        ("damage-after",
         "Documentary photograph of the same house and the same roof plane from the same "
         "angle and distance, now fully re-shingled: continuous new architectural "
         "shingles, no tarp, no missing tabs, clean ridge. Keep the house, the roof "
         "geometry, the surroundings and the framing identical to the reference image; "
         "change only the roof condition and give it clear light after the storm.",
         "4:3", "damage-before"),
        ("jobsite",
         "Documentary photograph of a tidy residential roofing job site: a pickup truck "
         "with ladders on the rack, a small debris container on plywood protecting the "
         "driveway, bundles of shingles stacked. No people in frame. Early morning, long "
         "shadows. 35mm.", "4:3", None),
        ("finished-home",
         "Photograph of a well-kept suburban two-storey house with a newly finished "
         "architectural shingle roof, shot from the front garden. Warm late-afternoon "
         "light, deep blue sky, mature planting. Wide establishing view. 35mm.",
         "16:9", None),
    ],
    "hvac": [
        ("condenser-set",
         "Documentary photograph of a brand-new residential outdoor air-conditioning "
         "condenser unit set level on a fresh composite pad beside a house wall, the "
         "refrigerant lineset neatly insulated and run up the wall, a new disconnect box "
         "above it. Clean mulch, no people. Bright diffuse daylight. 35mm, three-quarter "
         "view.", "4:3", None),
        ("air-handler",
         "Documentary photograph of a newly installed residential air handler and furnace "
         "in a tidy basement utility space: sheet-metal plenum with sealed seams, a new "
         "filter rack, flexible connector, condensate line run to a drain. No people. "
         "Even work-light illumination. 35mm, slight low angle.", "4:3", None),
        ("ductwork",
         "Close documentary photograph of rigid sheet-metal duct joints in a residential "
         "attic freshly sealed with grey mastic and foil tape, the brush strokes still "
         "visible, insulation batts around. No people. Headlamp and daylight from a "
         "gable vent. 50mm.", "4:3", None),
        ("attic-run",
         "Documentary photograph of insulated flexible ductwork in a residential attic "
         "newly installed: straight runs, properly strapped to rafters, no crushed or "
         "sagging sections, a sealed metal takeoff at the trunk. No people. Work light "
         "and a little daylight. 35mm.", "4:3", None),
        ("thermostat",
         "Close documentary photograph of a modern smart thermostat freshly mounted on "
         "a plain interior wall, screen glowing softly showing only a simple temperature "
         "graphic and no words or numbers, the wall plate clean and level. Warm interior "
         "light. 85mm, shallow depth of field.", "4:3", None),
        ("gauges",
         "Close documentary photograph of a refrigerant manifold gauge set hooked to the "
         "service valves of an outdoor condenser, one gloved hand on a knob at the edge "
         "of frame, no face. Hard afternoon sun, strong shadows. 50mm.", "4:3", None),
        ("coil-cleaning",
         "Close documentary photograph of a technician's gloved hands straightening the "
         "aluminium fins of an outdoor condenser coil with a fin comb, the cleaned fins "
         "bright against the dirty section still to do, no face in frame. Overcast "
         "daylight. 85mm, shallow depth of field.", "4:3", None),
        ("van-jobsite",
         "Documentary photograph of a plain white American full-size cargo van, Ford "
         "Transit shape, left-hand drive, no lettering, parked at the curb of a US "
         "suburban street outside a clapboard house at dusk, sliding side door open "
         "showing shelves of tools and parts, the house's porch light on. No people. "
         "Blue hour with warm window light. 35mm.", "4:3", None),
        ("unit-before",
         "Documentary photograph of an old, failing residential outdoor air-conditioning "
         "condenser unit beside a house wall: rust streaks on the cabinet, bent and "
         "clogged coil fins, a cracked and sunken concrete pad, weeds grown up around it, "
         "the lineset insulation perished and hanging off. Flat overcast light. 35mm, "
         "three-quarter view from standing height.", "4:3", None),
        ("unit-after",
         "Edit the reference photograph. Reproduce it exactly — the same house, the "
         "same siding colour and window, the same camera position, angle, lens and "
         "framing, the same ground and background — and change only one thing: the "
         "old rusted condenser and its cracked pad are gone, replaced in the identical "
         "position by a brand-new condenser on a fresh level pad with a new insulated "
         "lineset, the weeds cleared and the ground raked. Keep the overcast light. A "
         "viewer flicking between the two images must see the same scene with only the "
         "unit and its pad changed; the difference must be obvious side by side while "
         "staying believable.", "4:3", "unit-before"),
    ],
    "restoration": [
        ("extraction",
         "Documentary photograph of water extraction in a flooded suburban living room: "
         "a wide extraction wand on soaked carpet, a thick hose running out through the "
         "doorway, an inch of standing water reflecting the window. No people. Flat "
         "daylight through wet glass. 35mm.", "4:3", None),
        ("air-movers",
         "Documentary photograph of a room stripped for drying: a row of centrifugal "
         "air movers angled along the baseboards, a large dehumidifier in the corner, "
         "carpet pulled back and baseboards removed, plain unbranded equipment. No "
         "people. Work-light illumination. 35mm.", "4:3", None),
        ("moisture-meter",
         "Close documentary photograph of a gloved hand pressing a pin-type moisture "
         "meter into painted drywall near the floor, the meter a plain grey instrument "
         "with its display turned away from the camera, a pencilled tide line visible "
         "on the wall. No face. Torchlight and daylight. 85mm, shallow depth of field.",
         "4:3", None),
        ("containment",
         "Documentary photograph of a mould remediation containment: a wall of clear "
         "polythene sheeting with a zipper door, taped to the ceiling and floor, a "
         "negative-air machine's duct running through it, the room beyond hazy. No "
         "people. Cool work-light illumination. 35mm.", "4:3", None),
        ("smoke-clean",
         "Close documentary photograph of a fire-damaged interior wall being cleaned: "
         "the left half still black with soot, the right half wiped back to pale paint, "
         "a chemical sponge in a gloved hand at the boundary. No face. Raking light. "
         "50mm.", "4:3", None),
        ("demo",
         "Documentary photograph of a flooded room cut at the flood line: drywall "
         "removed to two feet above the floor along the whole wall, studs and the sill "
         "plate exposed, the cut edge clean and straight, debris bagged. No people. "
         "Daylight from the window. 35mm.", "4:3", None),
        ("truck-night",
         "Documentary photograph of a plain white American box truck with no lettering "
         "parked outside a suburban house at night, rear door up, drying equipment "
         "stacked inside, the house's lights on in every window. No people. Street "
         "light and porch light, wet road. 35mm.", "4:3", None),
        ("rebuild",
         "Documentary photograph of a room in rebuild after water damage: new drywall "
         "on the lower wall taped and mudded but unpainted, new baseboard leaning ready, "
         "subfloor clean and dry, a work light on a stand. No people. 35mm.",
         "4:3", None),
        ("flood-before",
         "Documentary photograph of a suburban family living room after a burst pipe: "
         "two inches of standing water across the floor, the carpet dark and soaked, "
         "the bottom of a sofa and bookcase sitting in water, a rug floating at one "
         "edge, the wall stained at the tide line. No people. Grey daylight from a "
         "window on the left. 35mm, standing height from the doorway.", "4:3", None),
        ("flood-after",
         "Edit the reference photograph. Reproduce it exactly — the same room, the "
         "same window on the left, the same sofa and bookcase in the same positions, "
         "the same camera position, angle and framing — and change only the damage: "
         "the water is gone, the floor is new dry oak boards, the wall is repainted "
         "clean to the skirting, the rug is dry and flat. Warm afternoon daylight from "
         "the same window. A viewer flicking between the two must see the same room "
         "put right.", "4:3", "flood-before"),
    ],
    "pool-builders": [
        ("excavation",
         "Documentary photograph of a residential pool excavation: the dug shape in "
         "a suburban backyard with a cage of tied steel rebar following the walls and "
         "the deep end, wooden forms at the bond beam, spoil heaped to one side. No "
         "people. Bright overcast daylight. 35mm, from the shallow end.", "4:3", None),
        ("gunite",
         "Documentary photograph of a freshly shot gunite pool shell, the grey concrete "
         "surface still rough and damp, steps and a bench formed in it, a hose lying on "
         "the deck, a suburban fence behind. No people. Late afternoon light. 35mm.",
         "4:3", None),
        ("tile-line",
         "Close documentary photograph of gloved hands setting glass mosaic waterline "
         "tile along the bond beam of a plastered pool, a notched trowel and a bucket "
         "of thinset beside them, no face in frame. Hard midday sun. 50mm.",
         "4:3", None),
        ("plaster",
         "Close documentary photograph of a pool plaster crew's trowel smoothing fresh "
         "white plaster across a pool floor, seen from above so only the trowel and a "
         "forearm are in frame, the surface wet and mirror-smooth behind it. Bright "
         "daylight. 50mm.", "4:3", None),
        ("coping",
         "Close documentary photograph of travertine coping at a pool edge, the stone "
         "overhanging clear blue water, a line of glass waterline tile beneath it, "
         "caustic light ripples on the pool wall. No people. Afternoon sun. 85mm.",
         "4:3", None),
        ("spa-spillover",
         "Photograph of a raised stone spa spilling in a smooth sheet into a gunite "
         "pool at dusk, the spa lit from within, steam rising, the pool water still "
         "and reflecting a deep blue sky. No people. Blue hour. 35mm.", "4:3", None),
        ("outdoor-living",
         "Photograph of a finished backyard: a covered outdoor kitchen with a stone "
         "counter and a plain stainless grill, a pergola, a seating area, and the "
         "corner of a pool with a fire feature, all in warm evening light. No people. "
         "35mm, wide.", "4:3", None),
        ("night-lights",
         "Photograph of a residential gunite pool at night, the underwater lights on "
         "and turning the water a glowing aqua, dark planting and a lit house behind "
         "it. No people. Long exposure look. 35mm.", "4:3", None),
        ("yard-before",
         "Documentary photograph of a plain suburban backyard before any work: a flat "
         "lawn patchy in places, a wooden fence along the back, a concrete patio slab "
         "by the house on the left, a single tree at the right corner. No people. Flat "
         "overcast daylight. 35mm, from the back door at standing height.",
         "4:3", None),
        ("yard-after",
         "Edit the reference photograph. Reproduce it exactly — the same fence along "
         "the back, the same tree at the right corner, the same house edge on the "
         "left, the same camera position, angle and framing — and change only the "
         "yard: a rectangular gunite pool with stone coping and a paved deck now fills "
         "the lawn, with low planting along the fence. Warm clear late-afternoon "
         "light. A viewer flicking between the two must see the same yard with the "
         "pool built.", "4:3", "yard-before"),
    ],
    "solar": [
        ("rail-install",
         "Close documentary photograph of gloved hands bolting an aluminium mounting "
         "rail to a flashed foot on an asphalt shingle roof, a torque wrench on the "
         "bolt, no face in frame. Clear morning light. 50mm.", "4:3", None),
        ("panels-going-on",
         "Documentary photograph from above and behind of two installers in plain "
         "harnesses lifting a solar panel onto a rail system on a suburban roof, their "
         "backs to the camera so no face is visible, half the array already fitted. "
         "Bright midday light. 35mm.", "4:3", None),
        ("inverter",
         "Documentary photograph of a plain grey unbranded string inverter and an AC "
         "disconnect mounted on a garage wall, metal conduit run neatly between them "
         "and up to the ceiling, the wall clean. No people. Even garage light. 35mm.",
         "4:3", None),
        ("battery",
         "Documentary photograph of a plain white unbranded wall-mounted home battery "
         "in a tidy garage, conduit running to a backup gateway beside it, a bicycle "
         "leaning in the corner. No people. Daylight from the open garage door. 35mm.",
         "4:3", None),
        ("conduit",
         "Close documentary photograph of a run of grey electrical conduit descending "
         "an exterior house wall from the roofline to a junction box, straight and "
         "evenly clipped, painted to match the siding. No people. Hard afternoon sun. "
         "85mm.", "4:3", None),
        ("roof-array-detail",
         "Close documentary photograph of the edge of a solar array on an asphalt "
         "shingle roof: the panel frame, the rail end, and the flashed mounting foot "
         "tucked under the shingle course, everything clean and square. No people. "
         "Raking evening light. 85mm.", "4:3", None),
        ("street-of-roofs",
         "Aerial photograph of an American suburban street with six houses carrying "
         "rooftop solar arrays of different sizes, tree-lined, cars in driveways. No "
         "people visible. Clear midday sun. Drone, moderate height.", "4:3", None),
        ("crew-van",
         "Documentary photograph of a plain white American cargo van with no lettering, "
         "ladder rack loaded, parked in a suburban driveway at first light with solar "
         "panels stacked on a pallet beside it. No people. Cool morning light. 35mm.",
         "4:3", None),
        ("roof-before",
         "Documentary photograph of a plain south-facing asphalt shingle roof on a "
         "two-storey American suburban house, seen from the street corner, the roof "
         "empty, a chimney at the left end, a clear sky. No people. Morning light. "
         "35mm, from across the road.", "4:3", None),
        ("roof-after",
         "Edit the reference photograph. Reproduce it exactly — the same house, the "
         "same roof, the chimney at the left end, the same camera position, angle and "
         "framing, the same sky — and change only one thing: a neat rectangular array "
         "of black solar panels now covers most of the main roof plane. A viewer "
         "flicking between the two must see the same house with the panels added.",
         "4:3", "roof-before"),
    ],
    "general-contractors": [
        ("kitchen-demo",
         "Documentary photograph of a kitchen gutted to the studs: cabinets and "
         "drywall gone, bare framing and old wiring exposed, the subfloor covered with "
         "protective board, a dust barrier of taped plastic across the far doorway. No "
         "people. Daylight from the window. 35mm.", "4:3", None),
        ("framing",
         "Documentary photograph of new wall framing in a renovation: a wide opening "
         "cut between two rooms with a new laminated header and jack studs, fresh pale "
         "lumber against the older grey framing, sawdust on the floor. No people. Work "
         "light and daylight. 35mm.", "4:3", None),
        ("rough-in",
         "Documentary photograph of a renovation at rough-in: new copper and PEX "
         "plumbing and electrical boxes with cable run neatly through open stud bays, "
         "ready for inspection, nothing closed up yet. No people. Even light. 35mm.",
         "4:3", None),
        ("drywall",
         "Documentary photograph of a freshly hung and taped drywall room, the joints "
         "mudded and sanded, corner bead crisp, floor protected with paper. No people. "
         "Soft daylight. 35mm.", "4:3", None),
        ("tile-work",
         "Close documentary photograph of gloved hands setting a large-format porcelain "
         "tile on a bathroom floor with a levelling clip system, a trowel beside them, "
         "no face in frame. Work light. 50mm.", "4:3", None),
        ("site-daily",
         "Documentary photograph of a renovation site at the end of the day: floors "
         "covered with plain unprinted brown protection board with no lettering, tools "
         "packed in a corner, the dust barrier zipped, a broom leaning by the door. No "
         "people. Late light through a window. 35mm.", "4:3", None),
        ("finished-kitchen",
         "Photograph of a newly finished kitchen: painted shaker cabinets, a quartz "
         "island, a plain range, a tiled backsplash, oak floor, morning light through a "
         "large window. No people, no text. 35mm, wide.", "4:3", None),
        ("addition-exterior",
         "Documentary photograph of a new rear addition framed and sheathed against an "
         "existing suburban house, the new pale OSB and plain unprinted white house "
         "wrap with no lettering or logos beside the old siding, a roof tied in, a "
         "small skip in the yard. No people. Clear daylight. 35mm.", "4:3", None),
        ("kitchen-before",
         "Documentary photograph of a dated kitchen before renovation: dark worn oak "
         "cabinets, laminate counters, a dropped ceiling with a fluorescent box light, "
         "vinyl floor, a window over the sink on the far wall. No people. Flat "
         "daylight. 35mm, from the doorway at standing height.", "4:3", None),
        ("kitchen-after",
         "Edit the reference photograph. Reproduce it exactly — the same room, the "
         "same window over the sink on the far wall, the same camera position, angle "
         "and framing — and change only the kitchen: the cabinets are now painted "
         "shaker in a soft white, the counters quartz, the dropped ceiling gone with "
         "recessed lights in a flat ceiling, the floor oak. Warm daylight from the "
         "same window. A viewer flicking between the two must see the same room "
         "renovated.", "4:3", "kitchen-before"),
    ],
    "custom-home-builders": [
        ("site-walk",
         "Documentary photograph of a wooded acreage building lot at first light: "
         "survey stakes with orange flagging tape marking a house footprint in long "
         "grass, mature trees behind, mist low on the ground. No people. 35mm.",
         "4:3", None),
        ("foundation",
         "Documentary photograph of a large poured concrete foundation with the forms "
         "just stripped, the walls clean and sharp, anchor bolts along the top, gravel "
         "and a stack of lumber beside it on a cleared lot. No people. Clear morning "
         "light. 35mm.", "4:3", None),
        ("framing-detail",
         "Documentary photograph inside a large house at framing: tall window openings "
         "framed in engineered lumber toward a view of trees, a cathedral ceiling of "
         "exposed rafters, sawdust on the subfloor. No people. Afternoon light through "
         "the openings. 35mm.", "4:3", None),
        ("joinery",
         "Close documentary photograph of a finish carpenter's hands fitting a mitred "
         "white oak casing joint with a block plane, the shaving curling, no face in "
         "frame. Window light. 85mm, shallow depth of field.", "4:3", None),
        ("stone-facade",
         "Close documentary photograph of a mason's gloved hands setting a course of "
         "natural split-face limestone veneer on a house exterior, a level and a bucket "
         "of mortar beside them, no face in frame. Bright overcast. 50mm.",
         "4:3", None),
        ("interior-finish",
         "Photograph of a finished great room in a custom home: white oak floor, a "
         "stone fireplace to the ceiling, tall steel-framed windows onto woodland, "
         "plain furniture. No people, no text. Soft afternoon light. 35mm, wide.",
         "4:3", None),
        ("kitchen",
         "Photograph of a finished estate kitchen: a long marble island, inset rift "
         "oak cabinetry, a plain range with a plaster hood, tall windows. No people, "
         "no text. Morning light. 35mm.", "4:3", None),
        ("exterior-evening",
         "Photograph of a finished custom house at dusk from the end of a gravel "
         "drive: stone and dark timber, long low roofline, every window warmly lit, "
         "mature trees behind. No people. Blue hour. 35mm.", "4:3", None),
        ("house-framing",
         "Documentary photograph of a large custom house framed and sheathed in pale "
         "OSB, the roof trusses on but no roofing, from the end of the driveway at a "
         "three-quarter angle, a line of mature oaks behind on the right and an open "
         "meadow to the left. No people. Clear midday light. 35mm.", "4:3", None),
        ("house-finished",
         "Edit the reference photograph, changing as little as possible. Keep the "
         "camera exactly where it is: the same angle, the same distance, the same "
         "framing, the same oaks behind on the right and the same meadow on the left. "
         "Keep the house's exact silhouette: every gable, every roof pitch, every "
         "window and door opening stays in precisely the same place and size. Only "
         "the surfaces change: the OSB is now clad in stone and dark-stained cedar, "
         "the trusses are now under a standing-seam metal roof, the openings now hold "
         "glass, the bare ground is now a gravel drive and lawn. Warm late-afternoon "
         "light. Someone flicking between the two images must see one house, framed "
         "and then finished, with nothing moved.", "4:3", "house-framing"),
    ],
    "interior-design": [
        ("material-board",
         "Overhead photograph of a designer's sample board on a pale linen surface: "
         "a white oak veneer chip, a slab of pink limewash plaster, a swatch of moss "
         "green velvet, an unlacquered brass pull, a fold of oatmeal linen, a black "
         "lacquer chip. No text, no labels, no people. Soft window light. 50mm.",
         "4:3", None),
        ("plaster-wall",
         "Close photograph of a limewash plaster wall in a soft clay colour, the "
         "cloudy texture caught by low afternoon light from a window at the left, a "
         "corner of an oak-framed chair at the bottom edge. No people. 85mm.",
         "4:3", None),
        ("upholstery",
         "Documentary photograph in an upholstery workroom: a wingback chair frame "
         "half covered in a bouclé fabric, a hand with a tack hammer at the edge of "
         "frame, bolts of fabric behind, no face. Daylight from a high window. 50mm.",
         "4:3", None),
        ("joinery-detail",
         "Close photograph of a built-in cabinet in white oak: a reeded door panel, an "
         "unlacquered brass edge pull, a shadow gap to the plaster wall. No people, no "
         "text. Side light. 85mm, shallow depth of field.", "4:3", None),
        ("lighting",
         "Photograph of a panelled living-room wall at night lit only by a brass "
         "picture light and a low table lamp, a pool of warm light on dark green "
         "panelling, the rest of the room falling to shadow. No people. 35mm.",
         "4:3", None),
        ("install-day",
         "Documentary photograph of a living room on install day: furniture still "
         "under moving blankets, a rolled rug, framed art leaning against the wall in "
         "bubble wrap, one lamp already placed and lit. No people, no text. Daylight. "
         "35mm.", "4:3", None),
        ("styled-shelf",
         "Photograph of a styled built-in bookcase: books with plain unlettered cloth "
         "spines in muted colours, a ceramic vessel, a small framed drawing, a brass "
         "object, arranged with air between them. No text anywhere. Soft light. 50mm.",
         "4:3", None),
        ("living-room",
         "Photograph of a finished living room by an interior designer: a linen sofa, "
         "a vintage oak table, a wool rug, limewash walls, a large window with sheer "
         "curtains, layered lamps. No people, no text. Late morning light. 35mm, wide.",
         "4:3", None),
        ("room-before",
         "Documentary photograph of an empty suburban living room before design work: "
         "flat beige walls, a single ceiling downlight, a bare grey carpet, a large "
         "window with vertical blinds on the far wall, a radiator beneath it. No "
         "people. Flat daylight. 35mm, from the doorway at standing height.",
         "4:3", None),
        ("room-after",
         "Edit the reference photograph. Reproduce it exactly — the same room, the "
         "same window on the far wall, the same radiator beneath it, the same camera "
         "position, angle and framing — and change only the design: the walls are now "
         "a warm limewash plaster, the carpet replaced by a wide oak floor and a wool "
         "rug, the blinds replaced by full linen curtains, a linen sofa and an oak "
         "table placed, two lamps lit. Warm daylight from the same window. A viewer "
         "flicking between the two must see the same room designed.",
         "4:3", "room-before"),
    ],
    "architecture": [
        ("model",
         "Close photograph of hands adjusting a white card and basswood study model "
         "of a house on a drafting table, a scalpel and offcuts beside it, no face in "
         "frame. North daylight. 85mm, shallow depth of field.", "4:3", None),
        ("drawing-macro",
         "Macro photograph of an architectural section drawing in pencil on tracing "
         "paper: wall lines, a roof pitch, hatched ground, a drafting pencil resting on "
         "it. Lines only, no lettering, no dimensions, no numbers. Raking window light. "
         "100mm macro.", "4:3", None),
        ("concrete-detail",
         "Close photograph of a built architectural detail: board-formed concrete "
         "meeting a white oak window frame, the grain of the boards printed into the "
         "concrete, a shadow gap between the two. No people. Low sun. 85mm.",
         "4:3", None),
        ("stair",
         "Photograph of a built interior stair in a private house: folded blackened "
         "steel treads, a plain oak handrail, a tall slot window washing the wall with "
         "light. No people, no text. 35mm.", "4:3", None),
        ("site-visit",
         "Documentary photograph of a sloping rural building site at dawn: long wet "
         "grass, a line of survey pegs, a dry-stone wall, a view down a valley, a roll "
         "of drawings left on the wall with no visible text. No people. 35mm.",
         "4:3", None),
        ("facade",
         "Photograph of a completed modern private house: a long low form in "
         "charcoal brick and timber under a single-pitch zinc roof, set into a meadow "
         "with a copse behind. No people, no text. Soft evening light. 35mm.",
         "4:3", None),
        ("adaptive-reuse",
         "Photograph inside a converted brick warehouse: original cast-iron columns "
         "and timber beams, with a new blackened-steel mezzanine and a glazed wall "
         "inserted. No people, no signage. Daylight through tall arched windows. 35mm.",
         "4:3", None),
        ("civic-interior",
         "Photograph of a civic reading hall: a tall timber-lattice ceiling, "
         "clerestory daylight, long oak tables, plain shelving. No people, no signage, "
         "no text. 35mm, wide.", "4:3", None),
        ("material-samples",
         "Overhead photograph of material samples on a concrete table: a handmade "
         "brick, a zinc offcut, a block of oak, a slab of lime render, a piece of "
         "corten steel. No text, no labels, no people. Even daylight. 50mm.",
         "4:3", None),
        ("construction",
         "Documentary photograph of a house under construction where the architecture "
         "is visible in the structure: a glulam timber frame and exposed steel "
         "connections, the roof deck on, scaffolding to one side. No people, no "
         "signage. Clear daylight. 35mm.", "4:3", None),
    ],
    "luxury-real-estate": [
        ("entry-hall",
         "Photograph of the entrance hall of a grand estate house: a sweeping stone "
         "staircase, a marble floor, a tall window on the landing, a single console. "
         "No people, no text. Morning light. 35mm, wide.", "4:3", None),
        ("kitchen",
         "Photograph of an estate kitchen at twilight: a marble island, painted "
         "cabinetry, brass hardware, pendant lights on, French doors open to a terrace "
         "with the sky going blue. No people, no text. 35mm.", "4:3", None),
        ("pool-terrace",
         "Photograph of a stone terrace and swimming pool behind a large house at "
         "dusk, the pool lit, loungers under a pergola, clipped hedges. No people. "
         "Blue hour. 35mm.", "4:3", None),
        ("drone-estate",
         "Aerial photograph of a large estate house with formal gardens, a long tree-"
         "lined drive, a pool and parkland beyond, in soft evening light. No people. "
         "Drone, moderate height.", "4:3", None),
        ("library-room",
         "Photograph of a panelled study in a fine house: floor-to-ceiling walnut "
         "shelves with books whose spines carry no legible lettering, a leather chair, "
         "a fireplace, a tall window. No people, no text. Afternoon light. 35mm.",
         "4:3", None),
        ("garden-path",
         "Photograph of a formal garden at a private estate: a gravel path between "
         "clipped box parterres, a stone urn, a glimpse of the house's facade beyond. "
         "No people. Golden hour. 50mm.", "4:3", None),
        ("bathroom",
         "Photograph of a principal bathroom: a freestanding stone bath under a tall "
         "sash window, book-matched marble walls, unlacquered brass taps. No people, "
         "no text. Soft daylight. 35mm.", "4:3", None),
        ("film-crew",
         "Documentary photograph of a cinema camera on a motorised slider set up in a "
         "long hallway of a grand house, a monitor beside it showing only a blurred "
         "image, no people in frame. Window light. 35mm.", "4:3", None),
        ("threshold",
         "Close photograph of the front door of a fine house: a deep black painted "
         "door, an unlacquered brass knocker and handle, stone steps, a boxwood in a "
         "lead planter. No numbers, no text, no people. Morning light. 85mm.",
         "4:3", None),
        ("twilight-facade",
         "Photograph of a large stone estate house from the drive at twilight, every "
         "window lit, the sky deep blue, gravel in the foreground. No people, no text. "
         "35mm.", "4:3", None),
    ],
    "dermatology": [
        ("dermatoscope",
         "Close clinical photograph of a gloved hand holding a dermatoscope against "
         "the skin of a forearm, the patient's face out of frame entirely, plain "
         "clinical background. Even clinical light. 85mm, shallow depth of field.",
         "4:3", None),
        ("exam-room",
         "Photograph of a bright dermatology exam room: a plain examination couch, a "
         "wall-mounted lamp, a stool, a window with a white blind. No people, no "
         "signage, no text. 35mm.", "4:3", None),
        ("mohs-lab",
         "Photograph of an in-house histology bench: a microscope, a tray of glass "
         "slides, a cryostat in the background, a gloved hand at the edge of frame "
         "placing a slide, no face. Cool lab light. 50mm.", "4:3", None),
        ("laser-suite",
         "Photograph of a cosmetic dermatology treatment room with a plain white "
         "unbranded laser device on an articulated arm beside a treatment bed, soft "
         "lighting. No people, no screens with text. 35mm.", "4:3", None),
        ("skin-macro",
         "Macro photograph of healthy skin across a shoulder and upper back in soft "
         "window light, fine texture visible, no face in frame, no identifying marks. "
         "100mm macro.", "4:3", None),
        ("reception",
         "Photograph of a calm clinic reception: pale wood, a plain counter, two "
         "chairs, a plant, morning light. No people, no signage, no text. 35mm.",
         "4:3", None),
        ("instrument-tray",
         "Close photograph of a sterile tray set out for a skin biopsy: punch tool, "
         "forceps, a needle holder with a curved needle, gauze, all on blue sterile "
         "drape. No packaging, no printed labels, no lettering anywhere. No people. "
         "Even clinical light. 85mm.", "4:3", None),
        ("phone-call",
         "Photograph of a plain telephone handset lifted from its cradle on a "
         "clinician's desk beside a closed folder and a pen, a window behind. No "
         "people, no text. Afternoon light. 50mm.", "4:3", None),
        ("sunlight-window",
         "Photograph of a window seat in a clinic corridor with bright sunlight "
         "falling across a pale cushion and a plain wall. No people, no text. 35mm.",
         "4:3", None),
        ("pediatric-room",
         "Photograph of a paediatric dermatology exam room in soft colours: a low "
         "couch, a small wooden stool, a plain wooden toy on a shelf, a window. No "
         "people, no characters, no text. 35mm.", "4:3", None),
    ],
    "med-spas": [
        ("treatment-room",
         "Photograph of a bright, calm medical spa treatment room: a plain treatment "
         "bed with white linen, a ring light on a stand, a small cabinet, a plant. No "
         "people, no branding, no text. Soft daylight. 35mm.", "4:3", None),
        ("flatlay",
         "Overhead photograph of a treatment set-up on a white tray: two unlabelled "
         "glass vials, a small syringe, alcohol swabs, a pair of nitrile gloves. No "
         "text, no branding, no people. Even light. 50mm.", "4:3", None),
        ("injector-hands",
         "Close photograph of gloved hands drawing up a syringe from an unlabelled "
         "vial in a treatment room, no face in frame. Soft light. 85mm, shallow depth "
         "of field.", "4:3", None),
        ("laser-device",
         "Close photograph of a plain white unbranded laser handpiece resting on its "
         "cradle beside a treatment bed, soft light. No people, no screens with text. "
         "85mm.", "4:3", None),
        ("skincare-shelf",
         "Photograph of a shelf of unlabelled frosted-glass skincare bottles and jars "
         "in plain colours, evenly spaced, warm light. No text, no branding, no people. "
         "50mm.", "4:3", None),
        ("consult-room",
         "Photograph of a consultation room in a medical spa: two soft chairs facing "
         "each other, a low table, a hand mirror, a window with sheer curtains. No "
         "people, no text. 35mm.", "4:3", None),
        ("reception",
         "Photograph of a bright medical spa reception: a plain white counter, warm "
         "wood, plants, a single chair. No people, no signage, no text. 35mm.",
         "4:3", None),
        ("lounge",
         "Photograph of a calm lounge corner in a medical spa: a linen sofa, a carafe "
         "of water with lemon on a tray, a plant, soft light. No people, no text. "
         "50mm.", "4:3", None),
        ("towel-detail",
         "Close photograph of rolled white towels, a sprig of eucalyptus and a plain "
         "ceramic bowl on a wooden surface. No text, no people. Soft light. 85mm.",
         "4:3", None),
        ("evening-window",
         "Photograph of a medical spa treatment room at evening, a lamp and candles "
         "lit, the window going blue, the bed made up. No people, no text. 35mm.",
         "4:3", None),
    ],
    "plastic-surgeons": [
        ("consult-room",
         "Photograph of a private surgical consultation room: two upholstered chairs "
         "at a small table, a closed leather folder, a window with sheer curtains. No "
         "people, no text. Soft daylight. 35mm.", "4:3", None),
        ("operating-suite",
         "Photograph of an accredited private operating suite: an operating table "
         "under a surgical light, plain unbranded anaesthetic equipment, everything "
         "spotless and ready. No people, no screens with text. Cool clean light. "
         "35mm.", "4:3", None),
        ("recovery-room",
         "Photograph of a calm private recovery room: a single bed with white linen, "
         "a soft chair, a window with a garden beyond. No people, no text. Morning "
         "light. 35mm.", "4:3", None),
        ("gloved-hands",
         "Close photograph of a surgeon's gloved hands being held up after scrubbing, "
         "forearms only, no face, a sterile gown, blurred surgical suite behind. Cool "
         "light. 85mm.", "4:3", None),
        ("instrument-tray",
         "Close photograph of a sterile surgical instrument tray laid out on blue "
         "drape: scalpel handles, forceps, retractors, in order. No people, no text. "
         "Even light. 85mm.", "4:3", None),
        ("corridor",
         "Photograph of a quiet private clinic corridor: pale walls, a runner rug, one "
         "closed door, a window at the end. No people, no signage, no text. 35mm.",
         "4:3", None),
        ("private-entrance",
         "Photograph of a discreet private entrance: a plain dark door with an "
         "unlettered brass plate, a small canopy, clipped planting, a quiet side "
         "street. No people, no numbers, no text. 50mm.", "4:3", None),
        ("imaging-room",
         "Photograph of a 3D imaging room: a plain multi-camera rig on a stand facing "
         "a stool, a neutral grey backdrop, the monitor turned away. No people, no "
         "text. Even light. 35mm.", "4:3", None),
        ("waiting-lounge",
         "Photograph of a private waiting lounge with a single armchair, a side table, "
         "a lamp, and a window onto a courtyard. No people, no text. 50mm.",
         "4:3", None),
        ("aftercare-kit",
         "Overhead photograph of an aftercare kit packed on a bed: a folded plain "
         "compression garment, dressings, an unlabelled bottle, a plain card folder. "
         "No text, no branding, no people. Soft light. 50mm.", "4:3", None),
    ],
    "veterinary": [
        ("exam-table",
         "Photograph of a veterinary exam room: a golden retriever standing on a "
         "stainless steel table seen from behind, a stethoscope on the counter, a "
         "window. No human faces, no text. Bright clinic light. 35mm.", "4:3", None),
        ("reception",
         "Photograph of a warm veterinary reception: a wooden counter, a dog's lead "
         "hung on a hook, a bowl of water on the floor, plants. No people, no signage, "
         "no text. 35mm.", "4:3", None),
        ("surgical-suite",
         "Photograph of a veterinary surgical suite: a stainless table under a surgical "
         "light, anaesthetic machine, monitors turned away, everything clean and "
         "ready. No people, no text. 35mm.", "4:3", None),
        ("dental",
         "Close photograph of a veterinary dental station: a scaler handpiece, a "
         "dental x-ray plate, a plain tray, a tabby cat asleep under a blanket in the "
         "background. No people, no text. 50mm.", "4:3", None),
        ("lab",
         "Photograph of a veterinary in-house lab bench: a microscope, a small blood "
         "analyser with its screen turned away, sample tubes in a rack. No people, no "
         "text. Even light. 50mm.", "4:3", None),
        ("kennel-recovery",
         "Photograph of a veterinary recovery kennel: a spaniel asleep on a fleece "
         "blanket in a clean stainless kennel, a soft light above. No people, no "
         "text. 50mm.", "4:3", None),
        ("pharmacy",
         "Photograph of a veterinary dispensary shelf: rows of plain amber bottles and "
         "white tubs with no labels, a pill counter, a small paper bag. No people, no "
         "text. 50mm.", "4:3", None),
        ("puppy-visit",
         "Photograph of a labrador puppy sitting on a veterinary floor scale, seen "
         "from the side, a gloved hand steadying it, no human face. Bright clinic "
         "light. 50mm.", "4:3", None),
        ("cat-room",
         "Photograph of a quiet cat-only waiting room: a shelf of carriers with "
         "towels draped over them, a soft bench, a window, a plant. No people, no "
         "text. 35mm.", "4:3", None),
        ("night-entrance",
         "Photograph of a veterinary clinic entrance at night, the porch light on "
         "and the door lit from inside, rain on the path, an empty parking space. No "
         "people, no signage, no text. 35mm.", "4:3", None),
    ],
    "accounting-cpas": [
        ("closed-ledger",
         "Photograph of a closed leather-bound ledger on a walnut desk beside a "
         "fountain pen and reading glasses, morning light from a window. No text "
         "visible, no people. 50mm.", "4:3", None),
        ("folders",
         "Photograph of a neat row of manila folders with blank tabs standing in a "
         "desk tray, evenly spaced, a pen beside them. No text, no people. Even "
         "light. 50mm.", "4:3", None),
        ("scanner",
         "Close photograph of a document scanner on an office desk with a blank white "
         "page feeding through it, a small stack of blank pages beside it. No text, "
         "no people. 50mm.", "4:3", None),
        ("meeting-room",
         "Photograph of a small accounting firm's meeting room: a round oak table, "
         "two chairs, a window onto a city street, a carafe of water. No people, no "
         "text. 35mm.", "4:3", None),
        ("office-morning",
         "Photograph of a small professional office at seven in the morning, one desk "
         "lamp on over a closed laptop and a single folder, the rest of the room in "
         "blue dawn light from tall windows. Modern, tidy. No people, no text. 35mm.",
         "4:3", None),
        ("signing",
         "Close photograph of a hand with a fountain pen resting on a blank ruled "
         "sheet on a desk, no face in frame. Warm light. 85mm, shallow depth of "
         "field.", "4:3", None),
        ("archive",
         "Photograph of a wall of plain grey archive boxes on steel shelving, no "
         "labels, evenly stacked, one box pulled slightly out. No text, no people. "
         "Even light. 35mm.", "4:3", None),
        ("quiet-desk",
         "Photograph of a tidy accountant's desk at the end of the day: a closed plain "
         "grey laptop with no logo on its lid, a cup of coffee, a single unlabelled "
         "manila folder, everything squared to the edge. No writing, no lettering, no "
         "logos, no people. Afternoon light. 50mm.", "4:3", None),
        ("window",
         "Photograph looking out of a tenth-floor office window over a mid-sized "
         "American city at dusk, the window frame and a corner of a desk in the "
         "foreground. No people, no legible signage. 35mm.", "4:3", None),
        ("handshake",
         "Close photograph of two hands shaking across a wooden meeting table, one "
         "in a suit cuff and one in a shirt cuff, no faces in frame. Window light. "
         "85mm.", "4:3", None),
    ],
    "wealth-management": [
        ("two-chairs",
         "Photograph of a wealth adviser's meeting room: two leather armchairs facing "
         "each other across a low walnut table, a tall window, a plant. No people, no "
         "screens, no text. Soft daylight. 35mm.", "4:3", None),
        ("ruled-sheet",
         "Close photograph of a single sheet of heavy cream paper with faint ruled "
         "lines on a desk, a fountain pen laid across it, nothing written. No text, "
         "no people. Raking light. 85mm.", "4:3", None),
        ("brass-door",
         "Photograph of the entrance to an old stone office building: a black door, "
         "a polished brass plate with no lettering, a brass handle, stone steps. No "
         "people, no numbers, no text. Morning light. 50mm.", "4:3", None),
        ("bound-volumes",
         "Photograph of a wall of old bound volumes in green and oxblood cloth in a "
         "firm's library, spines with no legible lettering, a ladder. No people, no "
         "text. Warm light. 35mm.", "4:3", None),
        ("graphite",
         "Close photograph of a graphite pencil resting on a sheet of cream paper "
         "with a few faint pencil rules drawn, an eraser beside it. No text, no "
         "numbers, no people. Window light. 100mm macro.", "4:3", None),
        ("street",
         "Photograph of a quiet tree-lined street of stone and brick professional "
         "buildings in an American city at eight in the morning, long shadows. No "
         "people, no legible signage. 35mm.", "4:3", None),
        ("family-table",
         "Photograph of a long dining table set for a family meeting in a firm's "
         "private room: eight chairs, a jug of water, cream folders at each place, "
         "a garden through the windows. No people, no text. 35mm.", "4:3", None),
        ("bound-plan",
         "Close photograph of a thick document bound in a plain dark cloth cover with "
         "no lettering, sitting on a walnut desk beside a pen. No text, no people. "
         "Soft light. 85mm.", "4:3", None),
        ("window-light",
         "Photograph of afternoon light falling across an empty walnut desk and a "
         "leather chair in a quiet office, a tall window with wooden shutters. No "
         "people, no text. 35mm.", "4:3", None),
        ("keys",
         "Close photograph of an old set of house keys on a worn leather fob resting "
         "on a wooden table beside a folded letter with no visible writing. No text, "
         "no people. Warm light. 85mm.", "4:3", None),
    ],
    "recruiting": [
        ("shop-floor",
         "Photograph of a modern manufacturing floor: a row of CNC machining centres, "
         "clean epoxy floor, overhead cranes, no people in frame, no signage, no "
         "text. Bright industrial light. 35mm, wide.", "4:3", None),
        ("control-panel",
         "Close photograph of gloved hands at an industrial control panel of plain "
         "buttons and dials, the screen showing only a simple graph with no text, no "
         "face in frame. 50mm.", "4:3", None),
        ("plant-exterior",
         "Photograph of a large manufacturing plant exterior at dawn, the car park "
         "half full, the sky going orange behind the roofline. No people, no signage, "
         "no text. 35mm.", "4:3", None),
        ("interview-room",
         "Photograph of a plain interview room with two chairs at a small table and a "
         "glass wall onto a factory floor beyond. No people, no text. Even light. "
         "35mm.", "4:3", None),
        ("hard-hats",
         "Photograph of a row of plain white hard hats and hi-vis vests hung on hooks "
         "by a plant door, safety boots beneath. No text, no logos, no people. 50mm.",
         "4:3", None),
        ("precision-parts",
         "Close photograph of machined aluminium parts laid out on a workbench, a "
         "micrometer beside them, coolant sheen on the metal. No people, no text. "
         "85mm.", "4:3", None),
        ("phone-desk",
         "Photograph of a plain desk phone and a closed notebook on a recruiter's "
         "desk, a window with a view of an industrial estate. No people, no text. "
         "50mm.", "4:3", None),
        ("warehouse",
         "Photograph down a long aisle of a distribution warehouse: racking to the "
         "ceiling, shrink-wrapped pallets, a reach truck parked at the far end. No "
         "people, no text, no logos. 35mm.", "4:3", None),
        ("welding",
         "Photograph of a welder seen from behind at a fabrication bench, mask down, "
         "sparks flying, face completely hidden. Dark workshop, the weld the only "
         "light. 50mm.", "4:3", None),
        ("forklift-yard",
         "Photograph of a plant loading yard at shift change: a forklift parked by a "
         "dock door, stacked pallets, a trailer backed in. No people, no text, no "
         "logos. Late afternoon light. 35mm.", "4:3", None),
    ],
    "property-management": [
        ("keys-desk",
         "Close photograph of a ring of house keys with plain unlabelled tags beside a "
         "closed folder on a desk. No text, no people. Window light. 85mm.",
         "4:3", None),
        ("brick-facade",
         "Photograph of a well-kept three-storey brick apartment building on an "
         "American street, trimmed hedges, a clean entrance, morning light. No "
         "people, no signage, no numbers. 35mm.", "4:3", None),
        ("lockbox",
         "Close photograph of a plain combination lockbox hanging on the handle of a "
         "front door, the dials turned away, a brass handle. No numbers visible, no "
         "text, no people. 85mm.", "4:3", None),
        ("maintenance-van",
         "Photograph of a plain white American cargo van with no lettering parked "
         "outside an apartment building, side door open, tools inside. No people. "
         "Daylight. 35mm.", "4:3", None),
        ("work-order",
         "Close photograph of a plumber's gloved hands tightening a fitting under a "
         "kitchen sink, a torch beside them, no face in frame. 50mm.", "4:3", None),
        ("unit-ready",
         "Photograph of an empty freshly painted apartment ready to let: new grey "
         "plank floor, white walls, a window with the blind up, a single key on the "
         "counter. No people, no text. Bright daylight. 35mm.", "4:3", None),
        ("portfolio-aerial",
         "Aerial photograph of a street of similar American rental houses and a small "
         "apartment block, tidy lawns, cars in driveways. No people visible. Clear "
         "light. Drone, moderate height.", "4:3", None),
        ("inspection",
         "Close photograph of a gloved hand pressing the test button on a ceiling "
         "smoke detector, no face in frame. Even light. 50mm.", "4:3", None),
        ("leasing-office",
         "Photograph of a small property management office: a plain desk, two "
         "chairs, a key cabinet on the wall with its door closed, a window. No "
         "people, no text. 35mm.", "4:3", None),
        ("showing",
         "Photograph of an apartment front door standing open onto a lit hallway, a "
         "set of keys in the lock. No people, no numbers, no text. 50mm.",
         "4:3", None),
    ],
}


def request(parts: list, size: str, aspect: str, key: str, retries: int = 3):
    body = {"contents": [{"parts": parts}],
            "generationConfig": {"imageConfig": {"aspectRatio": aspect,
                                                 "imageSize": size}}}
    req = urllib.request.Request(
        URL.format(m=MODEL, k=key), data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"})
    for attempt in range(1, retries + 1):
        try:
            resp = json.load(urllib.request.urlopen(req, timeout=300))
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as e:
            detail = e.read().decode() if hasattr(e, "read") else str(e)
            if "credits are depleted" in detail or "billing" in detail:
                return None, f"BILLING: {detail[:160]}"
            if attempt == retries:
                return None, f"FAILED after {retries}: {detail[:160]}"
            time.sleep(4 * attempt)
            continue
        for part in resp["candidates"][0]["content"]["parts"]:
            if "inlineData" in part:
                return base64.b64decode(part["inlineData"]["data"]), None
        return None, "no image returned: " + json.dumps(resp)[:200]
    return None, "exhausted retries"


# --- one library per build ---------------------------------------------------
# The first pass shared one library across the six builds in a trade, so a
# visitor scrolling the trade index saw the same six photographs six times.
# `--per-build` gives each build its own set under <trade>/<build-slug>/.
# Build one keeps the shared images; the other five are generated fresh with a
# clause that moves the scene — building, light, angle — so they are different
# places rather than the same scene re-rolled.
VARIANTS = [
    "",
    "A single full-frame photograph, set somewhere different from the other photographs: an older brick "
    "building in an established, leafy neighbourhood, soft overcast light, the "
    "camera slightly lower than eye level.",
    "A single full-frame photograph, set somewhere different from the other photographs: a newer "
    "development with pale siding, bright clear midday sun, a slightly wider "
    "framing that shows more of the surroundings.",
    "A single full-frame photograph, set somewhere different from the other photographs: a mid-century "
    "property with dark timber and stone, late golden-hour light with long "
    "shadows, a tighter crop on the subject.",
    "A single full-frame photograph, set somewhere different from the other photographs: a coastal or "
    "lakeside property in white and grey, cool overcast morning light, a "
    "three-quarter angle from the right.",
    "A single full-frame photograph, set somewhere different from the other photographs: a rural or "
    "wooded property, warm early-evening light, the camera slightly above the "
    "subject.",
]


# Indoor subjects get a different room, not a different property: a biopsy
# tray "at a coastal property" came back on a sea wall.
INDOOR_VARIANTS = [
    "",
    "A single full-frame photograph, in a different room from the other photographs: "
    "an older building with tall sash windows and exposed brick, soft overcast "
    "light, the camera slightly lower than eye level.",
    "A single full-frame photograph, in a different room from the other photographs: a "
    "new-build with white walls and pale wood, bright midday light through "
    "blinds, a slightly wider framing.",
    "A single full-frame photograph, in a different room from the other photographs: a "
    "converted mid-century space with dark timber and stone, warm late-afternoon "
    "light, a tighter crop on the subject.",
    "A single full-frame photograph, in a different room from the other photographs: a "
    "light room in white and grey with a window onto water, cool morning light, "
    "a three-quarter angle from the right.",
    "A single full-frame photograph, in a different room from the other photographs: a "
    "room with a window onto woodland, warm early-evening light, the camera "
    "slightly above the subject.",
]
EXTERIOR_HINTS = ("roof", "house", "yard", "garden", "street", "exterior", "aerial",
                  "drone", "van", "truck", "driveway", "facade", "pool", "terrace",
                  "condenser", "solar", "fence", "kerb", "curb", "porch",
                  "neighbourhood", "lawn", "plant exterior", "meadow", "loading yard")


# Clinical rooms vary in layout and light only. An operating theatre in a
# brick loft is not a different clinic, it is an implausible one.
CLINICAL_VARIANTS = [
    "",
    "A single full-frame photograph of a different room from the other "
    "photographs: a larger room with pale grey-green walls and two ceiling "
    "lights, cool even light, the camera slightly lower than eye level.",
    "A single full-frame photograph of a different room from the other "
    "photographs: a compact white room with pale blue accents, bright light, "
    "a slightly wider framing.",
    "A single full-frame photograph of a different room from the other "
    "photographs: a room with warm wood cabinetry and a frosted window, soft "
    "afternoon light, a tighter crop on the subject.",
    "A single full-frame photograph of a different room from the other "
    "photographs: a room in white and light grey with a tall frosted window, "
    "cool morning light, a three-quarter angle from the right.",
    "A single full-frame photograph of a different room from the other "
    "photographs: a room with a high window, pale walls and stainless fittings, "
    "warm light, the camera slightly above the subject.",
]
CLINICAL_HINTS = ("operating", "surgical", "suite", "lab", "exam", "clinic",
                  "treatment", "dental", "sterile", "instrument", "biopsy",
                  "dermatoscope", "scanner", "recovery", "imaging", "kennel",
                  "veterinary", "pharmacy", "dispensary", "anaesthetic")


def variant_for(prompt: str, idx: int) -> str:
    p = prompt.lower()
    if any(h in p for h in EXTERIOR_HINTS):
        table = VARIANTS
    elif any(h in p for h in CLINICAL_HINTS):
        table = CLINICAL_VARIANTS
    else:
        table = INDOOR_VARIANTS
    return table[idx % len(table)]


def build_sets(trade: str):
    """Which image names each build shows, in the order build-gallery lists them."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "build_gallery", Path(__file__).resolve().parent / "build-gallery.py")
    g = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(g)
    pair = list(g.PAIRS.get(trade, ()))
    return [(slug, pair + list(s["tiles"])) for slug, s in g.SETS.get(trade, {}).items()]


def generate(trade: str, name: str, prompt: str, aspect: str, ref: str | None,
             key: str, force: bool, sub: str | None = None) -> str:
    out_dir = OUT / trade / sub if sub else OUT / trade
    out_dir.mkdir(parents=True, exist_ok=True)
    dest = out_dir / f"{name}.jpg"
    label = f"{sub}/{name}" if sub else name
    if dest.exists() and not force:
        return f"{label}: skipped (exists)"

    parts: list = [{"text": f"{prompt} {NEGATIVE}"}]
    if ref:
        ref_path = out_dir / f"{ref}.jpg"
        if not ref_path.exists():
            return f"{name}: reference {ref} not generated yet"
        parts.insert(0, {"inlineData": {
            "mimeType": "image/jpeg",
            "data": base64.b64encode(ref_path.read_bytes()).decode()}})

    data, err = request(parts, SIZE, aspect, key)
    if err:
        return f"{label}: {err}"
    dest.write_bytes(data)
    return f"{label}: {len(data) // 1024}KB"


def run(tasks: list, key: str, force: bool) -> None:
    """tasks: (sub, name, prompt, aspect, ref). Chained entries run after
    everything they could point at."""
    independent = [t for t in tasks if not t[4]]
    dependent = [t for t in tasks if t[4]]
    for batch in (independent, dependent):
        if not batch:
            continue
        with ThreadPoolExecutor(max_workers=4) as pool:
            for line in pool.map(
                    lambda t: generate(args_trade, t[1], t[2], t[3], t[4], key, force, t[0]),
                    batch):
                print(f"  {line}")


def main() -> None:
    global args_trade
    ap = argparse.ArgumentParser()
    ap.add_argument("trade")
    ap.add_argument("--only", nargs="*", help="generate just these names")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--plain", action="store_true",
                    help="with --per-build: no variation clause (for an image the "
                         "clause keeps turning into a diptych)")
    ap.add_argument("--per-build", action="store_true",
                    help="one library per build under <trade>/<slug>/; build one "
                         "keeps the shared images, the rest are generated")
    args = ap.parse_args()
    args_trade = args.trade

    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        sys.exit("GEMINI_API_KEY not set")
    items = LIBRARIES.get(args.trade)
    if not items:
        sys.exit(f"no library defined for {args.trade}")
    by_name = {i[0]: i for i in items}

    if not args.per_build:
        if args.only:
            items = [i for i in items if i[0] in args.only]
        run([(None, *i) for i in items], key, args.force)
        return

    import shutil
    tasks = []
    for idx, (slug, names) in enumerate(build_sets(args.trade)):
        if args.only and slug not in args.only:
            continue
        sub_dir = OUT / args.trade / slug
        sub_dir.mkdir(parents=True, exist_ok=True)
        for name in names:
            if name not in by_name:
                sys.exit(f"{args.trade}: no prompt for {name}")
            if idx == 0:
                src = OUT / args.trade / f"{name}.jpg"
                dst = sub_dir / f"{name}.jpg"
                if src.exists() and not dst.exists():
                    shutil.copy2(src, dst)
                    print(f"  {slug}/{name}: kept the shared image")
                continue
            _, prompt, aspect, ref = by_name[name]
            clause = "" if args.plain else variant_for(prompt, idx)
            tasks.append((slug, name, f"{prompt} {clause}".strip(), aspect, ref))
    run(tasks, key, args.force)


if __name__ == "__main__":
    main()
