"""Plastic surgery — six practices. Clinical scope holds; the emphasis moves."""

SOURCE_FIRM = "Aurelia Aesthetic Surgery"
SOURCE_PHONE = "(555) 118-9030"
SOURCE_TEL = "+15551189030"
FORBIDDEN = ["Aurelia", "118-9030", "1189030"]

_SUB = "Aesthetic and reconstructive surgery in a private, accredited facility. Every consultation is with the surgeon who will operate — not a coordinator, not an associate."
_CLOSE = "Private consultations. Financing available. All enquiries handled confidentially."
_STRIP = "Board certified · Private consultations · Accredited surgical suite"
_STRIP2 = "· Board certified · Private consultations · Accredited surgical suite"
_ASK = "Considering something, but not ready to book?"

PAGES = {
    "d1-portfolio.html": {
        "firm": "Wyeth Plastic Surgery", "phone": "(555) 306-2214", "tel": "+15553062214",
        "h1": "Look through the cases before you ring anyone.",
        "copy": {
            _SUB: "Aesthetic and reconstructive surgery in a private, accredited facility. Before you speak to anybody, look through the cases — unretouched, photographed at the same angles under the same light, out to a year.",
            _ASK: "Want to see the outcomes first?",
            _CLOSE: "Private consultations, and every case shown here was performed by the surgeon you would sit with. All enquiries handled confidentially.",
            _STRIP: "Board certified · Cases photographed to one year",
            _STRIP2: "· Board certified · Cases photographed to one year",
        },
    },
    "d2-suite.html": {
        "firm": "Calder Aesthetic Surgery", "phone": "(555) 774-1128", "tel": "+15557741128",
        "h1": "One suite. One surgeon. One team, every time.",
        "copy": {
            _SUB: "Aesthetic and reconstructive surgery in our own accredited facility. The same anaesthetist, the same nurses and the same surgeon on every case, which is the part of a result nobody photographs.",
            _ASK: "Want to see where you'd have it done?",
            _CLOSE: "Private consultations and a tour of the suite before you commit to anything. Financing available; all enquiries handled confidentially.",
            _STRIP: "AAAASF accredited · One surgeon · One team",
            _STRIP2: "· AAAASF accredited · One surgeon · One team",
        },
    },
    "d3-consultation.html": {
        "firm": "Rothbury Plastic Surgery", "phone": "(555) 962-8840", "tel": "+15559628840",
        "h1": "Fifty unhurried minutes with the surgeon who operates.",
        "copy": {
            _SUB: "Aesthetic and reconstructive surgery in a private, accredited facility. The consultation is with the surgeon, it runs fifty minutes, and it ends with a written plan rather than a deposit request.",
            _ASK: "Not ready to decide anything?",
            _CLOSE: "Private consultations with no coordinator in the room and no decision expected on the day. All enquiries handled confidentially.",
            _STRIP: "Board certified · Fifty-minute consultations · No coordinators",
            _STRIP2: "· Board certified · Fifty-minute consultations · No coordinators",
        },
    },
    "d4-credential.html": {
        "firm": "Aldenmore Surgical Aesthetics", "phone": "(555) 445-7702", "tel": "+15554457702",
        "h1": "Board certified — and here is what that actually means.",
        "copy": {
            _SUB: "Aesthetic and reconstructive surgery in a private, accredited facility. Certification, hospital privileges and facility accreditation all published here, because almost nobody explains which of the three actually protects you.",
            _ASK: "Comparing surgeons and finding it opaque?",
            _CLOSE: "Private consultations. Bring the other quotes and we will go through what each credential on them does and doesn't mean. Enquiries handled confidentially.",
            _STRIP: "ABPS certified · Hospital privileges · AAAASF suite",
            _STRIP2: "· ABPS certified · Hospital privileges · AAAASF suite",
        },
    },
    "d5-gallery.html": {
        "firm": "Marchetti Plastic Surgery", "phone": "(555) 218-6635", "tel": "+15552186635",
        "h1": "Nine hundred cases, photographed at every stage.",
        "copy": {
            _SUB: "Aesthetic and reconstructive surgery in a private, accredited facility. Nine hundred cases over eighteen years, each photographed before, at six weeks, at six months and at a year — including the ones that took revision.",
            _ASK: "Want to see a case like yours?",
            _CLOSE: "Private consultations. Tell us what you are considering and we will pull the cases closest to it. All enquiries handled confidentially.",
            _STRIP: "Board certified · 900 cases · 18 years",
            _STRIP2: "· Board certified · 900 cases · 18 years",
        },
    },
    "d6-private.html": {
        "firm": "Sable Plastic Surgery", "phone": "(555) 583-9917", "tel": "+15555839917",
        "h1": "Discreet from the first phone call onward.",
        "copy": {
            _SUB: "Aesthetic and reconstructive surgery in a private, accredited facility. Separate entrance, no shared waiting room, and appointments scheduled so that you will not pass another patient coming or going.",
            _ASK: "Privacy the thing holding you back?",
            _CLOSE: "Private consultations, private entrance, and nothing about your enquiry recorded anywhere it does not have to be. Financing available.",
            _STRIP: "Board certified · Private entrance · Single-patient scheduling",
            _STRIP2: "· Board certified · Private entrance · Single-patient scheduling",
        },
    },
}
