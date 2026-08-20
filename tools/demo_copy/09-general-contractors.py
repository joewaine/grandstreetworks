"""General contracting — six builders. The trust document differs, the trade doesn't."""

SOURCE_FIRM = "Corvid Build Co."
SOURCE_PHONE = "(555) 071-3355"
SOURCE_TEL = "+15550713355"
FORBIDDEN = ["Corvid", "071-3355", "0713355"]

_SUB = "Whole-home renovations, additions and structural work. Projects typically start at $75,000. You get a fixed schedule, a named project manager, and a weekly update you don't have to chase."
_PM = "A named project manager, a written update every Friday, and a final walkthrough with a punch list we actually close out."
_FEW = "We take on fewer projects than we could, because running four properly beats running nine badly."
_ANX = "The part homeowners are genuinely anxious about isn't the price. It's not knowing what happens or when."
_PROP = "Drawings, engineering where needed, and a line-item proposal. One number, with allowances stated openly."

PAGES = {
    "d1-schedule.html": {
        "firm": "Whitfield Build Co.", "phone": "(555) 428-9910", "tel": "+15554289910",
        "h1": "You get the schedule before anyone swings a hammer.",
        "copy": {
            _SUB: "Whole-home renovations, additions and structural work, typically from $75,000. Before demolition starts you have a week-by-week schedule with every trade's dates on it, and we measure ourselves against it in public.",
            _ANX: "What actually keeps homeowners awake isn't the number. It's not knowing which week the kitchen comes back.",
            _PM: "A named project manager, a written update every Friday against the published schedule, and a punch list we close rather than abandon.",
        },
    },
    "d2-plainnumbers.html": {
        "firm": "Marrant Construction", "phone": "(555) 736-2204", "tel": "+15557362204",
        "h1": "One number, and every allowance stated openly.",
        "copy": {
            _SUB: "Whole-home renovations, additions and structural work, typically from $75,000. One line-item proposal with the allowances written where you can see them, because that is where surprise change orders are usually hiding.",
            _PROP: "Drawings, engineering where it's needed, and a line-item proposal. Every allowance is named and priced, so you know exactly which numbers can still move.",
            _ANX: "The price is rarely the anxious part. Not knowing which parts of it are still a guess — that's the anxious part.",
        },
    },
    "d3-sitediary.html": {
        "firm": "Halverson Build Co.", "phone": "(555) 291-6673", "tel": "+15552916673",
        "h1": "Photographs from your site, every single day.",
        "copy": {
            _SUB: "Whole-home renovations, additions and structural work, typically from $75,000. You get a dated site diary with photographs every working day, so you can follow the job from your desk without ringing anybody.",
            _PM: "A named project manager, a daily photo diary, and a written summary every Friday — none of which you have to ask for.",
            _ANX: "Homeowners aren't anxious about the money so much as about the silence. So we removed the silence.",
        },
    },
    "d4-threshold.html": {
        "firm": "Threshold Builders", "phone": "(555) 863-4417", "tel": "+15558634417",
        "h1": "We'll tell you when not to do it.",
        "copy": {
            _SUB: "Whole-home renovations, additions and structural work, typically from $75,000. The first visit is free and a fair share of them end with us saying the project isn't worth doing, or isn't worth doing yet.",
            _FEW: "We take fewer projects than we could and turn down ones we don't believe in. Running four properly beats running nine badly.",
            _PROP: "Drawings, engineering where needed, and a line-item proposal — issued only once we both think the project is worth building.",
        },
    },
    "d5-licence.html": {
        "firm": "Granby Construction", "phone": "(555) 517-8836", "tel": "+15555178836",
        "h1": "Licensed, bonded, permitted — and we'll show you all three.",
        "copy": {
            _SUB: "Whole-home renovations, additions and structural work, typically from $75,000. Licence number, bond, insurance certificates and every pulled permit are handed over at signing, not promised and then chased.",
            _PM: "A named project manager who pulls the permits in your name, schedules the inspections, and gives you the paperwork as it clears.",
            _ANX: "The part that frightens people is unpermitted work surfacing when they sell. That is exactly the part we document.",
        },
    },
    "d6-contract.html": {
        "firm": "Bexley Build Group", "phone": "(555) 604-2158", "tel": "+15556042158",
        "h1": "Read the contract before you meet the salesman.",
        "copy": {
            _SUB: "Whole-home renovations, additions and structural work, typically from $75,000. Our contract, payment schedule and change-order process are published here to be read at your kitchen table rather than produced at signing.",
            _PROP: "Drawings, engineering where needed, and a line-item proposal on our standard contract — the same one published on this page.",
            _FEW: "We run a small number of projects at a time and write it into the contract, so the schedule you sign is one we can actually keep.",
        },
    },
}
