"""Veterinary — six practices. Warm throughout; the open door differs."""
SOURCE_FIRM = "Brightwater Animal Hospital"
SOURCE_PHONE = "(555) 062-4477"
SOURCE_TEL = "+15550624477"
FORBIDDEN = ["Brightwater", "062-4477", "0624477"]
_SUB = "Full-service small animal care with online booking, Saturday hours and prescription refills you can request without phoning. New puppy or kitten? Their first visit is on us."
_NEW = "We're accepting new patients and hold same-day slots for sick visits. Book online in about a minute, or call and we'll sort it."
PAGES = {
    "d1-yes.html": {"firm": "Willowbank Animal Hospital", "phone": "(555) 283-6614", "tel": "+15552836614",
        "h1": "Yes — we're taking new patients.",
        "copy": {_SUB: "Full-service small animal care with online booking, Saturday hours and refills you can request without phoning. We are open to new patients today, which is not true of most practices near here."}},
    "d2-frontdesk.html": {"firm": "Corner Oak Veterinary", "phone": "(555) 719-2240", "tel": "+15557192240",
        "h1": "Nobody should have to phone to order a refill.",
        "copy": {_SUB: "Full-service small animal care. Refills, records, reminders and booking all happen online, so the front desk is free for the people standing in front of it with a frightened animal."}},
    "d3-opensign.html": {"firm": "Marlow Veterinary Clinic", "phone": "(555) 462-8873", "tel": "+15554628873",
        "h1": "Sick this morning? We hold slots for exactly that.",
        "copy": {_SUB: "Full-service small animal care with online booking and Saturday hours. Same-day slots are held back every morning for animals that were fine yesterday and are not fine today.",
                 _NEW: "We are accepting new patients and we keep same-day sick slots open. Book online in a minute, or ring and we will find you something."}},
    "d4-afterhours.html": {"firm": "Hollis Animal Hospital", "phone": "(555) 850-3327", "tel": "+15558503327",
        "h1": "Where to go at 2am, and when it can wait until morning.",
        "copy": {_SUB: "Full-service small animal care with online booking and Saturday hours — and a plainly published answer for nights and weekends, including which emergency hospital to drive to and when you genuinely can wait.",
                 _NEW: "Accepting new patients, with same-day sick slots and an after-hours line that tells you where to go rather than leaving a beep."}},
    "d5-samefaces.html": {"firm": "Fernhill Veterinary", "phone": "(555) 375-9948", "tel": "+15553759948",
        "h1": "The same vet and the same nurse, every visit.",
        "copy": {_SUB: "Full-service small animal care with online booking and Saturday hours. You are booked with your vet by name — anxious animals do considerably better with faces they recognise, and so do their owners."}},
    "d6-frontdoor.html": {"firm": "Beckett Animal Care", "phone": "(555) 604-1163", "tel": "+15556041163",
        "h1": "Prices for the ordinary things, printed here.",
        "copy": {_SUB: "Full-service small animal care with online booking and Saturday hours. Exams, vaccines, dentals, spays and neuters have their prices printed on this page, because nobody should have to ring to find out what a check-up costs.",
                 _NEW: "Accepting new patients, same-day sick slots held daily, and the routine prices published so there is no surprise at the desk."}},
}
