"""Copy deck for the six photographic personal-injury reference builds.

Every one of the 36 pages in cash_rich/static2 renders the same fictional firm
(Vance & Cole) with identical words, because they were six design experiments
on one prospect. Published side by side that reads as one site recoloured, so
each build gets its own firm, its own phone number and its own argument. The
structure — call-first hero, four practice areas, four figures, a review wall,
a four-step process — is deliberately held constant. That structure is the
product; the words are what makes six of them worth looking at.

Consumed by tools/build-photo-sets.py. Keys are the verbatim source strings.
"""

# Strings shared by all 36 source pages. A page's dict maps each to its
# replacement; anything omitted keeps the source wording on purpose.
PAGES = {
    "16203e61-d1": {
        "slug": "d1-blueprint",
        "name": "The Blueprint One",
        "why": "Fixes: phone number buried and no after-hours promise — the number is a fixed bar and the headline is the promise.",
        "accent": "#F2A57C",
        "axes": "Hero <b>ruled-grid</b> · Nav <b>bar</b> · Services <b>numbered</b> · Proof <b>stats</b> · Image <b>courthouse plate</b>",
        "firm": "Harlan & Vega",
        "initials": "HV",
        "phone": "(231) 204-8810",
        "tel": "+12312048810",
        "title": "Harlan & Vega — Injury and accident claims, answered day or night",
        "h1": ["Call at midnight.", "A lawyer picks up."],
        "copy": {
            "Injury and accident claims across the state. No fee unless we recover for you, and you speak to a lawyer in the first 24 hours — not a call centre, not a form.":
                "Injury and accident claims across the state. No fee unless we recover for you, and the first voice you hear is a lawyer's — not an intake service reading from a script.",
            "Free consultation": "Free case review",
            "Hablamos español": "Hablamos español",
            "Answering 24/7 · Se habla español": "Answered in person, 24/7 · Se habla español",
            "Call now — 24/7": "Call now — 24/7",
            "Start a free case review": "Start a free case review",
            "Home &amp; hospital visits": "Home &amp; hospital visits",
            "Cases we take": "Cases we take",
            "Car &amp; truck accidents": "Car &amp; truck accidents",
            "From rear-endings to commercial truck collisions. We handle the insurer, the medical liens and the property damage so you handle recovery.":
                "Rear-endings through to commercial truck collisions. We take the insurer, the medical liens and the property damage off your desk so you can get on with healing.",
            "Workplace injury": "Workplace injury",
            "Comp claims that were denied, third-party liability, construction site accidents. Often there is a claim beyond workers' comp.":
                "Denied comp claims, third-party liability, site accidents. There is very often a second claim beyond workers' comp, and it is usually the larger one.",
            "Slip, trip and premises": "Slip, trip and premises",
            "Property owners owe a duty of care. We move fast because the evidence — the wet floor, the broken step — disappears within days.":
                "Owners owe a duty of care. We move the same week, because the wet floor gets mopped and the broken step gets fixed long before anyone files anything.",
            "Wrongful death": "Wrongful death",
            "The hardest cases we take, and the ones we take most carefully. We deal with the process so your family doesn't have to.":
                "The hardest cases we take and the ones we take most slowly. We carry the process so that your family is not also managing paperwork.",
            "$48M+": "$61M+",
            "Recovered for clients": "Recovered for clients",
            "24hr": "1hr",
            "To speak with a lawyer": "Median callback, day or night",
            "98%": "94%",
            "Cases settled without trial": "Resolved without a trial",
            "Fee unless we win": "Fee unless we win",
            "\"I called four firms from the hospital. Three gave me voicemail. Vance &amp; Cole picked up at ten at night and had someone at my bedside the next morning.\"":
                "\"I called four firms from the hospital. Three gave me voicemail. Harlan &amp; Vega picked up at ten at night and had someone at my bedside before breakfast.\"",
            "— Ray M., Client, truck collision": "— Ray M., truck collision",
            "\"Answered on a Sunday. That alone told me everything.\"":
                "\"Answered on a Sunday. That alone told me everything.\"",
            "— Teresa L., Rear-end collision": "— Teresa L., rear-end collision",
            "\"They explained the lien situation in plain English. Nobody else had.\"":
                "\"They explained the lien situation in plain English. Nobody else had bothered.\"",
            "— Danny O., Workplace injury": "— Danny O., workplace injury",
            "\"Todo en español, desde la primera llamada.\"":
                "\"Todo en español, desde la primera llamada.\"",
            "— Rosa V., Auto accident": "— Rosa V., auto accident",
            "\"Settled for four times the first offer the insurer made me.\"":
                "\"Settled for four times what the insurer first offered.\"",
            "— Chris W., Premises liability": "— Chris W., premises liability",
            "What happens after you call": "What happens after you call",
            "Most people have never done this before and are frightened of the process more than the outcome.":
                "Most people have never done this before, and are more frightened of the process than of the outcome.",
            "You call, we listen": "You call, we listen",
            "Free, no obligation, and it takes about fifteen minutes. If we're not the right firm we'll tell you who is.":
                "Free, no obligation, about fifteen minutes. If we are not the right firm for it, we will tell you who is.",
            "We investigate": "We investigate",
            "Scene evidence, footage, witnesses and medical records — gathered fast, because most of it disappears within weeks.":
                "Scene evidence, footage, witnesses, medical records — gathered in days, because most of it is gone in weeks.",
            "We demand": "We demand",
            "A documented demand to the insurer. This is where most cases resolve, and where preparation shows up as money.":
                "A documented demand to the insurer. Most cases end here, and this is where preparation turns into money.",
            "We file if we must": "We file if we must",
            "If the offer is not serious, we file. We try cases, and insurers price that in.":
                "If the offer is not serious, we file. We try cases, and the insurers price that in.",
            "Injured in the last few days?": "Hurt in the last few days?",
            "Evidence disappears fast and insurers move first. One call, free, and you'll know within fifteen minutes whether you have a case. No fee unless we recover for you. Free consultations, home and hospital visits available.":
                "Evidence disappears fast and the insurer has already started. One free call and you will know inside fifteen minutes whether you have a case. No fee unless we recover for you; home and hospital visits available.",
        },
    },
}

