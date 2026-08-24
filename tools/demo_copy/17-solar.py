"""Solar — six installers. Anti-hype throughout; the honesty differs in kind."""
SOURCE_FIRM = "Northlight Solar"
SOURCE_PHONE = "(555) 105-7744"
SOURCE_TEL = "+15551057744"
FORBIDDEN = ["Northlight", "105-7744", "1057744"]
_SUB = "Put in your address and last bill and get a real estimate — production, savings and payback — before anyone asks for your phone number. We install with our own crews and we've been here since 2011."
_NINETY = "Get the real number in about ninety seconds, without giving us your phone number. If it doesn't make sense for your roof, the tool will say so."
PAGES = {
    "d1-number-first.html": {"firm": "Fairhaven Solar", "phone": "(251) 328-6617", "tel": "+12513286617",
        "h1": "See the number first. Give us your details after.",
        "copy": {_SUB: "Put in your address and last bill and get a real estimate — production, savings and payback — before anyone asks for your phone number. Our own crews, installing here since 2009."}},
    "d2-no-knock.html": {"firm": "Cedar Line Solar", "phone": "(731) 771-2248", "tel": "+17317712248",
        "h1": "We have never knocked on a door and never will.",
        "copy": {_SUB: "No canvassers, no clipboards, no appointment setters paid per signature. Put in your address and last bill, see the real numbers, and ring us only if they work.",
                 _NINETY: "Ninety seconds, no phone number, and nobody will appear at your door on a Saturday because you used it."}},
    "d3-meter.html": {"firm": "Halgrove Energy", "phone": "(681) 604-8873", "tel": "+16816048873",
        "h1": "Twelve months of your meter. Not a national average.",
        "copy": {_SUB: "Estimates built from twelve months of your actual meter data, your roof's pitch and your shading — not a state average multiplied by square footage, which is how systems end up oversized."}},
    "d4-incentive-sheet.html": {"firm": "Brightfold Solar", "phone": "(402) 245-3390", "tel": "+14022453390",
        "h1": "Every credit and rebate, with what it's actually worth to you.",
        "copy": {_SUB: "The federal credit, the state rebate and your utility's programme, listed with the amount each is worth on your system and the date each one expires. Nothing is quoted as though it were a discount.",
                 _NINETY: "Ninety seconds for the real number, with the incentives itemised rather than blended into a headline figure."}},
    "d5-quiet.html": {"firm": "Ansonia Solar", "phone": "(231) 916-7742", "tel": "+12319167742",
        "h1": "Sometimes the answer is that your roof isn't worth it.",
        "copy": {_SUB: "Put in your address and last bill and get a straight estimate. Roughly one in five roofs we look at does not pay back well enough to recommend, and we say so rather than quoting anyway."}},
    "d6-direct.html": {"firm": "Kettle Ridge Solar", "phone": "(406) 483-2216", "tel": "+14064832216",
        "h1": "Our crews. Our electricians. No subcontractors.",
        "copy": {_SUB: "Every install done by our own crews and our own licensed electricians. No subcontractors, which is why the warranty call goes to the people who put the panels up.",
                 _NINETY: "Ninety seconds for the real number, and the crew who would install it works for us rather than for whoever bid lowest that month."}},
}
