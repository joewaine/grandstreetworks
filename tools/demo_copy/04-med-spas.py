"""Med spas — six businesses. Published pricing stays; the promise around it moves."""

SOURCE_FIRM = "Lumen Aesthetics"
SOURCE_PHONE = "(555) 121-6600"
SOURCE_TEL = "+15551216600"
FORBIDDEN = ["Lumen", "121-6600", "1216600"]

_SUB = "Botox, filler, laser and medical-grade skincare, delivered by licensed injectors. Every price is on this page and you can book a real appointment slot without making an account."
_CLOSE = "Free consultations. All pricing published. Evening and Saturday appointments."
_ASK = "First time, or switching?"
_STRIP = "· Medical director on site · Licensed nurse injectors · Est. 2019"

PAGES = {
    "d1-pricelist.html": {
        "firm": "Marisol Aesthetics", "phone": "(555) 802-4419", "tel": "+15558024419",
        "h1": "Every price on the page. No consultation required to see it.",
        "copy": {
            _SUB: "Botox, filler, laser and medical-grade skincare from licensed nurse injectors. Every price is printed here, per unit and per syringe, so you can work out your visit before you book it.",
            _ASK: "Tired of 'call for pricing'?",
            _CLOSE: "Free consultations, every price published, and evening and Saturday appointments. Nothing costs more than the page says.",
            _STRIP: "· Medical director on site · Nurse injectors · Pricing published in full",
        },
    },
    "d2-membership.html": {
        "firm": "Verity Skin & Aesthetics", "phone": "(555) 337-1052", "tel": "+15553371052",
        "h1": "A monthly credit that rolls over, and never expires.",
        "copy": {
            _SUB: "Botox, filler, laser and medical-grade skincare from licensed injectors. Members put by a monthly credit that rolls over indefinitely, so treatment gets budgeted rather than deferred.",
            _ASK: "Treating occasionally and paying full price?",
            _CLOSE: "Free consultations, member pricing on everything, and credit that never expires. Cancel any month; the balance stays yours.",
            _STRIP: "· Medical director on site · Licensed injectors · Credit never expires",
        },
    },
    "d3-twotaps.html": {
        "firm": "Bright Hour Med Spa", "phone": "(555) 690-3376", "tel": "+15556903376",
        "h1": "Book in two taps. No account, no callback.",
        "copy": {
            _SUB: "Botox, filler, laser and medical-grade skincare from licensed injectors. Real slots on a real calendar, bookable in about forty seconds, with no account to create and nobody ringing you back to confirm.",
            _ASK: "Given up on booking somewhere?",
            _CLOSE: "Free consultations, live availability, and evening and Saturday slots. Book it now and get a text, not a phone call.",
            _STRIP: "· Medical director on site · Licensed injectors · Live booking, no account",
        },
    },
    "d4-ownedgrid.html": {
        "firm": "Onyx & Ivory Aesthetics", "phone": "(555) 148-2263", "tel": "+15551482263",
        "h1": "Under-treated on purpose. You can always add more.",
        "copy": {
            _SUB: "Botox, filler, laser and medical-grade skincare from licensed injectors. We start below what you asked for and top up at the two-week review, because the correction for too little is easy and the correction for too much is time.",
            _ASK: "Been over-filled somewhere before?",
            _CLOSE: "Free consultations, published pricing, and a two-week review included on every treatment. We will say no when the answer is no.",
            _STRIP: "· Medical director on site · Licensed injectors · Conservative by default",
        },
    },
    "d5-menu.html": {
        "short": {"Lumen": "Palmer Row"},
        "firm": "Palmer Row Med Spa", "phone": "(555) 275-8804", "tel": "+15552758804",
        "h1": "Read the whole menu before you sit down.",
        "copy": {
            "Lumen just put the prices up and let me book a Thursday evening.":
                "Palmer Row printed the whole menu and let me pick a Thursday evening off the calendar.",
            _SUB: "Botox, filler, laser and medical-grade skincare from licensed injectors. The full menu is here with prices and packages, because deciding in the chair is how people end up spending more than they meant to.",
            _ASK: "Not sure what you actually need?",
            _CLOSE: "Free consultations. Take the menu away, think about it, and book when you have decided. Evening and Saturday appointments.",
            _STRIP: "· Medical director on site · Licensed injectors · Full menu published",
        },
    },
    "d6-clients.html": {
        "firm": "Juniper Aesthetics", "phone": "(555) 916-4471", "tel": "+15559164471",
        "h1": "The same injector, every visit, for years.",
        "copy": {
            _SUB: "Botox, filler, laser and medical-grade skincare from licensed injectors. You keep the same injector visit after visit, which is why the result stays consistent instead of drifting with whoever happened to be free.",
            _ASK: "Been passed around a rota?",
            _CLOSE: "Free consultations, published pricing, and your injector booked by name. Evening and Saturday appointments available.",
            _STRIP: "· Medical director on site · Licensed injectors · Same injector every visit",
        },
    },
}
