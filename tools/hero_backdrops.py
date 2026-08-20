"""Which builds put their plate *behind* the hero rather than under it.

Not all of them, on purpose. A backdrop suits the trades whose argument is
physical — a roof, a flooded basement, a house on a lot. It actively hurts the
ones whose hero *is* the argument: wealth management's fee statement,
accounting's intake flow, architecture's title block. Those keep the plate
below the fold where it can't compete.

Within a chosen trade only two of the six get it, so a visitor scrolling the
set sees both treatments rather than six of one.

Pool builders was tried and pulled: both its candidates draw their own water in
CSS across the whole hero, so the photograph sat behind an opaque composition
and never showed. When a hero already fills itself edge to edge, the plate
belongs below it.

Keys are trade folders; values are indexes into that trade's deck order.
"""

BACKDROPS = {
    "roofing":              [0, 5],
    "restoration":          [0, 3],
    "hvac":                 [0, 3],
    "general-contractors":  [2, 4],
    "custom-home-builders": [3, 4],
    "luxury-real-estate":   [0, 5],
    "solar":                [2, 4],
}


def wants_backdrop(trade, index):
    return index in BACKDROPS.get(trade, [])
