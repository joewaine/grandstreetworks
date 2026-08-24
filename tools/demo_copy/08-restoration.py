"""Restoration — six companies. Everyone dries a house; the difference is the claim."""

SOURCE_FIRM = "Halcyon Restoration"
SOURCE_PHONE = "(555) 044-9001"
SOURCE_TEL = "+15550449001"
FORBIDDEN = ["Halcyon", "044-9001", "0449001"]

_SUB = "Emergency water, fire and mould restoration. We tarp, extract and dry, then bill your insurer direct and sit with the adjuster so you don't have to."
_ANSWER = "A person answers. We dispatch immediately and give you an arrival window measured in minutes."
_SCOPE = "Full photographic scope and moisture log, submitted to your carrier. We bill them direct and meet the adjuster on site."
_HOUR = "Every hour water sits, the damage and the cost compound. This is why we answer at 3am."
_TWO = "You are dealing with a disaster and an insurer at the same time. We take the second one off you."
_LOG = "Daily readings until verified dry, then reconstruction. You get the log, so nothing is disputed months later."

PAGES = {
    "d1-dispatch.html": {
        "firm": "Keystone Restoration", "phone": "(717) 521-7043", "tel": "+17175217043",
        "h1": "Crews roll before we've worked out who's paying.",
        "copy": {
            _SUB: "Emergency water, fire and mould restoration. Crews are dispatched the moment you ring. The questions about carriers, deductibles and coverage happen afterwards, because the water isn't waiting for them.",
            _ANSWER: "A person answers, takes the address, and rolls a truck. The paperwork conversation happens once the extraction is running.",
            _HOUR: "Every hour standing water sits, the drying time and the claim both grow. That is the whole reason we answer at three in the morning.",
        },
    },
    "d2-directbill.html": {
        "firm": "Bluewater Restoration", "phone": "(559) 638-2219", "tel": "+15596382219",
        "h1": "We bill your insurer. You pay your deductible.",
        "copy": {
            _SUB: "Emergency water, fire and mould restoration, billed direct to your carrier. You pay your deductible and nothing else: no float, no reimbursement paperwork, no waiting on a cheque to pay us.",
            _SCOPE: "A full photographic scope and moisture log goes to your carrier in their own format. We bill them direct, so you are never the one chasing the money.",
            _TWO: "You are dealing with a flooded house and an insurance company on the same morning. We will take the second one off your hands.",
        },
    },
    "d3-referral.html": {
        "firm": "Arbor Restoration Group", "phone": "(772) 947-3360", "tel": "+17729473360",
        "h1": "Most of our work comes from plumbers and agents.",
        "copy": {
            _SUB: "Emergency water, fire and mould restoration. Most of our calls come from plumbers, property managers and insurance agents who have watched us work, which is a harder reputation to buy than advertising.",
            _ANSWER: "A person answers day or night, whether you are the homeowner, the plumber already on site, or the agent who sent us.",
            _LOG: "Daily readings until independently verified dry, then reconstruction, with the log handed to whoever referred you as well as to you.",
        },
    },
    "d4-sixtyminute.html": {
        "firm": "Rapid Dry Restoration", "phone": "(534) 384-1176", "tel": "+15343841176",
        "h1": "Sixty minutes, or we tell you before the hour is up.",
        "copy": {
            _SUB: "Emergency water, fire and mould restoration with a sixty-minute metro response. If a crew is not going to make the hour, you get a call before the hour is out rather than an apology afterwards.",
            _ANSWER: "A person answers and gives you an arrival time in minutes. If it slips, we ring you. We do not let you sit and wonder.",
            _HOUR: "The first sixty minutes decide how much of the floor survives. Everything about how we are set up follows from that.",
        },
    },
    "d5-adjuster.html": {
        "firm": "Claymore Restoration", "phone": "(970) 715-6628", "tel": "+19707156628",
        "h1": "We stand with your adjuster and show the readings.",
        "copy": {
            _SUB: "Emergency water, fire and mould restoration. We document before we touch anything, meet your adjuster on site, and produce the moisture readings when the scope gets argued, which it does.",
            _SCOPE: "Dated photographs and a full moisture log, submitted in your carrier's format, with one of our people standing beside the adjuster when they scope it.",
            _TWO: "Disaster and insurer at once is more than most people can carry. We handle the second one and keep you copied on everything.",
        },
    },
    "d6-nightline.html": {
        "firm": "Nightwatch Restoration", "phone": "(435) 209-4482", "tel": "+14352094482",
        "h1": "Three in the morning is when most of these start.",
        "copy": {
            _SUB: "Emergency water, fire and mould restoration, staffed overnight because that is when pipes fail. Our own people answer the line at any hour, not a call centre taking a message for the morning.",
            _ANSWER: "Our own dispatcher answers, at any hour, and a truck is moving while you are still on the phone.",
            _HOUR: "Pipes burst at night and the damage compounds until someone arrives. Which is precisely why the line is staffed at three in the morning.",
        },
    },
}
