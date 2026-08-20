"""Recruiting — six firms."""
SOURCE_FIRM = "Ridgeway Search"
SOURCE_PHONE = "(555) 205-1160"
SOURCE_TEL = "+15552051160"
FORBIDDEN = ["Ridgeway", "205-1160", "2051160"]
_SUB = "We place engineers and operations leaders in manufacturing and industrial businesses. Every role we advertise carries a real salary band, and you can apply from your phone in under a minute."
_BOTH = "Either conversation is confidential and neither commits you to anything. Candidates: we'll tell you what you're worth right now even if you don't move."
PAGES = {
    "d1-rolelist.html": {"firm": "Halbrook Search", "phone": "(555) 372-8840", "tel": "+15553728840",
        "h1": "One sector. Every salary published. Apply in one tap.",
        "copy": {_SUB: "We place engineers and operations leaders in manufacturing and industrial businesses. Every advertised role carries its real band — not 'competitive' — and applying takes under a minute from a phone."}},
    "d2-switch.html": {"firm": "Ironvale Partners", "phone": "(555) 640-2273", "tel": "+15556402273",
        "h1": "Hiring, or being hired? Two different doors.",
        "copy": {_SUB: "We place engineers and operations leaders in manufacturing and industrial businesses. Employers and candidates want opposite things from a website, so we built both and let you choose.",
                 _BOTH: "Either conversation is confidential and commits you to nothing. Candidates: we will tell you your market number even when you decide to stay put."}},
    "d3-sector.html": {"firm": "Copperfield Industrial Search", "phone": "(555) 218-9964", "tel": "+15552189964",
        "h1": "We only do industrial. That's the whole point.",
        "copy": {_SUB: "Engineers and operations leaders in manufacturing and industrial businesses. One sector, worked for nineteen years, which is why we know who is unhappy at which plant before the role is even open."}},
    "d4-loud.html": {"firm": "Brandt Yates Recruitment", "phone": "(555) 803-4417", "tel": "+15558034417",
        "h1": "Four candidates. Not a stack of twelve.",
        "copy": {_SUB: "Engineers and operations leaders in manufacturing and industrial businesses. A mapped market and a shortlist of four people who will actually take the job — sending twelve is a way of transferring the work back to you."}},
    "d5-screening.html": {"firm": "Ellings Search Group", "phone": "(555) 456-1128", "tel": "+15554561128",
        "h1": "We turn down roles we can't fill honestly.",
        "copy": {_SUB: "Engineers and operations leaders in manufacturing and industrial businesses. We decline searches where the band is wrong or the role is undeliverable, which costs us fees and saves everybody four wasted months.",
                 _BOTH: "Both conversations are confidential. Candidates: we will tell you when a role is wrong for you even though saying so costs us the fee."}},
    "d6-onetap.html": {"firm": "Kirkwall Talent", "phone": "(555) 927-6650", "tel": "+15559276650",
        "h1": "Apply from the shop floor, on your phone, in a minute.",
        "copy": {_SUB: "Engineers and operations leaders in manufacturing and industrial businesses. No account, no cover letter, no fourteen-field form — the people we place are on a floor, not at a desk with a CV open."}},
}
