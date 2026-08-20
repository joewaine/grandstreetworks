"""Dermatology — six practices. The two-door split holds; the promise differs."""

SOURCE_FIRM = "Bellweather Dermatology"
SOURCE_PHONE = "(555) 134-2210"
SOURCE_TEL = "+15551342210"
FORBIDDEN = ["Bellweather", "134-2210", "1342210"]

_SUB = "Medical dermatology, skin cancer surgery and a separate cosmetic clinic. Two different kinds of visit, two different booking paths, so you land in the right one."
_CLOSE = "Most major insurance accepted. Cosmetic clinic pricing published and booked separately."
_ASK = "Noticed something that's changed?"
_STRIP = "Skin checks within 2 weeks · Most insurance accepted · Cosmetic clinic on site"
_STRIP2 = "· Board-certified dermatology · Mohs surgery on site · Accepting new patients"

PAGES = {
    "d1-two-door.html": {
        "firm": "Harrowgate Dermatology", "phone": "(555) 482-3390", "tel": "+15554823390",
        "h1": "Two clinics, one practice. Pick the right door.",
        "copy": {
            _SUB: "Medical dermatology, skin cancer surgery and a separate cosmetic clinic — different calendars, different money, different front doors. Choosing correctly saves you weeks and an argument with your insurer.",
            _ASK: "Not sure which door is yours?",
            _CLOSE: "Most major insurance accepted on the medical side. The cosmetic clinic publishes its prices and books separately. If unsure, book medical.",
            _STRIP: "Two clinics · One practice · Most insurance accepted",
            _STRIP2: "· Board-certified dermatology · Mohs surgery on site · Two booking paths",
        },
    },
    "d2-two-week.html": {
        "firm": "Colvin Dermatology", "phone": "(555) 719-6628", "tel": "+15557196628",
        "h1": "Skin checks inside two weeks. Urgent ones sooner.",
        "copy": {
            _SUB: "Medical dermatology, skin cancer surgery and a separate cosmetic clinic. Routine skin checks book about two weeks out, and we hold urgent slots every single week for the things that shouldn't wait.",
            _ASK: "Been told the wait is three months?",
            _CLOSE: "Most major insurance accepted. Urgent slots held weekly — ring rather than booking online if something has changed quickly.",
            _STRIP: "Skin checks within 2 weeks · Urgent slots held weekly",
            _STRIP2: "· Board-certified dermatology · Mohs on site · Urgent slots weekly",
        },
    },
    "d3-the-spot.html": {
        "firm": "Sundial Dermatology", "phone": "(555) 253-4417", "tel": "+15552534417",
        "h1": "If it changed, don't wait to see whether it changes back.",
        "copy": {
            _SUB: "Medical dermatology, skin cancer surgery and a separate cosmetic clinic. If something has changed shape, colour or size, that is the appointment to make this week — anything suspicious is biopsied at the same visit.",
            _ASK: "Watching something and hoping?",
            _CLOSE: "Most major insurance accepted. Suspicious lesions biopsied the same visit wherever possible, with pathology back inside a week.",
            _STRIP: "Same-visit biopsy · Pathology inside a week · Most insurance accepted",
            _STRIP2: "· Board-certified dermatology · Mohs surgery on site · Same-visit biopsy",
        },
    },
    "d4-calendar.html": {
        "firm": "Westbrook Skin & Surgery", "phone": "(555) 864-1173", "tel": "+15558641173",
        "h1": "Diagnosis and removal without two separate waits.",
        "copy": {
            _SUB: "Medical dermatology, skin cancer surgery and a separate cosmetic clinic. Screening, biopsy and Mohs surgery all happen in this building, so a positive result doesn't mean joining another queue somewhere else.",
            _ASK: "Been referred on and lost weeks?",
            _CLOSE: "Most major insurance accepted. Mohs surgery on site, scheduled the week the pathology lands rather than the month after.",
            _STRIP: "Mohs on site · Scheduled the same week · Most insurance accepted",
            _STRIP2: "· Board-certified dermatology · Mohs surgery on site · One building",
        },
    },
    "d5-counter.html": {
        "firm": "Larkin Dermatology", "phone": "(555) 391-7756", "tel": "+15553917756",
        "h1": "The cosmetic clinic, priced on the page.",
        "copy": {
            _SUB: "Medical dermatology, skin cancer surgery and a separate cosmetic clinic. The cosmetic side runs on its own calendar with every price published, so nothing about it gets tangled up in your insurance.",
            _ASK: "Wanting cosmetic, not medical?",
            _CLOSE: "Cosmetic pricing published in full and booked separately. Medical dermatology runs on insurance and referral, on a different calendar.",
            _STRIP: "Cosmetic clinic on site · Pricing published · Booked separately",
            _STRIP2: "· Board-certified dermatology · Cosmetic clinic on site · Pricing published",
        },
    },
    "d6-phone.html": {
        "firm": "Fenmore Dermatology", "phone": "(555) 607-2284", "tel": "+15556072284",
        "h1": "Your results, from a person, on the phone.",
        "copy": {
            _SUB: "Medical dermatology, skin cancer surgery and a separate cosmetic clinic. Pathology comes back within a week and you hear it from someone who rings you — with the next appointment already booked before they hang up.",
            _ASK: "Waiting on a result right now?",
            _CLOSE: "Most major insurance accepted. Results delivered by phone within a week, never left sitting in a portal for you to find.",
            _STRIP: "Results by phone in a week · Next step booked on the call",
            _STRIP2: "· Board-certified dermatology · Mohs on site · Results by phone",
        },
    },
}