PAGES.update({
    "35011531-d2": {
        "slug": "d2-broadside",
        "name": "The Broadside One",
        "why": "Fixes: no case results anywhere — the page is one enormous claim and the verdict board sits directly beneath it.",
        "accent": "#111111",
        "axes": "Hero <b>broadside</b> · Nav <b>minimal</b> · Services <b>list</b> · Proof <b>verdict board</b> · Image <b>skyline cutline</b>",
        "firm": "Okonkwo Trial Law",
        "initials": "OTL",
        "phone": "(743) 316-4020",
        "tel": "+17433164020",
        "title": "Okonkwo Trial Law — Injury cases tried, not just settled",
        "h1": ["Most firms settle.", "We try cases."],
        "copy": {
            "Injury and accident claims across the state. No fee unless we recover for you, and you speak to a lawyer in the first 24 hours — not a call centre, not a form.":
                "Injury and accident claims across the state. Ninety-odd per cent of these end in a settlement, and the size of that settlement depends entirely on whether the insurer believes you will go to trial. Ours know we will.",
            "Free consultation": "Free case review",
            "No fee unless we win": "No fee unless we win",
            "Hablamos español": "Hablamos español",
            "Answering 24/7 · Se habla español": "Trial counsel · Se habla español",
            "Call now — 24/7": "Talk to a trial lawyer",
            "Start a free case review": "See our verdicts",
            "Free case review": "Free case review",
            "Se habla español": "Se habla español",
            "Home &amp; hospital visits": "Home &amp; hospital visits",
            "Cases we take": "What we try",
            "Car &amp; truck accidents": "Catastrophic vehicle collisions",
            "From rear-endings to commercial truck collisions. We handle the insurer, the medical liens and the property damage so you handle recovery.":
                "Commercial trucking, multi-vehicle and wrongful-death collisions. The cases where the carrier's own lawyers arrive within hours and we need to be there first.",
            "Workplace injury": "Industrial and site injury",
            "Comp claims that were denied, third-party liability, construction site accidents. Often there is a claim beyond workers' comp.":
                "Scaffold and machinery cases against general contractors and equipment makers. Comp pays a fraction; the third-party claim is where the real recovery lives.",
            "Slip, trip and premises": "Premises and negligent security",
            "Property owners owe a duty of care. We move fast because the evidence — the wet floor, the broken step — disappears within days.":
                "Owners and managers who knew and did nothing. These turn on maintenance logs and prior complaints, and those only surface in discovery.",
            "Wrongful death": "Wrongful death",
            "The hardest cases we take, and the ones we take most carefully. We deal with the process so your family doesn't have to.":
                "Tried when they must be tried. Families are not asked to relive it in a deposition until we are certain the case needs it.",
            "$48M+": "$112M",
            "Recovered for clients": "Recovered at trial and in settlement",
            "24hr": "31",
            "To speak with a lawyer": "Jury verdicts returned",
            "98%": "9",
            "Cases settled without trial": "Lawyers, all of whom try cases",
            "0": "0",
            "Fee unless we win": "Fee unless we win",
            "\"I called four firms from the hospital. Three gave me voicemail. Vance &amp; Cole picked up at ten at night and had someone at my bedside the next morning.\"":
                "\"The insurer offered forty thousand and told me that was the ceiling. Okonkwo filed. Eleven months later a jury came back with just under two million.\"",
            "— Ray M., Client, truck collision": "— Ray M., commercial truck collision",
            "\"Answered on a Sunday. That alone told me everything.\"":
                "\"They showed me the verdict sheet from a case like mine on the first call.\"",
            "— Teresa L., Rear-end collision": "— Teresa L., rear-end collision",
            "\"They explained the lien situation in plain English. Nobody else had.\"":
                "\"Two other firms wanted to settle it in a fortnight. This one asked what happened.\"",
            "— Danny O., Workplace injury": "— Danny O., scaffold fall",
            "\"Todo en español, desde la primera llamada.\"":
                "\"Explicaron el juicio paso a paso, en español, sin prisa.\"",
            "— Rosa V., Auto accident": "— Rosa V., auto accident",
            "\"Settled for four times the first offer the insurer made me.\"":
                "\"They picked the jury on a Monday. The offer tripled on the Tuesday.\"",
            "— Chris W., Premises liability": "— Chris W., premises liability",
            "What happens after you call": "How a case gets tried",
            "Most people have never done this before and are frightened of the process more than the outcome.":
                "Almost everyone who calls us is frightened of a courtroom. Most never see one — but the preparation for it is what pays.",
            "You call, we listen": "The case review",
            "Free, no obligation, and it takes about fifteen minutes. If we're not the right firm we'll tell you who is.":
                "Free, unhurried, and honest about what your case is worth. If it belongs with a different firm we will say so on that call.",
            "We investigate": "Discovery",
            "Scene evidence, footage, witnesses and medical records — gathered fast, because most of it disappears within weeks.":
                "Depositions, maintenance records, black-box data, internal email. This is the stage that separates a nuisance offer from a real one.",
            "We demand": "The demand",
            "A documented demand to the insurer. This is where most cases resolve, and where preparation shows up as money.":
                "Everything discovery produced, put in front of the carrier with a number attached. Most cases end here — at a price set by what we found.",
            "We file if we must": "Trial",
            "If the offer is not serious, we file. We try cases, and insurers price that in.":
                "If the number is not serious, we pick a jury. Thirty-one times so far, which is precisely why the numbers usually are serious.",
            "Injured in the last few days?": "Been told what your case is worth?",
            "Evidence disappears fast and insurers move first. One call, free, and you'll know within fifteen minutes whether you have a case. No fee unless we recover for you. Free consultations, home and hospital visits available.":
                "Get a second read before you sign anything. Free, no obligation, and we will tell you honestly if the offer in front of you is already a fair one. No fee unless we recover for you.",
        },
    },
    "3cf68118-d2": {
        "slug": "d3-redline",
        "name": "The Redline One",
        "why": "Fixes: no urgency about evidence — the whole page is a clock, and the first block is what disappears this week.",
        "accent": "#D81E20",
        "axes": "Hero <b>split-red</b> · Nav <b>bar</b> · Services <b>cards</b> · Proof <b>review-wall</b> · Image <b>night city, red print</b>",
        "firm": "Brightmoor Injury Law",
        "initials": "BIL",
        "phone": "(564) 447-1180",
        "tel": "+15644471180",
        "title": "Brightmoor Injury Law — The evidence is gone in a week. Call today.",
        "h1": ["The evidence is gone", "in a week."],
        "copy": {
            "Injury and accident claims across the state. No fee unless we recover for you, and you speak to a lawyer in the first 24 hours — not a call centre, not a form.":
                "Injury and accident claims across the state. Camera footage is overwritten in days, skid marks wash away and witnesses forget. We start the same afternoon you call, and there is no fee unless we recover for you.",
            "Free consultation": "Same-day case review",
            "No fee unless we win": "No fee unless we win",
            "Hablamos español": "Hablamos español",
            "Answering 24/7 · Se habla español": "Investigators out today · Se habla español",
            "Call now — 24/7": "Call now — we start today",
            "Start a free case review": "Send us the details",
            "Free case review": "Free case review",
            "Home &amp; hospital visits": "Home &amp; hospital visits",
            "Cases we take": "What we take on",
            "Car &amp; truck accidents": "Vehicle collisions",
            "From rear-endings to commercial truck collisions. We handle the insurer, the medical liens and the property damage so you handle recovery.":
                "Cars, trucks, motorcycles, rideshare. We send a request to preserve footage before the carrier's own investigator is out of the office.",
            "Workplace injury": "Workplace injury",
            "Comp claims that were denied, third-party liability, construction site accidents. Often there is a claim beyond workers' comp.":
                "Site accidents, machinery, denied comp claims. Equipment gets repaired and logs get rewritten, so we ask for both in writing on day one.",
            "Slip, trip and premises": "Slip, trip and premises",
            "Property owners owe a duty of care. We move fast because the evidence — the wet floor, the broken step — disappears within days.":
                "The wet floor is mopped within the hour and the broken step is fixed by the weekend. Photographs taken today are frequently the entire case.",
            "Wrongful death": "Wrongful death",
            "The hardest cases we take, and the ones we take most carefully. We deal with the process so your family doesn't have to.":
                "We take the calls, the forms and the insurer, and we do not ask a family to make decisions in the first week unless the law forces it.",
            "$48M+": "$37M",
            "Recovered for clients": "Recovered for clients",
            "24hr": "6hr",
            "To speak with a lawyer": "Median time to a preservation letter",
            "98%": "72",
            "Cases settled without trial": "Hours in which most footage is overwritten",
            "Fee unless we win": "Fee unless we win",
            "\"I called four firms from the hospital. Three gave me voicemail. Vance &amp; Cole picked up at ten at night and had someone at my bedside the next morning.\"":
                "\"I called on the Thursday. Someone was at the junction photographing the lights on the Friday morning. The store's camera had already wiped it by Monday.\"",
            "— Ray M., Client, truck collision": "— Ray M., truck collision",
            "\"Answered on a Sunday. That alone told me everything.\"":
                "\"They had the footage before the shop's system deleted it. That was the case.\"",
            "— Teresa L., Rear-end collision": "— Teresa L., rear-end collision",
            "\"They explained the lien situation in plain English. Nobody else had.\"":
                "\"Told me exactly what to photograph while I was still in A&amp;E.\"",
            "— Danny O., Workplace injury": "— Danny O., workplace injury",
            "\"Todo en español, desde la primera llamada.\"":
                "\"Vinieron el mismo día. En español, sin intérprete.\"",
            "— Rosa V., Auto accident": "— Rosa V., auto accident",
            "\"Settled for four times the first offer the insurer made me.\"":
                "\"Four times the first offer, because they had the maintenance log and the insurer didn't know it.\"",
            "— Chris W., Premises liability": "— Chris W., premises liability",
            "What happens after you call": "The first seventy-two hours",
            "Most people have never done this before and are frightened of the process more than the outcome.":
                "Nearly everything that decides a case is decided in the first three days, usually before anyone has spoken to a lawyer.",
            "You call, we listen": "Hour one — you call",
            "Free, no obligation, and it takes about fifteen minutes. If we're not the right firm we'll tell you who is.":
                "Fifteen minutes, free, and we will tell you on that call what to photograph and what not to sign.",
            "We investigate": "Day one — we preserve",
            "Scene evidence, footage, witnesses and medical records — gathered fast, because most of it disappears within weeks.":
                "Letters out to everyone holding footage, logs or records, putting them on notice that destroying it now has consequences.",
            "We demand": "Week one — we gather",
            "A documented demand to the insurer. This is where most cases resolve, and where preparation shows up as money.":
                "Scene photographs, witnesses while they still remember, medical records, and the vehicle before it goes to the yard.",
            "We file if we must": "Then we demand",
            "If the offer is not serious, we file. We try cases, and insurers price that in.":
                "A documented demand built from what we preserved. If the answer is not serious, we file — and we have the file to do it.",
            "Injured in the last few days?": "Did it happen this week?",
            "Evidence disappears fast and insurers move first. One call, free, and you'll know within fifteen minutes whether you have a case. No fee unless we recover for you. Free consultations, home and hospital visits available.":
                "Then call today rather than tomorrow. Footage is the first thing to go and it goes on a timer. One free call, fifteen minutes, and you will know whether there is a case worth preserving. No fee unless we recover for you.",
        },
    },
})

