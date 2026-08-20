"""Property management — six companies. Owner-facing throughout."""
SOURCE_FIRM = "Kestrel Property Group"
SOURCE_PHONE = "(555) 158-3390"
SOURCE_TEL = "+15551583390"
FORBIDDEN = ["Kestrel", "158-3390", "1583390"]
_SUB = "Full-service management for owners of one to two hundred doors. Eight percent, no leasing markup, no maintenance mark-up, and an owner portal where you can see everything without asking anyone."
_QUOTE = "Send us the addresses and we'll come back with what we'd charge and what we think the units should be renting for. No meeting required to get the number."
PAGES = {
    "d1-ownerstatement.html": {"firm": "Rowan Property Group", "phone": "(555) 314-6672", "tel": "+15553146672",
        "h1": "Eight rentals and tired of being the plumber's first call?",
        "copy": {_SUB: "Full-service management for owners of one to two hundred doors. Eight percent, no leasing fee, no mark-up on maintenance, and a statement each month that reconciles to the cent without you asking for it."}},
    "d2-doorcount.html": {"firm": "Amberton Residential", "phone": "(555) 782-4419", "tel": "+15557824419",
        "h1": "One door or two hundred. Same eight percent.",
        "copy": {_SUB: "Full-service management for owners of one to two hundred doors, at the same eight percent whether you own a single condo or a portfolio. Small owners usually get quoted worse; we could not defend why.",
                 _QUOTE: "Send the addresses and we will come back with the fee and what we think each unit should rent for. No meeting needed to get a number."}},
    "d3-sundaynight.html": {"firm": "Halcombe Management", "phone": "(555) 269-8837", "tel": "+15552698837",
        "h1": "The nine o'clock Sunday call comes to us now.",
        "copy": {_SUB: "Full-service management for owners of one to two hundred doors. The maintenance line is staffed around the clock by our own people, so the broken water heater on Sunday night is our evening rather than yours."}},
    "d4-portal.html": {"firm": "Weatherby Property Co.", "phone": "(555) 851-3364", "tel": "+15558513364",
        "h1": "Everything visible, without asking anyone for it.",
        "copy": {_SUB: "Full-service management for owners of one to two hundred doors. Statements, invoices, inspection photographs, lease documents and work orders are all in the portal the moment they exist — no request, no wait, no summary email.",
                 _QUOTE: "Send the addresses and the numbers come back by email. You should not need a meeting to find out what something costs."}},
    "d5-workorder.html": {"firm": "Ridgemont Property Services", "phone": "(555) 407-1128", "tel": "+15554071128",
        "h1": "No mark-up on maintenance. You see the invoice.",
        "copy": {_SUB: "Full-service management for owners of one to two hundred doors. Contractor invoices are passed through at cost with the original attached — the industry's quiet ten-to-twenty percent maintenance mark-up is where the real money usually hides."}},
    "d6-eightpercent.html": {"firm": "Colvert Property Group", "phone": "(555) 936-2245", "tel": "+15559362245",
        "h1": "Eight percent. That is the entire fee schedule.",
        "copy": {_SUB: "Full-service management for owners of one to two hundred doors. Eight percent of collected rent and nothing else — no leasing fee, no renewal fee, no set-up fee, no mark-up, no inspection charge.",
                 _QUOTE: "Send the addresses and we will confirm the eight percent and what we think they should be renting for. There is nothing else to quote."}},
}
