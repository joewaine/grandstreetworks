"""Heating and cooling — six companies. The trade is the same; the promise isn't."""

SOURCE_FIRM = "Meridian Air"
SOURCE_PHONE = "(555) 026-7310"
SOURCE_TEL = "+15550267310"
FORBIDDEN = ["Meridian Air", "026-7310", "0267310"]

_SUB = "Repair, replacement and maintenance across the metro. Same-day emergency service, financing from $89 a month, and a written price before we start."
_PICKUP = "Call and someone picks up: nights, weekends, holidays. Same-day emergency slots held back every day for exactly this."
_WINDOW = "A human answers, day or night. We give you a window and we hit it or we tell you early."
_FLAT = "Flat pricing, approved before work starts. No hourly meter running while you watch."
_PLAN = "Two visits a year, priority scheduling, no overtime rates. Most breakdowns we attend were preventable at a tenth the cost."
_SIZE = "Right-sized with a proper load calculation, not a guess off the old unit's badge. Financing arranged before install day."
_REBATE = "There is serious money in federal credits and utility rebates right now. We handle the paperwork and it comes off your price."

PAGES = {
    "d1-dispatch.html": {
        "firm": "Ironwood Heating & Air", "phone": "(585) 348-2260", "tel": "+15853482260",
        "h1": "No heat tonight? We dispatch, we don't schedule.",
        "copy": {
            _SUB: "Repair, replacement and maintenance across the metro. Trucks are dispatched from the nearest yard rather than slotted into next week, and you get a written price before anyone opens a panel.",
            _WINDOW: "A person in our own office answers and dispatches the nearest truck. You get an arrival window in minutes, and a call if it slips.",
            _PICKUP: "Nights, weekends, holidays, the coldest evening of the year: someone picks up, and there are emergency slots held back every single day.",
        },
    },
    "d2-thermostat.html": {
        "firm": "Sutter Heating & Cooling", "phone": "(302) 712-9948", "tel": "+13027129948",
        "h1": "Half the calls we take aren't a broken system.",
        "copy": {
            _SUB: "Repair, replacement and maintenance across the metro. We diagnose before we quote, and a good share of what gets sold as a failed system turns out to be a thermostat, a filter or a blocked return.",
            _FLAT: "Flat pricing approved before work starts, and if the fix turns out to be twenty dollars of parts we charge you for twenty dollars of parts.",
            _PICKUP: "Someone picks up nights and weekends, and will happily walk you through two checks on the phone before dispatching anyone.",
        },
    },
    "d3-hotcold.html": {
        "firm": "Vantage Air Systems", "phone": "(225) 265-4471", "tel": "+12252654471",
        "h1": "One room freezing, one room baking. That's fixable.",
        "copy": {
            _SUB: "Repair, replacement and maintenance across the metro. Uneven rooms are usually ductwork and airflow rather than the unit, which is why replacing the unit so often fails to fix them.",
            _SIZE: "Right-sized against a proper load calculation and a duct survey, not a guess off the old badge, which is how houses end up with rooms nobody can live in.",
            _FLAT: "Flat pricing, approved before work starts, with the airflow readings shown to you before and after.",
        },
    },
    "d4-nightcall.html": {
        "firm": "Nightingale Heating & Air", "phone": "(878) 889-3305", "tel": "+18788893305",
        "h1": "Nights and weekends cost the same as Tuesday morning.",
        "copy": {
            _SUB: "Repair, replacement and maintenance across the metro. No overtime rate, no weekend premium and no holiday surcharge. A failure at nine on a Sunday is priced exactly as it would be at nine on a Tuesday.",
            _PICKUP: "Nights, weekends and holidays, answered by our own people, at the same price as any weekday call. That is the entire policy.",
            _FLAT: "Flat pricing approved before work starts, and the same flat price whatever the hour on the clock says.",
        },
    },
    "d5-plan.html": {
        "firm": "Beacon Comfort Co.", "phone": "(947) 403-6617", "tel": "+19474036617",
        "h1": "Most emergencies we attend were preventable in April.",
        "copy": {
            _SUB: "Repair, replacement and maintenance across the metro. Two visits a year catches the failures that otherwise arrive at their worst possible moment, at roughly a tenth of what the emergency costs.",
            _PLAN: "Two visits a year, priority when you do need us, and no overtime rates. Nearly every emergency we attend was visible six months earlier.",
            _REBATE: "There is real money in federal credits and utility rebates at the moment. We file the paperwork and it comes straight off your invoice.",
        },
    },
    "d6-certified.html": {
        "firm": "Trueline Heating & Air", "phone": "(662) 858-8823", "tel": "+16628588823",
        "h1": "Load-calculated, permitted, and commissioned properly.",
        "copy": {
            _SUB: "Repair, replacement and maintenance across the metro. Every replacement gets a Manual J load calculation, a pulled permit and a commissioning report: the three steps most quotes quietly skip.",
            _SIZE: "Sized by Manual J against your actual house, not the badge on the old unit. Oversizing is the most common fault we find and the most expensive to live with.",
            _REBATE: "Credits and rebates only pay out on properly documented installs. Ours are documented, so the paperwork goes through.",
        },
    },
}