# Strings that only some decks carry, or that a deck splits across two nodes.
EXTRA = {
    "16203e61-d1": {
        "If your situation isn't listed, ring anyway. We'll tell you honestly whether you have a case — and if you don't, we'll say so.":
            "If your situation isn't on this list, ring anyway. We will tell you honestly whether there is a case, and say so plainly when there isn't.",
        "Evidence disappears fast and insurers move first. One call, free, and you'll know within fifteen minutes whether you have a case.":
            "Evidence disappears fast and the insurer has already started. One free call and you will know inside fifteen minutes whether you have a case.",
        "No fee unless we recover for you. Free consultations, home and hospital visits available.":
            "No fee unless we recover for you. Home and hospital visits available across the state.",
    },
    "35011531-d2": {
        "If your situation isn't listed, ring anyway. We'll tell you honestly whether you have a case — and if you don't, we'll say so.":
            "If your situation isn't listed, ring anyway. We will tell you what it is worth and whether it needs a courtroom — including when the answer is no.",
        "Evidence disappears fast and insurers move first. One call, free, and you'll know within fifteen minutes whether you have a case.":
            "Get a second read before you sign anything. Free, no obligation, and we will tell you honestly if the offer in front of you is already fair.",
        "No fee unless we recover for you. Free consultations, home and hospital visits available.":
            "No fee unless we recover for you. Consultations at our office, your home, or the hospital.",
        "\"Somebody is always up here.\"": "\"The lights stay on the week before a trial.\"",
        "Fig. 1 — 02:14, from our floor": "Fig. 1 — 02:14, the week before trial",
        "V&amp;C / 24H": "OTL / TRIAL",
    },
    "3cf68118-d2": {
        "If your situation isn't listed, ring anyway. We'll tell you honestly whether you have a case — and if you don't, we'll say so.":
            "If your situation isn't listed, ring anyway — today rather than next week. We will tell you honestly whether there is anything left to preserve.",
        "Evidence disappears fast and insurers move first. One call, free, and you'll know within fifteen minutes whether you have a case.":
            "Footage goes on a timer and the carrier's investigator is already working. One free call, fifteen minutes, and you will know what is worth preserving.",
        "No fee unless we recover for you. Free consultations, home and hospital visits available.":
            "No fee unless we recover for you. We come to the hospital, the house or the site.",
        "Clients on the record": "Clients on the record",
        "Desk 01 —": "Desk 01 —",
        "22:47": "22:47",
    },
}
for _k, _v in EXTRA.items():
    PAGES[_k]["copy"].update(_v)

