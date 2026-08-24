"""Roofing — six firms, six arguments, one trade.

Shared and left alone on purpose: the four services, the order of a job, the
nav. Six roofers really do tear off, re-deck and magnet-sweep. What changes is
who they are, what they lead with, and what they put a number on.
"""

SOURCE_FIRM = "Ridgeline Roofing"
SOURCE_PHONE = "(555) 014-8820"
SOURCE_TEL = "+15550148820"
FORBIDDEN = ["Ridgeline", "014-8820", "0148820"]

PAGES = {
    "d1-stormline.html": {
        "short": {"Ridgeline": "Halloran"},

        "firm": "Halloran Roofing",
        "phone": "(970) 208-4417",
        "tel": "+19702084417",
        "copy": {
            "Hail took out half the neighbourhood. Ridgeline had a tarp on our roof the same afternoon and sat with our adjuster the following Tuesday. The rest of the street was still waiting on callbacks.":
                "Hail took out half the neighbourhood. Halloran had a tarp on our roof before dark and sat with our adjuster the following Tuesday. The rest of the street was still waiting on callbacks.",
            "A roof over your head by the end of the week.":
                "Tarped tonight. Replaced this week.",
            "Storm damage, full replacements and repairs across the metro. We meet your adjuster, handle the claim paperwork, and you get one number to call.":
                "Storm damage, full replacements and repairs across the metro. We tarp the same night you ring, meet your adjuster on the roof, and hand you one number that stays the same from the first call to the warranty.",
            "Got water coming in right now?":
                "Water coming in tonight?",
            "Free inspections. No obligation. We'll tell you if you don't need a roof.":
                "We tarp first and work out whose bill it is afterwards. No obligation, and we will tell you when you don't need a roof.",
            "Licensed &amp; insured · Serving the metro area since 2004":
                "Licensed &amp; insured · Family-run since 1998",
            "· Licensed, bonded and insured · Serving the metro area since 2004":
                "· Licensed, bonded and insured · Family-run since 1998",
            "Same-day emergency tarping": "Tarped within four hours",
            "Emergency response · 24/7": "Storm crews standing by · 24/7",
            "The part most roofers don't explain, which is the part homeowners are actually anxious about.":
                "The part most roofers leave vague, which is the part keeping you awake while it's still raining.",
            "Call and a human answers — day, night, weekend, during the storm. Emergency tarping usually the same day.":
                "Ring at three in the morning during a hailstorm and a person picks up. Tarping crews run through the night in storm season.",
        },
    },
    "d2-neighbours.html": {
        "firm": "Fair Oaks Roofing",
        "phone": "(217) 331-9075",
        "tel": "+12173319075",
        "copy": {
            "A roof over your head by the end of the week.":
                "Ask the four houses on your street we did this year.",
            "Storm damage, full replacements and repairs across the metro. We meet your adjuster, handle the claim paperwork, and you get one number to call.":
                "Storm damage, full replacements and repairs, mostly within a few miles of our yard. Nearly every job we book comes from the last one, which is a strong incentive to leave a street tidy.",
            "Got water coming in right now?":
                "Want to see one we finished nearby?",
            "Free inspections. No obligation. We'll tell you if you don't need a roof.":
                "Free inspections, no obligation, and we will happily give you the address of a roof we did on your street so you can look at it yourself.",
            "Licensed &amp; insured · Serving the metro area since 2004":
                "Licensed &amp; insured · Two generations in this county",
            "· Licensed, bonded and insured · Serving the metro area since 2004":
                "· Licensed, bonded and insured · Two generations in this county",
            "Same-day emergency tarping": "Same-day emergency tarping",
            "Emergency response · 24/7": "Neighbourhood crews · Local since 1991",
            "The part most roofers don't explain, which is the part homeowners are actually anxious about.":
                "The part most roofers gloss over, which is exactly what your neighbours will ask you about afterwards.",
            "We walk it with you, register your warranty, and you have a direct number if anything ever comes up.":
                "We walk it with you, register the warranty, and leave you the mobile number of the person who ran your job — not an office line.",
        },
    },
    "d3-numbers.html": {
        "firm": "Meridian Roof Co.",
        "phone": "(463) 645-2130",
        "tel": "+14636452130",
        "copy": {
            "A roof over your head by the end of the week.":
                "Two thousand four hundred roofs. Six crews. One foreman you'll actually meet.",
            "Storm damage, full replacements and repairs across the metro. We meet your adjuster, handle the claim paperwork, and you get one number to call.":
                "Storm damage, full replacements and repairs across the metro. Twenty-one years, 2,400 roofs, and a foreman who gives you his number on day one and answers it on day four hundred.",
            "Got water coming in right now?":
                "Want the numbers on your roof?",
            "Free inspections. No obligation. We'll tell you if you don't need a roof.":
                "Free inspection, every slope photographed, and a written figure the same day. We will tell you plainly when the answer is a repair rather than a roof.",
            "Licensed &amp; insured · Serving the metro area since 2004":
                "Licensed &amp; insured · 2,400 roofs since 2003",
            "· Licensed, bonded and insured · Serving the metro area since 2004":
                "· Licensed, bonded and insured · 2,400 roofs since 2003",
            "Emergency response · 24/7": "2,400 roofs · 21 years · 6 crews",
            "25-year workmanship warranty": "25-year workmanship warranty, in writing",
            "The part most roofers don't explain, which is the part homeowners are actually anxious about.":
                "The part most roofers keep vague, which is the part we would rather put a number against.",
            "We go up, photograph everything, and tell you whether you need a roof or a repair. No pressure either way.":
                "We go up, photograph every slope and valley, and give you the count: how many nails were short, how many vents were blocked, how many years are left.",
        },
    },
    "d4-safetyyellow.html": {
        "firm": "Anchor Peak Roofing",
        "phone": "(210) 872-6604",
        "tel": "+12108726604",
        "copy": {
            "A roof over your head by the end of the week.":
                "Eighty-nine a month, or the whole claim handled. Your choice.",
            "Storm damage, full replacements and repairs across the metro. We meet your adjuster, handle the claim paperwork, and you get one number to call.":
                "Storm damage, full replacements and repairs across the metro. Two ways to pay for it: we run the insurance claim end to end, or you finance it from $89 a month with nothing down.",
            "Got water coming in right now?":
                "Worried about how you'd pay for it?",
            "Free inspections. No obligation. We'll tell you if you don't need a roof.":
                "Free inspection and a straight answer on both routes — what the claim would likely cover, and what the monthly would be if it doesn't.",
            "Licensed &amp; insured · Serving the metro area since 2004":
                "Licensed &amp; insured · Financing approved in minutes",
            "· Licensed, bonded and insured · Serving the metro area since 2004":
                "· Licensed, bonded and insured · Financing approved in minutes",
            "Financing from $89/mo": "From $89/mo, nothing down",
            "Emergency response · 24/7": "Claims handled · Financing on site",
            "The part most roofers don't explain, which is the part homeowners are actually anxious about.":
                "The part most roofers won't put a figure on, which is the only part most homeowners actually want a figure on.",
            "If it's insurance, we meet your adjuster on site. If it's retail, you get a fixed written price with financing options.":
                "If it's insurance, we meet your adjuster on the roof and handle the paperwork. If it isn't, you get one fixed written price and a monthly figure beside it.",
        },
    },
    "d5-claimdocket.html": {
        "short": {"Ridgeline": "Sentry"},

        "firm": "Sentry Roofing & Restoration",
        "phone": "(620) 490-7728",
        "tel": "+16204907728",
        "copy": {
            "Hail took out half the neighbourhood. Ridgeline had a tarp on our roof the same afternoon and sat with our adjuster the following Tuesday. The rest of the street was still waiting on callbacks.":
                "The first adjuster wrote it up for four thousand. Sentry filed a supplement with photographs taken before he arrived, and the final cheque was just under nineteen.",
            "A roof over your head by the end of the week.":
                "We meet your adjuster on the roof.",
            "Storm damage, full replacements and repairs across the metro. We meet your adjuster, handle the claim paperwork, and you get one number to call.":
                "Storm and hail claims across the metro. We photograph the damage before the adjuster arrives, stand on the roof with them, and put the supplement in writing when they miss something — which they usually do.",
            "Got water coming in right now?":
                "Claim denied or underpaid?",
            "Free inspections. No obligation. We'll tell you if you don't need a roof.":
                "Free inspection and an honest read on whether the claim is worth filing. Sometimes it isn't, and a denied claim on your record costs you more than the repair.",
            "Licensed &amp; insured · Serving the metro area since 2004":
                "Licensed &amp; insured · Haag-certified inspectors",
            "· Licensed, bonded and insured · Serving the metro area since 2004":
                "· Licensed, bonded and insured · Haag-certified inspectors",
            "Insurance claims handled": "Supplements filed and won",
            "Emergency response · 24/7": "Adjuster meetings · Claims &amp; supplements",
            "The part most roofers don't explain, which is the part homeowners are actually anxious about.":
                "The part most roofers hand back to you in a folder, which is the part that decides what the cheque says.",
            "Free inspection, full photo report, and we meet the adjuster on site so nothing gets argued about later.":
                "Free inspection, a dated photo report filed before the adjuster arrives, and one of our inspectors on the roof beside them when they scope it.",
        },
    },
    "d6-dispatch.html": {
        "firm": "Northgate Roofing",
        "phone": "(570) 676-3382",
        "tel": "+15706763382",
        "copy": {
            "A roof over your head by the end of the week.":
                "Call during the storm. Someone answers.",
            "Storm damage, full replacements and repairs across the metro. We meet your adjuster, handle the claim paperwork, and you get one number to call.":
                "Storm damage, full replacements and repairs across the metro. One number, answered by a person in our office rather than a service, and a truck dispatched from whichever yard is closest to you.",
            "Got water coming in right now?":
                "Storm just came through?",
            "Free inspections. No obligation. We'll tell you if you don't need a roof.":
                "Ring the number. A person answers, takes the address, and tells you when the truck will be there. No forms, no callback queue.",
            "Licensed &amp; insured · Serving the metro area since 2004":
                "Licensed &amp; insured · Three yards across the metro",
            "· Licensed, bonded and insured · Serving the metro area since 2004":
                "· Licensed, bonded and insured · Three yards across the metro",
            "Emergency response · 24/7": "Dispatch open · A person, not a service",
            "Same-day emergency tarping": "Trucks dispatched, not scheduled",
            "The part most roofers don't explain, which is the part homeowners are actually anxious about.":
                "The part most roofers make you chase an office for, which is the part you want answered while it is still raining.",
            "Call and a human answers — day, night, weekend, during the storm. Emergency tarping usually the same day.":
                "Day, night, weekend, mid-storm: a person in our own office picks up, not an answering service taking a message for Monday.",
        },
    },
}
