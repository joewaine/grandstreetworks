"""Luxury real estate — six brokerages, six answers to 'six photographs'."""

SOURCE_FIRM = "Hallowell & Reece"
SOURCE_PHONE = "(555) 147-0180"
SOURCE_TEL = "+15551470180"
FORBIDDEN = ["Hallowell", "Reece", "147-0180", "1470180"]

_SUB = "Full marketing production: photography, film, drone, floor plans and a standalone property site, all included rather than optional extras."
_AGENTS = "Producing agents: full marketing production on every listing you take, a real split, and no desk fees. Have a look at what we'd give you."
_VAL = "A valuation conversation commits you to nothing and is genuinely useful even if you decide to stay put for another five years."
_SEQ = "A dedicated property page, the private network first, then public portals. Sequenced deliberately, not simultaneously."
_FIRST = "The production work happens before a single buyer sees the property, which is why the first two weeks matter most."

PAGES = {
    "d1-plate.html": {
        "firm": "Rathmore & Finch", "phone": "(319) 380-4471", "tel": "+13193804471",
        "h1": "Photographed the way the house deserves.",
        "copy": {
            _SUB: "Full marketing production on every listing: architectural photography, film, drone, measured floor plans and a standalone property site. Included, never presented later as an optional upgrade.",
            _FIRST: "All of it is finished before a single buyer sees the listing, because the first fortnight sets the price everything afterwards negotiates against.",
        },
    },
    "d2-prospectus.html": {
        "firm": "Bellamy Estates", "phone": "(309) 617-2293", "tel": "+13096172293",
        "h1": "A printed prospectus, not a portal listing.",
        "copy": {
            _SUB: "Full marketing production: photography, film, drone, measured plans and a bound prospectus delivered by hand to the buyers most likely to move on it, before anything is published anywhere.",
            _SEQ: "The prospectus goes to a named private list first, then to a dedicated property page, then to the portals. Deliberately in that order.",
        },
    },
    "d3-storyboard.html": {
        "firm": "Ellery & Vane", "phone": "(217) 245-8830", "tel": "+12172458830",
        "h1": "Every house gets a film, not a slideshow.",
        "copy": {
            _SUB: "Full marketing production: photography, drone, measured plans, a standalone property site, and a properly directed film with a location scout and a shooting schedule rather than a phone on a gimbal.",
            _FIRST: "Production is complete before the listing goes live. A film shot after the price drops is a film nobody watches.",
        },
    },
    "d4-seconddoor.html": {
        "firm": "Thornbury Property Group", "phone": "(719) 903-1164", "tel": "+17199031164",
        "h1": "For sellers, and for the agents who wish they'd joined sooner.",
        "copy": {
            _SUB: "Full marketing production on every listing: photography, film, drone, plans and a property site, included. Two doors here: one for owners selling, one for agents tired of paying for their own marketing.",
            _AGENTS: "Producing agents: full production on every listing you take, a genuine split, no desk fees, and no monthly bill for the marketing you are already paying for elsewhere.",
        },
    },
    "d5-masthead.html": {
        "firm": "Marlowe & Hart", "phone": "(458) 458-7726", "tel": "+14584587726",
        "h1": "Forty-one years on the same six streets.",
        "copy": {
            _SUB: "Full marketing production: photography, film, drone, plans and a standalone property site. Forty-one years in this neighbourhood, which is why we know what the house three doors down actually sold for.",
            _VAL: "A valuation conversation commits you to nothing and is worth having even if you intend to stay another decade. We have had many of those.",
        },
    },
    "d6-quiet.html": {
        "firm": "Ashcroft Residential", "phone": "(765) 636-6649", "tel": "+17656366649",
        "h1": "Sold quietly, before it was ever listed.",
        "copy": {
            _SUB: "Full marketing production, held in reserve. A good share of our sales close from a private list before anything is published: no sign, no portal, no neighbours counting the viewings.",
            _SEQ: "The private network sees it first and often that is where it ends. A property page and the portals follow only if you want them to.",
        },
    },
}