PAGES.update({
    "3f4ca354-d5": {
        "slug": "d4-protocol",
        "name": "The Protocol One",
        "why": "Fixes: English-only genericism and no workplace angle — the page is bilingual at the top and leads with the second claim comp never mentions.",
        "accent": "#F5C518",
        "axes": "Hero <b>hazard-band</b> · Nav <b>bar</b> · Services <b>list</b> · Proof <b>review-wall</b> · Image <b>night, full-bleed</b>",
        "firm": "Salcedo & Roth",
        "initials": "SR",
        "phone": "(715) 962-3315",
        "tel": "+17159623315",
        "title": "Salcedo & Roth — Workplace injury. Hay un segundo reclamo.",
        "h1": ["Hurt at work?", "There is usually", "a second claim."],
        "copy": {
            "Injury and accident claims across the state. No fee unless we recover for you, and you speak to a lawyer in the first 24 hours — not a call centre, not a form.":
                "Workplace and accident claims across the state. Comp pays your wages at a discount and closes the file. The claim against whoever actually caused it is separate, larger, and nobody at the comp office is going to mention it.",
            "Free consultation": "Consulta gratis",
            "No fee unless we win": "No fee unless we win",
            "Hablamos español": "Hablamos español",
            "Answering 24/7 · Se habla español": "Se habla español · Atendemos 24/7",
            "Call now — 24/7": "Llámenos — 24/7",
            "Start a free case review": "Start a free case review",
            "Free case review": "Free case review",
            "Se habla español": "Se habla español",
            "Home &amp; hospital visits": "Home &amp; hospital visits",
            "Cases we take": "Where the second claim hides",
            "If your situation isn't listed, ring anyway. We'll tell you honestly whether you have a case — and if you don't, we'll say so.":
                "Not sure whether yours is one of these? Ring anyway. Si prefiere, llame y hablamos en español — le decimos con franqueza si hay caso.",
            "Car &amp; truck accidents": "Injured driving for work",
            "From rear-endings to commercial truck collisions. We handle the insurer, the medical liens and the property damage so you handle recovery.":
                "If you were in a vehicle on the clock, there is a comp claim and there is a claim against the other driver. They are separate files and only one of them is capped.",
            "Workplace injury": "Site and machinery accidents",
            "Comp claims that were denied, third-party liability, construction site accidents. Often there is a claim beyond workers' comp.":
                "The general contractor, the equipment maker and the subcontractor are not your employer, which means comp's limits do not protect them from a claim.",
            "Slip, trip and premises": "Denied or closed comp claims",
            "Property owners owe a duty of care. We move fast because the evidence — the wet floor, the broken step — disappears within days.":
                "Denied, cut short, or closed while you were still in pain. Denials are appealable, and a denial is not the same as a decision.",
            "Wrongful death": "Wrongful death",
            "The hardest cases we take, and the ones we take most carefully. We deal with the process so your family doesn't have to.":
                "We handle the insurer, the employer and the paperwork in whichever language your family prefers, and we do not rush anybody through it.",
            "$48M+": "$44M",
            "Recovered for clients": "Recovered beyond comp",
            "24hr": "68%",
            "To speak with a lawyer": "Of our clients had a second claim nobody mentioned",
            "98%": "100%",
            "Cases settled without trial": "Of consultations available in Spanish",
            "Fee unless we win": "Fee unless we win",
            "\"I called four firms from the hospital. Three gave me voicemail. Vance &amp; Cole picked up at ten at night and had someone at my bedside the next morning.\"":
                "\"Comp gave me sixty per cent of my wages and said that was it. Salcedo &amp; Roth went after the scaffold company. That claim was eleven times the comp file.\"",
            "— Ray M., Client, truck collision": "— Ray M., scaffold collapse",
            "\"Answered on a Sunday. That alone told me everything.\"":
                "\"Nobody had told me I could claim against anyone other than my boss.\"",
            "— Teresa L., Rear-end collision": "— Teresa L., delivery driver",
            "\"They explained the lien situation in plain English. Nobody else had.\"":
                "\"They appealed the denial. It was overturned in nine weeks.\"",
            "— Danny O., Workplace injury": "— Danny O., denied comp claim",
            "\"Todo en español, desde la primera llamada.\"":
                "\"Todo en español, desde la primera llamada hasta el cheque.\"",
            "— Rosa V., Auto accident": "— Rosa V., accidente de trabajo",
            "\"Settled for four times the first offer the insurer made me.\"":
                "\"I thought comp was all there was. It was about a fifth of it.\"",
            "— Chris W., Premises liability": "— Chris W., machinery injury",
            "What happens after you call": "What happens after you call",
            "Most people have never done this before and are frightened of the process more than the outcome.":
                "Most people who call us are worried about their job, their status, or both. Neither is a reason a claim gets refused, and neither comes up in a call with us.",
            "You call, we listen": "You call, in either language",
            "Free, no obligation, and it takes about fifteen minutes. If we're not the right firm we'll tell you who is.":
                "Free, about fifteen minutes, in English or Spanish, with a lawyer rather than an interpreter reading from a form.",
            "We investigate": "We find the second claim",
            "Scene evidence, footage, witnesses and medical records — gathered fast, because most of it disappears within weeks.":
                "Who owned the equipment, who ran the site, who was contracted to inspect it. The answer is rarely your employer, and that is the point.",
            "We demand": "We demand",
            "A documented demand to the insurer. This is where most cases resolve, and where preparation shows up as money.":
                "A documented demand against every party that owed you a duty. Most cases resolve here, at a number set by how much we found.",
            "We file if we must": "We file if we must",
            "If the offer is not serious, we file. We try cases, and insurers price that in.":
                "If the offer is not serious, we file. Your employer is not the defendant and cannot be the one to punish you for it.",
            "Injured in the last few days?": "¿Se lastimó en el trabajo?",
            "Evidence disappears fast and insurers move first. One call, free, and you'll know within fifteen minutes whether you have a case.":
                "Llame y le decimos en quince minutos si hay un segundo reclamo. Free, in English or Spanish, and no obligation either way.",
            "No fee unless we recover for you. Free consultations, home and hospital visits available.":
                "No fee unless we recover for you. Visitas a domicilio y al hospital disponibles.",
        },
    },
    "aed21146-d3": {
        "slug": "d5-plainenglish",
        "name": "The Plain English One",
        "why": "Fixes: nobody explains the fee — the agreement is on the page in plain words, before any form.",
        "accent": "#5C7A63",
        "axes": "Hero <b>panel</b> · Nav <b>centered</b> · Services <b>cards</b> · Proof <b>testimonial-lead</b> · Image <b>desk, soft block</b>",
        "firm": "Merrow Injury Group",
        "initials": "MIG",
        "phone": "(316) 636-7744",
        "tel": "+13166367744",
        "title": "Merrow Injury Group — The fee agreement, in plain words, before you sign",
        "h1": ["No fee unless we win.", "In writing, before", "you sign anything."],
        "copy": {
            "Injury and accident claims across the state. No fee unless we recover for you, and you speak to a lawyer in the first 24 hours — not a call centre, not a form.":
                "Injury and accident claims across the state. One third if we settle it, forty per cent if we have to file, nothing at all if we recover nothing. Costs come out of the recovery, not out of your pocket, and it is all on one page.",
            "Free consultation": "Free consultation",
            "No fee unless we win": "One third — nothing if we lose",
            "Hablamos español": "Hablamos español",
            "Answering 24/7 · Se habla español": "Plain-English agreement · Se habla español",
            "Call now — 24/7": "Ask us what it costs",
            "Start a free case review": "Read the fee agreement",
            "Free case review": "Free case review",
            "Home &amp; hospital visits": "Home &amp; hospital visits",
            "Cases we take": "Cases we take",
            "If your situation isn't listed, ring anyway. We'll tell you honestly whether you have a case — and if you don't, we'll say so.":
                "If yours isn't listed, ring anyway. The consultation is free whether or not we take it on, and we will tell you plainly when there is no case.",
            "Car &amp; truck accidents": "Car &amp; truck accidents",
            "From rear-endings to commercial truck collisions. We handle the insurer, the medical liens and the property damage so you handle recovery.":
                "We deal with the adjuster, the hire car and the hospital lien. You get a written update every fortnight whether or not anything has moved.",
            "Workplace injury": "Workplace injury",
            "Comp claims that were denied, third-party liability, construction site accidents. Often there is a claim beyond workers' comp.":
                "Denied comp claims and third-party liability. We explain in advance which pot any money would come out of, and what comp will want back.",
            "Slip, trip and premises": "Slip, trip and premises",
            "Property owners owe a duty of care. We move fast because the evidence — the wet floor, the broken step — disappears within days.":
                "Owners owe a duty of care. We will tell you on the first call how strong that duty looks, rather than after you have signed.",
            "Wrongful death": "Wrongful death",
            "The hardest cases we take, and the ones we take most carefully. We deal with the process so your family doesn't have to.":
                "Handled slowly and explained twice, because families are asked to make decisions at the worst possible time and deserve to understand them.",
            "$48M+": "$29M",
            "Recovered for clients": "Recovered for clients",
            "24hr": "1/3",
            "To speak with a lawyer": "Our fee if the case settles",
            "98%": "14 days",
            "Cases settled without trial": "Between written updates, guaranteed",
            "Fee unless we win": "Fee if we recover nothing",
            "\"I called four firms from the hospital. Three gave me voicemail. Vance &amp; Cole picked up at ten at night and had someone at my bedside the next morning.\"":
                "\"Every firm said no fee unless we win. Merrow was the only one that showed me what came out of the settlement before the cheque, on the first call, on one page.\"",
            "— Ray M., Client, truck collision": "— Ray M., truck collision",
            "\"Answered on a Sunday. That alone told me everything.\"":
                "\"I knew what the fee was before I signed. That was new.\"",
            "— Teresa L., Rear-end collision": "— Teresa L., rear-end collision",
            "\"They explained the lien situation in plain English. Nobody else had.\"":
                "\"They explained the lien situation in plain English. Nobody else had.\"",
            "— Danny O., Workplace injury": "— Danny O., workplace injury",
            "\"Todo en español, desde la primera llamada.\"":
                "\"Me explicaron los honorarios en español, por escrito.\"",
            "— Rosa V., Auto accident": "— Rosa V., auto accident",
            "\"Settled for four times the first offer the insurer made me.\"":
                "\"An update every two weeks, even the weeks nothing happened.\"",
            "— Chris W., Premises liability": "— Chris W., premises liability",
            "What happens after you call": "What it costs, and when",
            "Most people have never done this before and are frightened of the process more than the outcome.":
                "The fee is the part people are most afraid to ask about, so we put it first instead of on page nine.",
            "You call, we listen": "The consultation is free",
            "Free, no obligation, and it takes about fifteen minutes. If we're not the right firm we'll tell you who is.":
                "Free whether or not we take the case, about fifteen minutes, with no pressure to sign anything on that call.",
            "We investigate": "One third if we settle",
            "Scene evidence, footage, witnesses and medical records — gathered fast, because most of it disappears within weeks.":
                "If the case resolves without filing suit, our fee is a third of the recovery. That number does not move once you have signed.",
            "We demand": "Forty per cent if we file",
            "A documented demand to the insurer. This is where most cases resolve, and where preparation shows up as money.":
                "Filing means depositions, experts and months of work, so the fee rises to forty per cent. We tell you before we file, not after.",
            "We file if we must": "Nothing if we recover nothing",
            "If the offer is not serious, we file. We try cases, and insurers price that in.":
                "If we recover nothing you owe us nothing — not the fee, and not the costs we advanced along the way.",
            "Injured in the last few days?": "Want to see the agreement first?",
            "Evidence disappears fast and insurers move first. One call, free, and you'll know within fifteen minutes whether you have a case.":
                "Ask and we will send it before you commit to anything. One page, plain English, no obligation to sign it.",
            "No fee unless we recover for you. Free consultations, home and hospital visits available.":
                "No fee unless we recover for you. Free consultations at our office, your home or the hospital.",
        },
    },
    "f5636758-d4": {
        "slug": "d6-firstoffer",
        "name": "The First Offer One",
        "why": "Fixes: no case results — the page is built around the gap between the opening offer and the final one.",
        "accent": "#C8A45C",
        "axes": "Hero <b>panel</b> · Nav <b>bar</b> · Services <b>tiles</b> · Proof <b>stats</b> · Image <b>gold-bordered plate</b>",
        "firm": "Prentice & Aldana",
        "initials": "P&A",
        "phone": "(458) 573-6690",
        "tel": "+14585736690",
        "title": "Prentice & Aldana — The first offer is never the last offer",
        "h1": ["The first offer", "is never", "the last offer."],
        "copy": {
            "Injury and accident claims across the state. No fee unless we recover for you, and you speak to a lawyer in the first 24 hours — not a call centre, not a form.":
                "Injury and accident claims across the state. The adjuster's opening number is an opening position, calculated on the assumption that you will take it. Almost nobody who calls a lawyer ends up settling for it.",
            "Free consultation": "Free offer review",
            "No fee unless we win": "No fee unless we win",
            "Hablamos español": "Hablamos español",
            "Answering 24/7 · Se habla español": "Reviewing offers daily · Se habla español",
            "Call now — 24/7": "Have your offer reviewed",
            "Start a free case review": "Start a free case review",
            "Free case review": "Free case review",
            "Home &amp; hospital visits": "Home &amp; hospital visits",
            "Cases we take": "Cases we take",
            "If your situation isn't listed, ring anyway. We'll tell you honestly whether you have a case — and if you don't, we'll say so.":
                "Already been offered something? Ring before you accept. Sometimes the offer on your table is genuinely fair, and we will be the ones to tell you so.",
            "Car &amp; truck accidents": "Car &amp; truck accidents",
            "From rear-endings to commercial truck collisions. We handle the insurer, the medical liens and the property damage so you handle recovery.":
                "Opening offers here tend to cover the vehicle and ignore the year of physiotherapy. We price the whole injury, including the part that has not happened yet.",
            "Workplace injury": "Workplace injury",
            "Comp claims that were denied, third-party liability, construction site accidents. Often there is a claim beyond workers' comp.":
                "Comp offers what the schedule says. Whether a third party owes you considerably more is a separate question that the schedule never asks.",
            "Slip, trip and premises": "Slip, trip and premises",
            "Property owners owe a duty of care. We move fast because the evidence — the wet floor, the broken step — disappears within days.":
                "Insurers open low on premises cases because they expect no lawyer. The maintenance record usually changes the arithmetic entirely.",
            "Wrongful death": "Wrongful death",
            "The hardest cases we take, and the ones we take most carefully. We deal with the process so your family doesn't have to.":
                "Never negotiated in the first weeks. Early offers in these cases are made precisely because a family is not in a position to weigh them.",
            "$48M+": "$52M",
            "Recovered for clients": "Recovered for clients",
            "24hr": "6.4x",
            "To speak with a lawyer": "Median final recovery against first offer",
            "98%": "91%",
            "Cases settled without trial": "Resolved without going to trial",
            "Fee unless we win": "Fee unless we win",
            "\"I called four firms from the hospital. Three gave me voicemail. Vance &amp; Cole picked up at ten at night and had someone at my bedside the next morning.\"":
                "\"The insurer's cheque was for nine thousand and the adjuster was very nice about it. Prentice &amp; Aldana closed it at eighty-two. I had a pen in my hand for the nine.\"",
            "— Ray M., Client, truck collision": "— Ray M., truck collision",
            "\"Answered on a Sunday. That alone told me everything.\"":
                "\"They told me the first offer was actually decent. Then they got me more anyway.\"",
            "— Teresa L., Rear-end collision": "— Teresa L., rear-end collision",
            "\"They explained the lien situation in plain English. Nobody else had.\"":
                "\"Nobody had counted the physio I would still be paying for next year.\"",
            "— Danny O., Workplace injury": "— Danny O., workplace injury",
            "\"Todo en español, desde la primera llamada.\"":
                "\"Revisaron la oferta en español antes de que yo firmara nada.\"",
            "— Rosa V., Auto accident": "— Rosa V., auto accident",
            "\"Settled for four times the first offer the insurer made me.\"":
                "\"Settled for four times the first offer the insurer made me.\"",
            "— Chris W., Premises liability": "— Chris W., premises liability",
            "What happens after you call": "How the number moves",
            "Most people have never done this before and are frightened of the process more than the outcome.":
                "An opening offer is a negotiating position dressed up as a valuation. Here is what actually moves it.",
            "You call, we listen": "We read the offer",
            "Free, no obligation, and it takes about fifteen minutes. If we're not the right firm we'll tell you who is.":
                "Free, fifteen minutes, and an honest read on whether the number in front of you is already fair. Sometimes it is.",
            "We investigate": "We price the whole injury",
            "Scene evidence, footage, witnesses and medical records — gathered fast, because most of it disappears within weeks.":
                "Future treatment, lost earnings, the work you can no longer do. Opening offers routinely count none of it.",
            "We demand": "We put it in writing",
            "A documented demand to the insurer. This is where most cases resolve, and where preparation shows up as money.":
                "A documented demand with every figure evidenced. This is the document that moves the number, and most cases end on it.",
            "We file if we must": "We file if we must",
            "If the offer is not serious, we file. We try cases, and insurers price that in.":
                "If the answer stays unserious we file, and the carrier reprices the file the moment it has a court date on it.",
            "Injured in the last few days?": "Been offered a settlement?",
            "Evidence disappears fast and insurers move first. One call, free, and you'll know within fifteen minutes whether you have a case.":
                "Have it read before you sign. Free, fifteen minutes, and we will say plainly if the offer is already a good one.",
            "No fee unless we recover for you. Free consultations, home and hospital visits available.":
                "No fee unless we recover for you. Free consultations, home and hospital visits available.",
        },
    },
})
