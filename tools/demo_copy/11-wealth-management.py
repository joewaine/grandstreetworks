"""Wealth management — six fee-only firms. The fiduciary promise is shared; the proof isn't."""

SOURCE_FIRM = "Ardsley Wealth Partners"
SOURCE_PHONE = "(555) 169-5540"
SOURCE_TEL = "+15551695540"
FORBIDDEN = ["Ardsley", "169-5540", "1695540"]

_SUB = "Fee-only fiduciary advice for families and business owners. No commissions, no product sales, no third-party payments — our fee schedule is published on this page."
_SECOND = "A second opinion costs nothing and takes about an hour. Half the people who come for one go back to their existing adviser reassured, and that is a fine outcome."
_NEXTGEN = "We meet your adult children at no additional cost. Most families lose their adviser at inheritance; that is a failure of relationship, not returns."
_PLAIN = "Presented in full, in plain English, including what we think you're doing wrong. You take it away whether or not you engage us."
_GATHER = "We gather everything and analyse it properly — tax returns, statements, insurance, estate documents. Two to three weeks."

PAGES = {
    "d1-statement.html": {
        "firm": "Ferrier Wealth Partners", "phone": "(743) 384-2217", "tel": "+17433842217",
        "h1": "Our fee schedule is on this page. All of it.",
        "copy": {
            _SUB: "Fee-only fiduciary advice for families and business owners. The entire fee schedule is printed on this page — no commissions, no product sales, no third-party payments, and no number you have to book a meeting to hear.",
            _PLAIN: "Presented in full and in plain English, including the parts of your current arrangement we think are wrong. Yours to keep whether or not you engage us.",
        },
    },
    "d2-ledger.html": {
        "firm": "Copeland Fiduciary", "phone": "(854) 726-4408", "tel": "+18547264408",
        "h1": "Every dollar we are paid, and who paid it.",
        "copy": {
            _SUB: "Fee-only fiduciary advice for families and business owners. One page shows every dollar of revenue this firm receives and its source. All of it comes from clients; none of it from products.",
            _PLAIN: "Presented as a plain statement rather than a pitch, including what we think is wrong with your current arrangement. You keep it either way.",
        },
    },
    "d3-handover.html": {
        "firm": "Winslow Family Wealth", "phone": "(607) 519-6672", "tel": "+16075196672",
        "h1": "Your children should know us before they need us.",
        "copy": {
            _SUB: "Fee-only fiduciary advice for families and business owners, built to survive a generation. We meet your adult children years before anyone needs us to, at no additional fee.",
            _NEXTGEN: "We meet your adult children at no extra cost and keep meeting them. Most families change adviser within a year of inheriting, and it is almost never about performance.",
        },
    },
    "d4-conversations.html": {
        "firm": "Bracken & Lowe", "phone": "(928) 240-8853", "tel": "+19282408853",
        "h1": "Three conversations before anyone signs anything.",
        "copy": {
            _SUB: "Fee-only fiduciary advice for families and business owners. Three unhurried conversations before any paperwork exists: what you have, what you want it to do, and what we would actually change.",
            _SECOND: "The first conversation costs nothing and takes about an hour. A good share of people leave reassured about the adviser they already have, which is a fine outcome.",
        },
    },
    "d5-plain.html": {
        "firm": "Hartwell Wealth Advisors", "phone": "(540) 967-1134", "tel": "+15409671134",
        "h1": "No charts. No jargon. What you have and what it does.",
        "copy": {
            _SUB: "Fee-only fiduciary advice for families and business owners, written in English. If a document needs a glossary to be understood, it has failed before you have read it.",
            _PLAIN: "Written in plain English with no glossary and no charts that flatter us, including the parts we think you have got wrong. Yours to take away.",
        },
    },
    "d6-letterhead.html": {
        "firm": "Ostrander Wealth Counsel", "phone": "(681) 631-7790", "tel": "+16816317790",
        "h1": "Sixty-one families. Not sixty-two.",
        "copy": {
            _SUB: "Fee-only fiduciary advice for a deliberately small number of families and business owners. Sixty-one households today, and a waiting list rather than a bigger client roster.",
            _GATHER: "We gather everything and analyse it properly — tax returns, statements, insurance, estate documents — over two to three weeks. That pace is only possible because we take on few families.",
        },
    },
}
