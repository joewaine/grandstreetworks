"""Accounting and CPA firms — six practices. Compliance is table stakes; the rhythm differs."""

SOURCE_FIRM = "Fenwick & Hale CPAs"
SOURCE_PHONE = "(555) 172-8845"
SOURCE_TEL = "+15551728845"
FORBIDDEN = ["Fenwick", "172-8845", "1728845"]

_SUB = "Business accounting, tax and advisory for owner-managed companies. Secure document intake, quarterly conversations rather than one annual scramble, and fixed monthly fees."
_MAY = "Then this is the right month to talk. Everything worth fixing has to be built between May and August — by January it's too late to change anything."
_SIZE = "We work with owner-managed businesses between roughly $500k and $20M in revenue. Below that we'll point you somewhere better suited."
_SWITCH = "We request records from your current accountant — you don't have to have that conversation. Usually two to three weeks."
_PERSONAL = "Included for owners of business clients. Your company and personal position are the same problem and should be looked at together."

PAGES = {
    "d1-intake.html": {
        "firm": "Brandt & Yoo CPAs", "phone": "(930) 471-3328", "tel": "+19304713328",
        "h1": "Stop emailing your tax documents as attachments.",
        "copy": {
            _SUB: "Business accounting, tax and advisory for owner-managed companies. Documents go into an encrypted portal with a checklist that tracks itself, so nobody is ever searching an inbox for a K-1 in March.",
            _SWITCH: "We request the records from your current accountant, through the portal, so you never have to make that phone call yourself.",
        },
    },
    "d2-ledger.html": {
        "firm": "Latimer Accounting", "phone": "(585) 806-2245", "tel": "+15858062245",
        "h1": "Books closed by the tenth. Every month.",
        "copy": {
            _SUB: "Business accounting, tax and advisory for owner-managed companies. Your books close by the tenth of the following month, so the numbers you are making decisions on are five weeks old at worst.",
            _MAY: "This is the right month to talk. Decisions taken on numbers from last quarter are guesses, however good the guesser is.",
        },
    },
    "d3-advisory.html": {
        "firm": "Corven CPA Group", "phone": "(402) 358-9917", "tel": "+14023589917",
        "h1": "Compliance is the floor, not the service.",
        "copy": {
            _SUB: "Business accounting, tax and advisory for owner-managed companies. Filing on time is the minimum anyone should expect. What you are actually paying for is entity structure, owner compensation and the planning that only works before December.",
            _PERSONAL: "Your personal return is included, because for an owner the company and the household are one problem wearing two hats.",
        },
    },
    "d4-checklist.html": {
        "firm": "Ashby & Kerr CPAs", "phone": "(269) 692-4471", "tel": "+12696924471",
        "h1": "You will always know what we're waiting on.",
        "copy": {
            _SUB: "Business accounting, tax and advisory for owner-managed companies. A live checklist shows exactly which documents are outstanding and who is holding each one — usually us, and we say so.",
            _SWITCH: "We request records from your current accountant and the checklist shows you where that request has got to. No chasing on your side.",
        },
    },
    "d5-rhythm.html": {
        "firm": "Rennick CPA", "phone": "(210) 217-5583", "tel": "+12102175583",
        "h1": "Four conversations a year, not one long panic.",
        "copy": {
            _SUB: "Business accounting, tax and advisory for owner-managed companies. Four scheduled conversations a year, booked in advance, so decisions get made in the months when they can still change the outcome.",
            _MAY: "May through August is when a tax position is actually built. By January we are all just reporting what already happened.",
        },
    },
    "d6-plain.html": {
        "firm": "Halstead Accounting", "phone": "(660) 940-3362", "tel": "+16609403362",
        "h1": "A fixed monthly fee, agreed before we start.",
        "copy": {
            _SUB: "Business accounting, tax and advisory for owner-managed companies. One fixed monthly fee agreed in advance and never billed by the six-minute unit, so ringing your accountant a question stops feeling expensive.",
            _SIZE: "We work with owner-managed businesses roughly between $500k and $20M in revenue. Below that the fixed fee stops being good value and we will say so.",
        },
    },
}
